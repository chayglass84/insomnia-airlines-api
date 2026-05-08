from __future__ import annotations

import copy
import uuid
from enum import Enum
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

app = FastAPI(
    title="Insomnia Airlines — Flights & Airports API",
    version="1.0.0",
    description="REST API for Insomnia Airlines: airports, routes, and scheduled flights.",
)

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


@app.exception_handler(HTTPException)
async def http_exc(request, exc):
    if isinstance(exc.detail, dict):
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"code": "ERROR", "message": str(exc.detail)})


@app.get("/", include_in_schema=False)
def root():
    return FileResponse("index.html")


# ── Enums ──────────────────────────────────────────────────────────────────────

class FlightStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    BOARDING   = "BOARDING"
    DEPARTED   = "DEPARTED"
    ARRIVED    = "ARRIVED"
    DELAYED    = "DELAYED"
    CANCELLED  = "CANCELLED"


# ── Pydantic models ────────────────────────────────────────────────────────────

class Airport(BaseModel):
    iataCode: str
    name: str
    city: str
    country: str
    timezone: str

class Route(BaseModel):
    id: str
    origin: str
    destination: str
    distanceNauticalMiles: Optional[int] = None
    blockTimeMinutes: int

class RouteInput(BaseModel):
    origin: str
    destination: str
    distanceNauticalMiles: Optional[int] = None
    blockTimeMinutes: int

class Flight(BaseModel):
    flightNumber: str
    departureDate: str
    routeId: str
    aircraftTailNumber: str
    scheduledDeparture: str
    scheduledArrival: str
    gate: Optional[str] = None
    status: FlightStatus

class FlightInput(BaseModel):
    flightNumber: str
    departureDate: str
    routeId: str
    aircraftTailNumber: str
    scheduledDeparture: str
    scheduledArrival: str
    gate: Optional[str] = None

class FlightPatch(BaseModel):
    scheduledDeparture: Optional[str] = None
    scheduledArrival: Optional[str] = None
    aircraftTailNumber: Optional[str] = None
    gate: Optional[str] = None
    status: Optional[FlightStatus] = None


# ── Seed data ──────────────────────────────────────────────────────────────────

AIRPORTS: dict = {a["iataCode"]: a for a in [
    {"iataCode": "YYZ", "name": "Toronto Pearson International Airport",           "city": "Toronto",         "country": "CA", "timezone": "America/Toronto"},
    {"iataCode": "YUL", "name": "Montréal–Trudeau International Airport",          "city": "Montréal",        "country": "CA", "timezone": "America/Toronto"},
    {"iataCode": "YVR", "name": "Vancouver International Airport",                 "city": "Vancouver",       "country": "CA", "timezone": "America/Vancouver"},
    {"iataCode": "SEA", "name": "Seattle-Tacoma International Airport",            "city": "Seattle",         "country": "US", "timezone": "America/Los_Angeles"},
    {"iataCode": "SFO", "name": "San Francisco International Airport",             "city": "San Francisco",   "country": "US", "timezone": "America/Los_Angeles"},
    {"iataCode": "ORD", "name": "O'Hare International Airport",                   "city": "Chicago",         "country": "US", "timezone": "America/Chicago"},
    {"iataCode": "IAH", "name": "George Bush Intercontinental Airport",            "city": "Houston",         "country": "US", "timezone": "America/Chicago"},
    {"iataCode": "IAD", "name": "Dulles International Airport",                    "city": "Washington",      "country": "US", "timezone": "America/New_York"},
    {"iataCode": "BOS", "name": "Logan International Airport",                     "city": "Boston",          "country": "US", "timezone": "America/New_York"},
    {"iataCode": "FLL", "name": "Fort Lauderdale-Hollywood International Airport", "city": "Fort Lauderdale", "country": "US", "timezone": "America/New_York"},
]}

ROUTES: dict = {r["id"]: r for r in [
    {"id": "3f2504e0-4f89-11d3-9a0c-0305e82c3301", "origin": "YYZ", "destination": "SFO", "distanceNauticalMiles": 1850, "blockTimeMinutes": 305},
    {"id": "4a3604f1-4f89-11d3-9a0c-0305e82c3302", "origin": "YYZ", "destination": "ORD", "distanceNauticalMiles":  360, "blockTimeMinutes":  90},
    {"id": "5b4714f2-4f89-11d3-9a0c-0305e82c3303", "origin": "YYZ", "destination": "IAD", "distanceNauticalMiles":  330, "blockTimeMinutes":  95},
    {"id": "6c5824f3-4f89-11d3-9a0c-0305e82c3304", "origin": "YYZ", "destination": "BOS", "distanceNauticalMiles":  290, "blockTimeMinutes":  80},
    {"id": "7d6934f4-4f89-11d3-9a0c-0305e82c3305", "origin": "YUL", "destination": "FLL", "distanceNauticalMiles": 1280, "blockTimeMinutes": 195},
    {"id": "8e7a44f5-4f89-11d3-9a0c-0305e82c3306", "origin": "YVR", "destination": "SEA", "distanceNauticalMiles":  125, "blockTimeMinutes":  45},
    {"id": "9f8b54f6-4f89-11d3-9a0c-0305e82c3307", "origin": "YVR", "destination": "ORD", "distanceNauticalMiles": 1605, "blockTimeMinutes": 245},
    {"id": "a09c64f7-4f89-11d3-9a0c-0305e82c3308", "origin": "SFO", "destination": "IAH", "distanceNauticalMiles": 1640, "blockTimeMinutes": 210},
    {"id": "b1ad74f8-4f89-11d3-9a0c-0305e82c3309", "origin": "ORD", "destination": "IAH", "distanceNauticalMiles":  925, "blockTimeMinutes": 130},
    {"id": "c2be84f9-4f89-11d3-9a0c-0305e82c3310", "origin": "BOS", "destination": "IAD", "distanceNauticalMiles":  400, "blockTimeMinutes":  75},
]}

# keyed by (flightNumber, departureDate)
FLIGHTS: dict = {(f["flightNumber"], f["departureDate"]): f for f in [
    {"flightNumber": "IA101",  "departureDate": "2026-05-08", "routeId": "3f2504e0-4f89-11d3-9a0c-0305e82c3301", "aircraftTailNumber": "C-FINS", "scheduledDeparture": "2026-05-08T13:00:00Z", "scheduledArrival": "2026-05-08T18:05:00Z", "gate": "D32", "status": "DEPARTED"},
    {"flightNumber": "IA204",  "departureDate": "2026-05-08", "routeId": "4a3604f1-4f89-11d3-9a0c-0305e82c3302", "aircraftTailNumber": "C-FZZA", "scheduledDeparture": "2026-05-08T14:30:00Z", "scheduledArrival": "2026-05-08T16:00:00Z", "gate": "B14", "status": "BOARDING"},
    {"flightNumber": "IA315",  "departureDate": "2026-05-08", "routeId": "5b4714f2-4f89-11d3-9a0c-0305e82c3303", "aircraftTailNumber": "C-GZZZ", "scheduledDeparture": "2026-05-08T15:00:00Z", "scheduledArrival": "2026-05-08T16:35:00Z", "gate": "C22", "status": "SCHEDULED"},
    {"flightNumber": "IA422",  "departureDate": "2026-05-08", "routeId": "6c5824f3-4f89-11d3-9a0c-0305e82c3304", "aircraftTailNumber": "C-FMNO", "scheduledDeparture": "2026-05-08T16:00:00Z", "scheduledArrival": "2026-05-08T17:20:00Z", "gate": "A05", "status": "SCHEDULED"},
    {"flightNumber": "IA530",  "departureDate": "2026-05-08", "routeId": "7d6934f4-4f89-11d3-9a0c-0305e82c3305", "aircraftTailNumber": "C-GPQR", "scheduledDeparture": "2026-05-08T11:00:00Z", "scheduledArrival": "2026-05-08T14:15:00Z", "gate": "F18", "status": "ARRIVED"},
    {"flightNumber": "IA611",  "departureDate": "2026-05-08", "routeId": "8e7a44f5-4f89-11d3-9a0c-0305e82c3306", "aircraftTailNumber": "C-FSTU", "scheduledDeparture": "2026-05-08T22:00:00Z", "scheduledArrival": "2026-05-08T22:45:00Z", "gate": "G01", "status": "SCHEDULED"},
    {"flightNumber": "IA718",  "departureDate": "2026-05-08", "routeId": "9f8b54f6-4f89-11d3-9a0c-0305e82c3307", "aircraftTailNumber": "C-FVWX", "scheduledDeparture": "2026-05-08T10:00:00Z", "scheduledArrival": "2026-05-08T14:05:00Z", "gate": "H12", "status": "ARRIVED"},
    {"flightNumber": "IA825",  "departureDate": "2026-05-08", "routeId": "a09c64f7-4f89-11d3-9a0c-0305e82c3308", "aircraftTailNumber": "C-FYZA", "scheduledDeparture": "2026-05-08T20:30:00Z", "scheduledArrival": "2026-05-09T00:00:00Z", "gate": "T44", "status": "DELAYED"},
    {"flightNumber": "IA933",  "departureDate": "2026-05-09", "routeId": "3f2504e0-4f89-11d3-9a0c-0305e82c3301", "aircraftTailNumber": "C-FINS", "scheduledDeparture": "2026-05-09T13:00:00Z", "scheduledArrival": "2026-05-09T18:05:00Z", "gate": "D32", "status": "SCHEDULED"},
    {"flightNumber": "IA1042", "departureDate": "2026-05-09", "routeId": "b1ad74f8-4f89-11d3-9a0c-0305e82c3309", "aircraftTailNumber": "C-FBCD", "scheduledDeparture": "2026-05-09T17:00:00Z", "scheduledArrival": "2026-05-09T19:10:00Z", "gate": "K07", "status": "SCHEDULED"},
]}


# ── Airports ───────────────────────────────────────────────────────────────────

@app.get("/airports", response_model=list[Airport], tags=["airports"])
def list_airports(country: Optional[str] = None, limit: int = Query(50, ge=1, le=100)):
    results = list(AIRPORTS.values())
    if country:
        results = [a for a in results if a["country"] == country]
    return results[:limit]


@app.post("/airports", response_model=Airport, status_code=201, tags=["airports"])
def create_airport(body: Airport):
    if body.iataCode in AIRPORTS:
        raise HTTPException(409, {"code": "AIRPORT_EXISTS", "message": f"Airport '{body.iataCode}' already exists."})
    AIRPORTS[body.iataCode] = body.model_dump()
    return AIRPORTS[body.iataCode]


@app.get("/airports/{iataCode}", response_model=Airport, tags=["airports"])
def get_airport(iataCode: str):
    if iataCode not in AIRPORTS:
        raise HTTPException(404, {"code": "AIRPORT_NOT_FOUND", "message": f"No airport with IATA code '{iataCode}'."})
    return AIRPORTS[iataCode]


@app.put("/airports/{iataCode}", response_model=Airport, tags=["airports"])
def update_airport(iataCode: str, body: Airport):
    if iataCode not in AIRPORTS:
        raise HTTPException(404, {"code": "AIRPORT_NOT_FOUND", "message": f"No airport with IATA code '{iataCode}'."})
    AIRPORTS[iataCode] = {**body.model_dump(), "iataCode": iataCode}
    return AIRPORTS[iataCode]


@app.delete("/airports/{iataCode}", status_code=204, tags=["airports"])
def delete_airport(iataCode: str):
    if iataCode not in AIRPORTS:
        raise HTTPException(404, {"code": "AIRPORT_NOT_FOUND", "message": f"No airport with IATA code '{iataCode}'."})
    if any(r["origin"] == iataCode or r["destination"] == iataCode for r in ROUTES.values()):
        raise HTTPException(409, {"code": "AIRPORT_IN_USE", "message": f"Airport '{iataCode}' is referenced by active routes."})
    del AIRPORTS[iataCode]


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/routes", response_model=list[Route], tags=["routes"])
def list_routes(origin: Optional[str] = None, destination: Optional[str] = None):
    results = list(ROUTES.values())
    if origin:
        results = [r for r in results if r["origin"] == origin]
    if destination:
        results = [r for r in results if r["destination"] == destination]
    return results


@app.post("/routes", response_model=Route, status_code=201, tags=["routes"])
def create_route(body: RouteInput):
    if body.origin == body.destination:
        raise HTTPException(400, {"code": "SAME_ORIGIN_DESTINATION", "message": "Origin and destination must differ."})
    if body.origin not in AIRPORTS:
        raise HTTPException(400, {"code": "UNKNOWN_AIRPORT", "message": f"Unknown airport '{body.origin}'."})
    if body.destination not in AIRPORTS:
        raise HTTPException(400, {"code": "UNKNOWN_AIRPORT", "message": f"Unknown airport '{body.destination}'."})
    if any(r["origin"] == body.origin and r["destination"] == body.destination for r in ROUTES.values()):
        raise HTTPException(409, {"code": "ROUTE_EXISTS", "message": "Route already exists for that origin–destination pair."})
    route = {"id": str(uuid.uuid4()), **body.model_dump()}
    ROUTES[route["id"]] = route
    return route


@app.get("/routes/{routeId}", response_model=Route, tags=["routes"])
def get_route(routeId: str):
    if routeId not in ROUTES:
        raise HTTPException(404, {"code": "ROUTE_NOT_FOUND", "message": f"No route with ID '{routeId}'."})
    return ROUTES[routeId]


@app.delete("/routes/{routeId}", status_code=204, tags=["routes"])
def delete_route(routeId: str):
    if routeId not in ROUTES:
        raise HTTPException(404, {"code": "ROUTE_NOT_FOUND", "message": f"No route with ID '{routeId}'."})
    future_statuses = {"SCHEDULED", "BOARDING", "DELAYED"}
    if any(f["routeId"] == routeId and f["status"] in future_statuses for f in FLIGHTS.values()):
        raise HTTPException(409, {"code": "ROUTE_IN_USE", "message": "Route is referenced by future flights."})
    del ROUTES[routeId]


# ── Flights ────────────────────────────────────────────────────────────────────

@app.get("/flights", response_model=list[Flight], tags=["flights"])
def list_flights(
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    departureDate: Optional[str] = None,
    status: Optional[FlightStatus] = None,
    limit: int = Query(50, ge=1, le=200),
):
    results = list(FLIGHTS.values())
    if origin or destination:
        matching_routes = {
            r["id"] for r in ROUTES.values()
            if (not origin or r["origin"] == origin)
            and (not destination or r["destination"] == destination)
        }
        results = [f for f in results if f["routeId"] in matching_routes]
    if departureDate:
        results = [f for f in results if f["departureDate"] == departureDate]
    if status:
        results = [f for f in results if f["status"] == status.value]
    return results[:limit]


@app.post("/flights", response_model=Flight, status_code=201, tags=["flights"])
def schedule_flight(body: FlightInput):
    key = (body.flightNumber, body.departureDate)
    if key in FLIGHTS:
        raise HTTPException(409, {"code": "FLIGHT_EXISTS", "message": "Flight number already in use for that departure date."})
    if body.routeId not in ROUTES:
        raise HTTPException(400, {"code": "UNKNOWN_ROUTE", "message": f"Unknown route '{body.routeId}'."})
    flight = {**body.model_dump(), "status": "SCHEDULED"}
    FLIGHTS[key] = flight
    return flight


@app.get("/flights/{flightNumber}", response_model=Flight, tags=["flights"])
def get_flight(flightNumber: str, departureDate: str = Query(..., description="ISO 8601 date, e.g. 2026-05-08")):
    key = (flightNumber, departureDate)
    if key not in FLIGHTS:
        raise HTTPException(404, {"code": "FLIGHT_NOT_FOUND", "message": f"No flight '{flightNumber}' on {departureDate}."})
    return FLIGHTS[key]


@app.patch("/flights/{flightNumber}", response_model=Flight, tags=["flights"])
def patch_flight(flightNumber: str, body: FlightPatch, departureDate: str = Query(..., description="ISO 8601 date, e.g. 2026-05-08")):
    key = (flightNumber, departureDate)
    if key not in FLIGHTS:
        raise HTTPException(404, {"code": "FLIGHT_NOT_FOUND", "message": f"No flight '{flightNumber}' on {departureDate}."})
    flight = copy.copy(FLIGHTS[key])
    for field, value in body.model_dump(exclude_none=True).items():
        flight[field] = value.value if isinstance(value, Enum) else value
    FLIGHTS[key] = flight
    return flight


@app.delete("/flights/{flightNumber}", status_code=204, tags=["flights"])
def cancel_flight(flightNumber: str, departureDate: str = Query(..., description="ISO 8601 date, e.g. 2026-05-08")):
    key = (flightNumber, departureDate)
    if key not in FLIGHTS:
        raise HTTPException(404, {"code": "FLIGHT_NOT_FOUND", "message": f"No flight '{flightNumber}' on {departureDate}."})
    FLIGHTS[key]["status"] = "CANCELLED"
