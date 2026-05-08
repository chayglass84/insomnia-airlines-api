from __future__ import annotations

import copy
import random
import string
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

app = FastAPI(
    title="Insomnia Airlines API",
    version="1.0.0",
    description="Flights, bookings, and baggage for Insomnia Airlines.",
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

class BookingStatus(str, Enum):
    HELD       = "HELD"
    CONFIRMED  = "CONFIRMED"
    CHECKED_IN = "CHECKED_IN"
    FLOWN      = "FLOWN"
    CANCELLED  = "CANCELLED"

class TravelClass(str, Enum):
    ECONOMY         = "ECONOMY"
    PREMIUM_ECONOMY = "PREMIUM_ECONOMY"
    BUSINESS        = "BUSINESS"
    FIRST           = "FIRST"

class FrequentFlyerTier(str, Enum):
    STANDARD = "STANDARD"
    SILVER   = "SILVER"
    GOLD     = "GOLD"
    PLATINUM = "PLATINUM"

class BagStatus(str, Enum):
    CHECKED_IN = "CHECKED_IN"
    IN_TRANSIT = "IN_TRANSIT"
    LOADED     = "LOADED"
    ARRIVED    = "ARRIVED"
    CLAIMED    = "CLAIMED"
    DELAYED    = "DELAYED"
    LOST       = "LOST"
    DAMAGED    = "DAMAGED"

class BagEventType(str, Enum):
    CHECK_IN       = "CHECK_IN"
    SECURITY_CLEAR = "SECURITY_CLEAR"
    LOAD           = "LOAD"
    UNLOAD         = "UNLOAD"
    TRANSFER       = "TRANSFER"
    CLAIM          = "CLAIM"
    FLAG_DELAYED   = "FLAG_DELAYED"
    FLAG_LOST      = "FLAG_LOST"
    FLAG_DAMAGED   = "FLAG_DAMAGED"

class LostBaggageCaseStatus(str, Enum):
    OPEN      = "OPEN"
    SEARCHING = "SEARCHING"
    LOCATED   = "LOCATED"
    DELIVERED = "DELIVERED"
    CLOSED    = "CLOSED"


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

class Money(BaseModel):
    amount: float
    currency: str

class FlightSegment(BaseModel):
    segmentIndex: int
    flightNumber: str
    departureDate: str
    origin: str
    destination: str
    scheduledDeparture: Optional[str] = None
    travelClass: TravelClass

class FlightSegmentInput(BaseModel):
    flightNumber: str
    departureDate: str
    travelClass: TravelClass

class Passenger(BaseModel):
    id: str
    firstName: str
    lastName: str
    email: Optional[str] = None
    phone: Optional[str] = None
    frequentFlyerId: Optional[str] = None
    dateOfBirth: Optional[str] = None

class PassengerInput(BaseModel):
    firstName: str
    lastName: str
    email: Optional[str] = None
    phone: Optional[str] = None
    frequentFlyerId: Optional[str] = None
    dateOfBirth: Optional[str] = None

class SeatAssignment(BaseModel):
    id: str
    passengerId: str
    segmentIndex: int
    seatNumber: str

class SeatAssignmentInput(BaseModel):
    passengerId: str
    segmentIndex: int
    seatNumber: str

class SeatAssignmentPatch(BaseModel):
    seatNumber: Optional[str] = None

class Booking(BaseModel):
    pnr: str
    status: BookingStatus
    contactEmail: Optional[str] = None
    passengers: list[Passenger]
    segments: list[FlightSegment]
    totalFare: Money
    createdAt: str

class BookingInput(BaseModel):
    contactEmail: Optional[str] = None
    passengers: list[PassengerInput]
    segments: list[FlightSegmentInput]

class BookingPatch(BaseModel):
    status: Optional[BookingStatus] = None
    contactEmail: Optional[str] = None

class FrequentFlyer(BaseModel):
    frequentFlyerId: str
    firstName: str
    lastName: str
    email: Optional[str] = None
    tier: FrequentFlyerTier
    milesBalance: int
    memberSince: Optional[str] = None

class Bag(BaseModel):
    bagTag: str
    pnr: str
    passengerId: str
    weightKg: float
    status: BagStatus
    currentLocation: Optional[str] = None
    assignedFlightNumber: Optional[str] = None
    assignedDepartureDate: Optional[str] = None
    checkedInAt: str

class BagInput(BaseModel):
    pnr: str
    passengerId: str
    weightKg: float
    assignedFlightNumber: Optional[str] = None
    assignedDepartureDate: Optional[str] = None

class BagPatch(BaseModel):
    weightKg: Optional[float] = None
    assignedFlightNumber: Optional[str] = None
    assignedDepartureDate: Optional[str] = None
    status: Optional[BagStatus] = None

class BagEvent(BaseModel):
    id: str
    bagTag: str
    type: BagEventType
    location: str
    flightNumber: Optional[str] = None
    occurredAt: str
    notes: Optional[str] = None

class BagEventInput(BaseModel):
    type: BagEventType
    location: str
    flightNumber: Optional[str] = None
    occurredAt: Optional[str] = None
    notes: Optional[str] = None

class LostBaggageCase(BaseModel):
    caseId: str
    pnr: str
    bagTag: Optional[str] = None
    reportedAtAirport: Optional[str] = None
    description: Optional[str] = None
    status: LostBaggageCaseStatus
    openedAt: str
    notes: Optional[str] = None

class LostBaggageCaseInput(BaseModel):
    pnr: str
    bagTag: Optional[str] = None
    reportedAtAirport: str
    description: str

class LostBaggageCasePatch(BaseModel):
    bagTag: Optional[str] = None
    status: Optional[LostBaggageCaseStatus] = None
    notes: Optional[str] = None


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

FREQUENT_FLYERS: dict = {
    "FF1029384": {"frequentFlyerId": "FF1029384", "firstName": "Alex",  "lastName": "Morgan", "email": "alex.morgan@example.com",  "tier": "GOLD",   "milesBalance": 48230, "memberSince": "2019-08-04"},
    "FF2938475": {"frequentFlyerId": "FF2938475", "firstName": "Sam",   "lastName": "Taylor", "email": "sam.taylor@example.com",   "tier": "SILVER", "milesBalance": 12500, "memberSince": "2022-03-15"},
}

# keyed by PNR; passengers and segments are stored inline
BOOKINGS: dict = {
    "AB12CD": {
        "pnr": "AB12CD", "status": "CONFIRMED", "contactEmail": "alex.morgan@example.com",
        "passengers": [
            {"id": "a1000001-0000-0000-0000-000000000000", "firstName": "Alex",   "lastName": "Morgan", "email": "alex.morgan@example.com", "frequentFlyerId": "FF1029384", "dateOfBirth": "1988-04-12"},
            {"id": "a1000002-0000-0000-0000-000000000000", "firstName": "Sam",    "lastName": "Taylor", "email": "sam.taylor@example.com",  "frequentFlyerId": "FF2938475"},
        ],
        "segments": [
            {"segmentIndex": 0, "flightNumber": "IA204", "departureDate": "2026-05-08", "origin": "YYZ", "destination": "ORD", "scheduledDeparture": "2026-05-08T14:30:00Z", "travelClass": "ECONOMY"},
        ],
        "totalFare": {"amount": 842.50, "currency": "USD"}, "createdAt": "2026-04-30T19:14:02Z",
    },
    "EF34GH": {
        "pnr": "EF34GH", "status": "CONFIRMED", "contactEmail": "jordan.lee@example.com",
        "passengers": [
            {"id": "a1000003-0000-0000-0000-000000000000", "firstName": "Jordan", "lastName": "Lee",    "email": "jordan.lee@example.com"},
        ],
        "segments": [
            {"segmentIndex": 0, "flightNumber": "IA101", "departureDate": "2026-05-08", "origin": "YYZ", "destination": "SFO", "scheduledDeparture": "2026-05-08T13:00:00Z", "travelClass": "BUSINESS"},
        ],
        "totalFare": {"amount": 2100.00, "currency": "USD"}, "createdAt": "2026-05-01T08:30:00Z",
    },
    "IJ56KL": {
        "pnr": "IJ56KL", "status": "HELD", "contactEmail": "maria.santos@example.com",
        "passengers": [
            {"id": "a1000004-0000-0000-0000-000000000000", "firstName": "Maria",  "lastName": "Santos", "email": "maria.santos@example.com"},
        ],
        "segments": [
            {"segmentIndex": 0, "flightNumber": "IA933", "departureDate": "2026-05-09", "origin": "YYZ", "destination": "SFO", "scheduledDeparture": "2026-05-09T13:00:00Z", "travelClass": "ECONOMY"},
        ],
        "totalFare": {"amount": 689.00, "currency": "USD"}, "createdAt": "2026-05-05T14:00:00Z",
    },
    "MN78OP": {
        "pnr": "MN78OP", "status": "FLOWN", "contactEmail": "david.chen@example.com",
        "passengers": [
            {"id": "a1000005-0000-0000-0000-000000000000", "firstName": "David",  "lastName": "Chen",   "email": "david.chen@example.com"},
        ],
        "segments": [
            {"segmentIndex": 0, "flightNumber": "IA530", "departureDate": "2026-05-08", "origin": "YUL", "destination": "FLL", "scheduledDeparture": "2026-05-08T11:00:00Z", "travelClass": "ECONOMY"},
        ],
        "totalFare": {"amount": 421.00, "currency": "USD"}, "createdAt": "2026-04-25T10:00:00Z",
    },
    "QR90ST": {
        "pnr": "QR90ST", "status": "CANCELLED", "contactEmail": "lisa.park@example.com",
        "passengers": [
            {"id": "a1000006-0000-0000-0000-000000000000", "firstName": "Lisa",   "lastName": "Park",   "email": "lisa.park@example.com"},
        ],
        "segments": [
            {"segmentIndex": 0, "flightNumber": "IA315", "departureDate": "2026-05-08", "origin": "YYZ", "destination": "IAD", "scheduledDeparture": "2026-05-08T15:00:00Z", "travelClass": "PREMIUM_ECONOMY"},
        ],
        "totalFare": {"amount": 1100.00, "currency": "USD"}, "createdAt": "2026-04-28T16:00:00Z",
    },
}

# keyed by assignment UUID; includes pnr for filtering
SEAT_ASSIGNMENTS: dict = {
    "s1000001-0000-0000-0000-000000000000": {"id": "s1000001-0000-0000-0000-000000000000", "pnr": "AB12CD", "passengerId": "a1000001-0000-0000-0000-000000000000", "segmentIndex": 0, "seatNumber": "14C"},
    "s1000002-0000-0000-0000-000000000000": {"id": "s1000002-0000-0000-0000-000000000000", "pnr": "AB12CD", "passengerId": "a1000002-0000-0000-0000-000000000000", "segmentIndex": 0, "seatNumber": "14D"},
    "s1000003-0000-0000-0000-000000000000": {"id": "s1000003-0000-0000-0000-000000000000", "pnr": "EF34GH", "passengerId": "a1000003-0000-0000-0000-000000000000", "segmentIndex": 0, "seatNumber": "3A"},
}

# keyed by bagTag
BAGS: dict = {
    "0074123456": {"bagTag": "0074123456", "pnr": "AB12CD", "passengerId": "a1000001-0000-0000-0000-000000000000", "weightKg": 18.4, "status": "LOADED",     "currentLocation": "YYZ", "assignedFlightNumber": "IA204", "assignedDepartureDate": "2026-05-08", "checkedInAt": "2026-05-08T11:42:18Z"},
    "0074123457": {"bagTag": "0074123457", "pnr": "AB12CD", "passengerId": "a1000002-0000-0000-0000-000000000000", "weightKg": 22.1, "status": "LOADED",     "currentLocation": "YYZ", "assignedFlightNumber": "IA204", "assignedDepartureDate": "2026-05-08", "checkedInAt": "2026-05-08T11:50:00Z"},
    "0074234567": {"bagTag": "0074234567", "pnr": "EF34GH", "passengerId": "a1000003-0000-0000-0000-000000000000", "weightKg": 15.0, "status": "LOADED",     "currentLocation": "YYZ", "assignedFlightNumber": "IA101", "assignedDepartureDate": "2026-05-08", "checkedInAt": "2026-05-08T10:15:00Z"},
    "0074345678": {"bagTag": "0074345678", "pnr": "MN78OP", "passengerId": "a1000005-0000-0000-0000-000000000000", "weightKg":  8.5, "status": "CLAIMED",    "currentLocation": "FLL", "checkedInAt": "2026-05-08T08:00:00Z"},
    "0074456789": {"bagTag": "0074456789", "pnr": "IJ56KL", "passengerId": "a1000004-0000-0000-0000-000000000000", "weightKg": 20.0, "status": "CHECKED_IN", "currentLocation": "YYZ", "assignedFlightNumber": "IA933", "assignedDepartureDate": "2026-05-09", "checkedInAt": "2026-05-08T17:00:00Z"},
    "0074567890": {"bagTag": "0074567890", "pnr": "QR90ST", "passengerId": "a1000006-0000-0000-0000-000000000000", "weightKg": 12.0, "status": "LOST",       "currentLocation": "ORD", "checkedInAt": "2026-05-06T14:30:00Z"},
}

# keyed by bagTag; each value is a list of events
BAG_EVENTS: dict = {
    "0074123456": [
        {"id": "e1000001-0000-0000-0000-000000000000", "bagTag": "0074123456", "type": "CHECK_IN",       "location": "YYZ",                             "occurredAt": "2026-05-08T11:42:18Z"},
        {"id": "e1000002-0000-0000-0000-000000000000", "bagTag": "0074123456", "type": "SECURITY_CLEAR", "location": "YYZ",                             "occurredAt": "2026-05-08T12:10:00Z"},
        {"id": "e1000003-0000-0000-0000-000000000000", "bagTag": "0074123456", "type": "LOAD",           "location": "YYZ", "flightNumber": "IA204",    "occurredAt": "2026-05-08T13:50:00Z", "notes": "Loaded into forward cargo hold."},
    ],
    "0074123457": [
        {"id": "e1000004-0000-0000-0000-000000000000", "bagTag": "0074123457", "type": "CHECK_IN",       "location": "YYZ",                             "occurredAt": "2026-05-08T11:50:00Z"},
        {"id": "e1000005-0000-0000-0000-000000000000", "bagTag": "0074123457", "type": "SECURITY_CLEAR", "location": "YYZ",                             "occurredAt": "2026-05-08T12:15:00Z"},
        {"id": "e1000006-0000-0000-0000-000000000000", "bagTag": "0074123457", "type": "LOAD",           "location": "YYZ", "flightNumber": "IA204",    "occurredAt": "2026-05-08T13:52:00Z"},
    ],
    "0074234567": [
        {"id": "e1000007-0000-0000-0000-000000000000", "bagTag": "0074234567", "type": "CHECK_IN",       "location": "YYZ",                             "occurredAt": "2026-05-08T10:15:00Z"},
        {"id": "e1000008-0000-0000-0000-000000000000", "bagTag": "0074234567", "type": "LOAD",           "location": "YYZ", "flightNumber": "IA101",    "occurredAt": "2026-05-08T11:45:00Z"},
    ],
    "0074345678": [
        {"id": "e1000009-0000-0000-0000-000000000000", "bagTag": "0074345678", "type": "CHECK_IN",       "location": "YUL",                             "occurredAt": "2026-05-08T08:00:00Z"},
        {"id": "e1000010-0000-0000-0000-000000000000", "bagTag": "0074345678", "type": "LOAD",           "location": "YUL", "flightNumber": "IA530",    "occurredAt": "2026-05-08T09:45:00Z"},
        {"id": "e1000011-0000-0000-0000-000000000000", "bagTag": "0074345678", "type": "UNLOAD",         "location": "FLL",                             "occurredAt": "2026-05-08T14:30:00Z"},
        {"id": "e1000012-0000-0000-0000-000000000000", "bagTag": "0074345678", "type": "CLAIM",          "location": "FLL",                             "occurredAt": "2026-05-08T15:05:00Z"},
    ],
    "0074456789": [
        {"id": "e1000013-0000-0000-0000-000000000000", "bagTag": "0074456789", "type": "CHECK_IN",       "location": "YYZ",                             "occurredAt": "2026-05-08T17:00:00Z"},
    ],
    "0074567890": [
        {"id": "e1000014-0000-0000-0000-000000000000", "bagTag": "0074567890", "type": "CHECK_IN",       "location": "YYZ",                             "occurredAt": "2026-05-06T14:30:00Z"},
        {"id": "e1000015-0000-0000-0000-000000000000", "bagTag": "0074567890", "type": "LOAD",           "location": "YYZ", "flightNumber": "IA718",    "occurredAt": "2026-05-06T15:45:00Z"},
        {"id": "e1000016-0000-0000-0000-000000000000", "bagTag": "0074567890", "type": "FLAG_LOST",      "location": "ORD",                             "occurredAt": "2026-05-06T18:30:00Z", "notes": "Not found in cargo hold after IA718 arrived."},
    ],
}

# keyed by caseId UUID
LOST_BAGGAGE_CASES: dict = {
    "c1000001-0000-0000-0000-000000000000": {
        "caseId": "c1000001-0000-0000-0000-000000000000", "pnr": "QR90ST", "bagTag": "0074567890",
        "reportedAtAirport": "ORD", "description": "Black hardshell roller, red ribbon on handle.",
        "status": "SEARCHING", "openedAt": "2026-05-06T18:45:00Z",
        "notes": "Passenger confirms checked in at YYZ on IA718. Last scanned ORD.",
    },
    "c1000002-0000-0000-0000-000000000000": {
        "caseId": "c1000002-0000-0000-0000-000000000000", "pnr": "MN78OP",
        "reportedAtAirport": "FLL", "description": "Blue duffel bag with airline tag sticker.",
        "status": "OPEN", "openedAt": "2026-05-08T15:30:00Z",
    },
}


# ── Helpers ────────────────────────────────────────────────────────────────────

def _new_pnr() -> str:
    chars = string.ascii_uppercase + string.digits
    while True:
        pnr = "".join(random.choices(chars, k=6))
        if pnr not in BOOKINGS:
            return pnr

def _new_bag_tag() -> str:
    while True:
        tag = "".join(random.choices(string.digits, k=10))
        if tag not in BAGS:
            return tag

# Maps a BagEventType to the resulting BagStatus (None = no change)
_EVENT_STATUS: dict = {
    "CHECK_IN":       "CHECKED_IN",
    "SECURITY_CLEAR": None,
    "LOAD":           "LOADED",
    "UNLOAD":         "IN_TRANSIT",
    "TRANSFER":       "IN_TRANSIT",
    "CLAIM":          "CLAIMED",
    "FLAG_DELAYED":   "DELAYED",
    "FLAG_LOST":      "LOST",
    "FLAG_DAMAGED":   "DAMAGED",
}


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


# ── Bookings ───────────────────────────────────────────────────────────────────

@app.get("/bookings", response_model=list[Booking], tags=["bookings"])
def list_bookings(
    status: Optional[BookingStatus] = None,
    frequentFlyerId: Optional[str] = None,
    flightNumber: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
):
    results = list(BOOKINGS.values())
    if status:
        results = [b for b in results if b["status"] == status.value]
    if frequentFlyerId:
        results = [b for b in results if any(p.get("frequentFlyerId") == frequentFlyerId for p in b["passengers"])]
    if flightNumber:
        results = [b for b in results if any(s["flightNumber"] == flightNumber for s in b["segments"])]
    return results[:limit]

@app.post("/bookings", response_model=Booking, status_code=201, tags=["bookings"])
def create_booking(body: BookingInput):
    if not body.passengers:
        raise HTTPException(400, {"code": "NO_PASSENGERS", "message": "At least one passenger is required."})
    if not body.segments:
        raise HTTPException(400, {"code": "NO_SEGMENTS", "message": "At least one flight segment is required."})
    ff_ids = [p.frequentFlyerId for p in body.passengers if p.frequentFlyerId]
    if len(ff_ids) != len(set(ff_ids)):
        raise HTTPException(409, {"code": "DUPLICATE_FREQUENT_FLYER", "message": "Duplicate frequent flyer on the same booking."})
    segments = []
    for i, seg_in in enumerate(body.segments):
        key = (seg_in.flightNumber, seg_in.departureDate)
        if key not in FLIGHTS:
            raise HTTPException(400, {"code": "UNKNOWN_FLIGHT", "message": f"No flight '{seg_in.flightNumber}' on {seg_in.departureDate}."})
        flight = FLIGHTS[key]
        route = ROUTES.get(flight["routeId"], {})
        segments.append({
            "segmentIndex": i,
            "flightNumber": seg_in.flightNumber,
            "departureDate": seg_in.departureDate,
            "origin": route.get("origin", ""),
            "destination": route.get("destination", ""),
            "scheduledDeparture": flight.get("scheduledDeparture"),
            "travelClass": seg_in.travelClass.value,
        })
    passengers = [
        {**p.model_dump(exclude_none=True), "id": str(uuid.uuid4())}
        for p in body.passengers
    ]
    pnr = _new_pnr()
    booking = {
        "pnr": pnr,
        "status": "HELD",
        "contactEmail": body.contactEmail,
        "passengers": passengers,
        "segments": segments,
        "totalFare": {"amount": 500.00, "currency": "USD"},
        "createdAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    BOOKINGS[pnr] = booking
    return booking

@app.get("/bookings/{pnr}", response_model=Booking, tags=["bookings"])
def get_booking(pnr: str):
    if pnr not in BOOKINGS:
        raise HTTPException(404, {"code": "BOOKING_NOT_FOUND", "message": f"No booking with PNR '{pnr}'."})
    return BOOKINGS[pnr]

@app.patch("/bookings/{pnr}", response_model=Booking, tags=["bookings"])
def patch_booking(pnr: str, body: BookingPatch):
    if pnr not in BOOKINGS:
        raise HTTPException(404, {"code": "BOOKING_NOT_FOUND", "message": f"No booking with PNR '{pnr}'."})
    booking = copy.copy(BOOKINGS[pnr])
    for field, value in body.model_dump(exclude_none=True).items():
        booking[field] = value.value if isinstance(value, Enum) else value
    BOOKINGS[pnr] = booking
    return booking

@app.delete("/bookings/{pnr}", status_code=204, tags=["bookings"])
def cancel_booking(pnr: str):
    if pnr not in BOOKINGS:
        raise HTTPException(404, {"code": "BOOKING_NOT_FOUND", "message": f"No booking with PNR '{pnr}'."})
    BOOKINGS[pnr]["status"] = "CANCELLED"


# ── Passengers ─────────────────────────────────────────────────────────────────

@app.get("/bookings/{pnr}/passengers", response_model=list[Passenger], tags=["passengers"])
def list_passengers(pnr: str):
    if pnr not in BOOKINGS:
        raise HTTPException(404, {"code": "BOOKING_NOT_FOUND", "message": f"No booking with PNR '{pnr}'."})
    return BOOKINGS[pnr]["passengers"]

@app.post("/bookings/{pnr}/passengers", response_model=Passenger, status_code=201, tags=["passengers"])
def add_passenger(pnr: str, body: PassengerInput):
    if pnr not in BOOKINGS:
        raise HTTPException(404, {"code": "BOOKING_NOT_FOUND", "message": f"No booking with PNR '{pnr}'."})
    if body.frequentFlyerId:
        if any(p.get("frequentFlyerId") == body.frequentFlyerId for p in BOOKINGS[pnr]["passengers"]):
            raise HTTPException(409, {"code": "PASSENGER_EXISTS", "message": "Passenger is already on this booking."})
    passenger = {**body.model_dump(exclude_none=True), "id": str(uuid.uuid4())}
    BOOKINGS[pnr]["passengers"].append(passenger)
    return passenger

@app.get("/bookings/{pnr}/passengers/{passengerId}", response_model=Passenger, tags=["passengers"])
def get_passenger(pnr: str, passengerId: str):
    if pnr not in BOOKINGS:
        raise HTTPException(404, {"code": "BOOKING_NOT_FOUND", "message": f"No booking with PNR '{pnr}'."})
    for p in BOOKINGS[pnr]["passengers"]:
        if p["id"] == passengerId:
            return p
    raise HTTPException(404, {"code": "PASSENGER_NOT_FOUND", "message": f"No passenger '{passengerId}' on booking '{pnr}'."})

@app.delete("/bookings/{pnr}/passengers/{passengerId}", status_code=204, tags=["passengers"])
def remove_passenger(pnr: str, passengerId: str):
    if pnr not in BOOKINGS:
        raise HTTPException(404, {"code": "BOOKING_NOT_FOUND", "message": f"No booking with PNR '{pnr}'."})
    passengers = BOOKINGS[pnr]["passengers"]
    if not any(p["id"] == passengerId for p in passengers):
        raise HTTPException(404, {"code": "PASSENGER_NOT_FOUND", "message": f"No passenger '{passengerId}' on booking '{pnr}'."})
    if len(passengers) == 1:
        raise HTTPException(409, {"code": "LAST_PASSENGER", "message": "Cannot remove the last passenger — cancel the booking instead."})
    BOOKINGS[pnr]["passengers"] = [p for p in passengers if p["id"] != passengerId]
    # remove any seat assignments for this passenger on this booking
    for sid in list(SEAT_ASSIGNMENTS):
        sa = SEAT_ASSIGNMENTS[sid]
        if sa["pnr"] == pnr and sa["passengerId"] == passengerId:
            del SEAT_ASSIGNMENTS[sid]

@app.get("/passengers/{frequentFlyerId}", response_model=FrequentFlyer, tags=["passengers"])
def get_frequent_flyer(frequentFlyerId: str):
    if frequentFlyerId not in FREQUENT_FLYERS:
        raise HTTPException(404, {"code": "FREQUENT_FLYER_NOT_FOUND", "message": f"No frequent flyer '{frequentFlyerId}'."})
    return FREQUENT_FLYERS[frequentFlyerId]

@app.get("/passengers/{frequentFlyerId}/bookings", response_model=list[Booking], tags=["passengers"])
def list_frequent_flyer_bookings(frequentFlyerId: str, status: Optional[BookingStatus] = None):
    if frequentFlyerId not in FREQUENT_FLYERS:
        raise HTTPException(404, {"code": "FREQUENT_FLYER_NOT_FOUND", "message": f"No frequent flyer '{frequentFlyerId}'."})
    results = [
        b for b in BOOKINGS.values()
        if any(p.get("frequentFlyerId") == frequentFlyerId for p in b["passengers"])
    ]
    if status:
        results = [b for b in results if b["status"] == status.value]
    return results


# ── Seats ──────────────────────────────────────────────────────────────────────

@app.get("/bookings/{pnr}/seats", response_model=list[SeatAssignment], tags=["seats"])
def list_seats(pnr: str):
    if pnr not in BOOKINGS:
        raise HTTPException(404, {"code": "BOOKING_NOT_FOUND", "message": f"No booking with PNR '{pnr}'."})
    return [sa for sa in SEAT_ASSIGNMENTS.values() if sa["pnr"] == pnr]

@app.post("/bookings/{pnr}/seats", response_model=SeatAssignment, status_code=201, tags=["seats"])
def assign_seat(pnr: str, body: SeatAssignmentInput):
    if pnr not in BOOKINGS:
        raise HTTPException(404, {"code": "BOOKING_NOT_FOUND", "message": f"No booking with PNR '{pnr}'."})
    booking = BOOKINGS[pnr]
    if not any(p["id"] == body.passengerId for p in booking["passengers"]):
        raise HTTPException(400, {"code": "UNKNOWN_PASSENGER", "message": f"Passenger '{body.passengerId}' is not on this booking."})
    if body.segmentIndex >= len(booking["segments"]):
        raise HTTPException(400, {"code": "INVALID_SEGMENT", "message": f"Segment index {body.segmentIndex} is out of range."})
    for sa in SEAT_ASSIGNMENTS.values():
        if sa["pnr"] == pnr and sa["segmentIndex"] == body.segmentIndex and sa["seatNumber"] == body.seatNumber:
            raise HTTPException(409, {"code": "SEAT_TAKEN", "message": f"Seat {body.seatNumber} is already assigned on segment {body.segmentIndex}."})
    assignment = {"id": str(uuid.uuid4()), "pnr": pnr, **body.model_dump()}
    SEAT_ASSIGNMENTS[assignment["id"]] = assignment
    return assignment

@app.patch("/bookings/{pnr}/seats/{seatAssignmentId}", response_model=SeatAssignment, tags=["seats"])
def change_seat(pnr: str, seatAssignmentId: str, body: SeatAssignmentPatch):
    if pnr not in BOOKINGS:
        raise HTTPException(404, {"code": "BOOKING_NOT_FOUND", "message": f"No booking with PNR '{pnr}'."})
    if seatAssignmentId not in SEAT_ASSIGNMENTS or SEAT_ASSIGNMENTS[seatAssignmentId]["pnr"] != pnr:
        raise HTTPException(404, {"code": "SEAT_ASSIGNMENT_NOT_FOUND", "message": f"No seat assignment '{seatAssignmentId}' on booking '{pnr}'."})
    if body.seatNumber:
        sa = SEAT_ASSIGNMENTS[seatAssignmentId]
        for other in SEAT_ASSIGNMENTS.values():
            if (other["id"] != seatAssignmentId and other["pnr"] == pnr
                    and other["segmentIndex"] == sa["segmentIndex"] and other["seatNumber"] == body.seatNumber):
                raise HTTPException(409, {"code": "SEAT_TAKEN", "message": f"Seat {body.seatNumber} is already assigned on that segment."})
        SEAT_ASSIGNMENTS[seatAssignmentId]["seatNumber"] = body.seatNumber
    return SEAT_ASSIGNMENTS[seatAssignmentId]

@app.delete("/bookings/{pnr}/seats/{seatAssignmentId}", status_code=204, tags=["seats"])
def release_seat(pnr: str, seatAssignmentId: str):
    if pnr not in BOOKINGS:
        raise HTTPException(404, {"code": "BOOKING_NOT_FOUND", "message": f"No booking with PNR '{pnr}'."})
    if seatAssignmentId not in SEAT_ASSIGNMENTS or SEAT_ASSIGNMENTS[seatAssignmentId]["pnr"] != pnr:
        raise HTTPException(404, {"code": "SEAT_ASSIGNMENT_NOT_FOUND", "message": f"No seat assignment '{seatAssignmentId}' on booking '{pnr}'."})
    del SEAT_ASSIGNMENTS[seatAssignmentId]


# ── Bags ───────────────────────────────────────────────────────────────────────

@app.get("/bags", response_model=list[Bag], tags=["bags"])
def list_bags(
    pnr: Optional[str] = None,
    flightNumber: Optional[str] = None,
    status: Optional[BagStatus] = None,
    limit: int = Query(50, ge=1, le=200),
):
    results = list(BAGS.values())
    if pnr:
        results = [b for b in results if b["pnr"] == pnr]
    if flightNumber:
        results = [b for b in results if b.get("assignedFlightNumber") == flightNumber]
    if status:
        results = [b for b in results if b["status"] == status.value]
    return results[:limit]

@app.post("/bags", response_model=Bag, status_code=201, tags=["bags"])
def check_in_bag(body: BagInput):
    if body.pnr not in BOOKINGS:
        raise HTTPException(400, {"code": "UNKNOWN_BOOKING", "message": f"No booking with PNR '{body.pnr}'."})
    if not any(p["id"] == body.passengerId for p in BOOKINGS[body.pnr]["passengers"]):
        raise HTTPException(400, {"code": "UNKNOWN_PASSENGER", "message": f"Passenger '{body.passengerId}' is not on booking '{body.pnr}'."})
    tag = _new_bag_tag()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    bag = {
        "bagTag": tag, "pnr": body.pnr, "passengerId": body.passengerId,
        "weightKg": body.weightKg, "status": "CHECKED_IN",
        "currentLocation": None,
        "assignedFlightNumber": body.assignedFlightNumber,
        "assignedDepartureDate": body.assignedDepartureDate,
        "checkedInAt": now,
    }
    BAGS[tag] = bag
    BAG_EVENTS[tag] = [{"id": str(uuid.uuid4()), "bagTag": tag, "type": "CHECK_IN", "location": "UNKNOWN", "occurredAt": now}]
    return bag

@app.get("/bags/{bagTag}", response_model=Bag, tags=["bags"])
def get_bag(bagTag: str):
    if bagTag not in BAGS:
        raise HTTPException(404, {"code": "BAG_NOT_FOUND", "message": f"No bag with tag '{bagTag}'."})
    return BAGS[bagTag]

@app.patch("/bags/{bagTag}", response_model=Bag, tags=["bags"])
def patch_bag(bagTag: str, body: BagPatch):
    if bagTag not in BAGS:
        raise HTTPException(404, {"code": "BAG_NOT_FOUND", "message": f"No bag with tag '{bagTag}'."})
    bag = copy.copy(BAGS[bagTag])
    for field, value in body.model_dump(exclude_none=True).items():
        bag[field] = value.value if isinstance(value, Enum) else value
    BAGS[bagTag] = bag
    return bag

@app.delete("/bags/{bagTag}", status_code=204, tags=["bags"])
def delete_bag(bagTag: str):
    if bagTag not in BAGS:
        raise HTTPException(404, {"code": "BAG_NOT_FOUND", "message": f"No bag with tag '{bagTag}'."})
    events = BAG_EVENTS.get(bagTag, [])
    if any(e["type"] != "CHECK_IN" for e in events):
        raise HTTPException(409, {"code": "BAG_HAS_HISTORY", "message": "Bag already has tracking history and cannot be deleted."})
    del BAGS[bagTag]
    BAG_EVENTS.pop(bagTag, None)


# ── Tracking ───────────────────────────────────────────────────────────────────

@app.get("/bags/{bagTag}/events", response_model=list[BagEvent], tags=["tracking"])
def list_bag_events(bagTag: str):
    if bagTag not in BAGS:
        raise HTTPException(404, {"code": "BAG_NOT_FOUND", "message": f"No bag with tag '{bagTag}'."})
    return BAG_EVENTS.get(bagTag, [])

@app.post("/bags/{bagTag}/events", response_model=BagEvent, status_code=201, tags=["tracking"])
def record_bag_event(bagTag: str, body: BagEventInput):
    if bagTag not in BAGS:
        raise HTTPException(404, {"code": "BAG_NOT_FOUND", "message": f"No bag with tag '{bagTag}'."})
    occurred_at = body.occurredAt or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    event = {
        "id": str(uuid.uuid4()), "bagTag": bagTag,
        "type": body.type.value, "location": body.location,
        "flightNumber": body.flightNumber, "occurredAt": occurred_at,
        "notes": body.notes,
    }
    BAG_EVENTS.setdefault(bagTag, []).append(event)
    new_status = _EVENT_STATUS.get(body.type.value)
    if new_status:
        BAGS[bagTag]["status"] = new_status
    BAGS[bagTag]["currentLocation"] = body.location
    return event

@app.get("/bookings/{pnr}/bags", response_model=list[Bag], tags=["bags"])
def list_booking_bags(pnr: str):
    if pnr not in BOOKINGS:
        raise HTTPException(404, {"code": "BOOKING_NOT_FOUND", "message": f"No booking with PNR '{pnr}'."})
    return [b for b in BAGS.values() if b["pnr"] == pnr]

@app.get("/flights/{flightNumber}/bags", response_model=list[Bag], tags=["bags"])
def list_flight_bags(flightNumber: str, departureDate: str = Query(..., description="ISO 8601 date, e.g. 2026-05-08")):
    if (flightNumber, departureDate) not in FLIGHTS:
        raise HTTPException(404, {"code": "FLIGHT_NOT_FOUND", "message": f"No flight '{flightNumber}' on {departureDate}."})
    return [b for b in BAGS.values() if b.get("assignedFlightNumber") == flightNumber and b.get("assignedDepartureDate") == departureDate]


# ── Lost baggage ───────────────────────────────────────────────────────────────

@app.get("/lost-baggage-cases", response_model=list[LostBaggageCase], tags=["lost-baggage"])
def list_lost_baggage_cases(status: Optional[LostBaggageCaseStatus] = None, pnr: Optional[str] = None):
    results = list(LOST_BAGGAGE_CASES.values())
    if status:
        results = [c for c in results if c["status"] == status.value]
    if pnr:
        results = [c for c in results if c["pnr"] == pnr]
    return results

@app.post("/lost-baggage-cases", response_model=LostBaggageCase, status_code=201, tags=["lost-baggage"])
def create_lost_baggage_case(body: LostBaggageCaseInput):
    if body.pnr not in BOOKINGS:
        raise HTTPException(400, {"code": "UNKNOWN_BOOKING", "message": f"No booking with PNR '{body.pnr}'."})
    case_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    case = {
        "caseId": case_id, "pnr": body.pnr, "bagTag": body.bagTag,
        "reportedAtAirport": body.reportedAtAirport, "description": body.description,
        "status": "OPEN", "openedAt": now,
    }
    LOST_BAGGAGE_CASES[case_id] = case
    return case

@app.get("/lost-baggage-cases/{caseId}", response_model=LostBaggageCase, tags=["lost-baggage"])
def get_lost_baggage_case(caseId: str):
    if caseId not in LOST_BAGGAGE_CASES:
        raise HTTPException(404, {"code": "CASE_NOT_FOUND", "message": f"No lost-baggage case '{caseId}'."})
    return LOST_BAGGAGE_CASES[caseId]

@app.patch("/lost-baggage-cases/{caseId}", response_model=LostBaggageCase, tags=["lost-baggage"])
def patch_lost_baggage_case(caseId: str, body: LostBaggageCasePatch):
    if caseId not in LOST_BAGGAGE_CASES:
        raise HTTPException(404, {"code": "CASE_NOT_FOUND", "message": f"No lost-baggage case '{caseId}'."})
    case = copy.copy(LOST_BAGGAGE_CASES[caseId])
    for field, value in body.model_dump(exclude_none=True).items():
        case[field] = value.value if isinstance(value, Enum) else value
    LOST_BAGGAGE_CASES[caseId] = case
    return case

@app.delete("/lost-baggage-cases/{caseId}", status_code=204, tags=["lost-baggage"])
def close_lost_baggage_case(caseId: str):
    if caseId not in LOST_BAGGAGE_CASES:
        raise HTTPException(404, {"code": "CASE_NOT_FOUND", "message": f"No lost-baggage case '{caseId}'."})
    LOST_BAGGAGE_CASES[caseId]["status"] = "CLOSED"
