# Insomnia Airlines API

A simple local REST API for the fictional Insomnia Airlines, covering airports, routes, flights, bookings, passengers, seats, and baggage.

Built with **Python + FastAPI**. All data lives in memory — no database, no setup beyond installing two packages.

## Quickstart

```bash
pip3 install -r requirements.txt
python3 -m uvicorn main:app --reload
```

Then open:

- `http://localhost:8000` — endpoint reference page
- `http://localhost:8000/docs` — interactive docs (try requests in the browser)

## Endpoints

### Airports
| Method | Path | Description |
|--------|------|-------------|
| GET | `/airports` | List airports (`?country=CA`) |
| POST | `/airports` | Add an airport |
| GET | `/airports/{iataCode}` | Get one airport |
| PUT | `/airports/{iataCode}` | Update an airport |
| DELETE | `/airports/{iataCode}` | Remove an airport |

### Routes
| Method | Path | Description |
|--------|------|-------------|
| GET | `/routes` | List routes (`?origin=YYZ&destination=SFO`) |
| POST | `/routes` | Publish a route |
| GET | `/routes/{routeId}` | Get one route |
| DELETE | `/routes/{routeId}` | Withdraw a route |

### Flights
| Method | Path | Description |
|--------|------|-------------|
| GET | `/flights` | List flights (`?origin=YYZ&departureDate=2026-05-08&status=SCHEDULED`) |
| POST | `/flights` | Schedule a flight |
| GET | `/flights/{flightNumber}?departureDate=` | Get one flight |
| PATCH | `/flights/{flightNumber}?departureDate=` | Update status, gate, or times |
| DELETE | `/flights/{flightNumber}?departureDate=` | Cancel a flight |
| GET | `/flights/{flightNumber}/bags?departureDate=` | List bags on a flight |

### Bookings
| Method | Path | Description |
|--------|------|-------------|
| GET | `/bookings` | List bookings (`?status=CONFIRMED&frequentFlyerId=FF1029384`) |
| POST | `/bookings` | Create a booking (PNR auto-generated) |
| GET | `/bookings/{pnr}` | Get one booking |
| PATCH | `/bookings/{pnr}` | Update status or contact email |
| DELETE | `/bookings/{pnr}` | Cancel a booking |
| GET | `/bookings/{pnr}/bags` | List bags on a booking |

### Passengers & frequent flyers
| Method | Path | Description |
|--------|------|-------------|
| GET | `/bookings/{pnr}/passengers` | List passengers on a booking |
| POST | `/bookings/{pnr}/passengers` | Add a passenger |
| GET | `/bookings/{pnr}/passengers/{passengerId}` | Get one passenger |
| DELETE | `/bookings/{pnr}/passengers/{passengerId}` | Remove a passenger |
| GET | `/passengers/{frequentFlyerId}` | Get frequent-flyer profile |
| GET | `/passengers/{frequentFlyerId}/bookings` | List a frequent flyer's bookings |

### Seats
| Method | Path | Description |
|--------|------|-------------|
| GET | `/bookings/{pnr}/seats` | List seat assignments |
| POST | `/bookings/{pnr}/seats` | Assign a seat |
| PATCH | `/bookings/{pnr}/seats/{seatAssignmentId}` | Change seat number |
| DELETE | `/bookings/{pnr}/seats/{seatAssignmentId}` | Release a seat |

### Bags & tracking
| Method | Path | Description |
|--------|------|-------------|
| GET | `/bags` | List bags (`?pnr=AB12CD&status=LOADED`) |
| POST | `/bags` | Check in a bag (tag auto-generated) |
| GET | `/bags/{bagTag}` | Get one bag |
| PATCH | `/bags/{bagTag}` | Update weight, flight, or status |
| DELETE | `/bags/{bagTag}` | Remove a bag (only before any tracking events) |
| GET | `/bags/{bagTag}/events` | List tracking events for a bag |
| POST | `/bags/{bagTag}/events` | Record a scan event |

### Lost baggage
| Method | Path | Description |
|--------|------|-------------|
| GET | `/lost-baggage-cases` | List cases (`?status=SEARCHING&pnr=QR90ST`) |
| POST | `/lost-baggage-cases` | Open a case |
| GET | `/lost-baggage-cases/{caseId}` | Get one case |
| PATCH | `/lost-baggage-cases/{caseId}` | Update status, attach bag tag, add notes |
| DELETE | `/lost-baggage-cases/{caseId}` | Close a case |

## Seed data

All data is pre-loaded on startup and resets when you restart the server.

| Resource | Count | Notes |
|----------|-------|-------|
| Airports | 10 | YYZ, YUL, YVR, SEA, SFO, ORD, IAH, IAD, BOS, FLL |
| Routes | 10 | Subset of the 10 airports |
| Flights | 10 | Mix of statuses across 2026-05-08–09 |
| Bookings | 5 | PNRs: AB12CD, EF34GH, IJ56KL, MN78OP, QR90ST |
| Frequent flyers | 2 | FF1029384 (Alex Morgan, GOLD), FF2938475 (Sam Taylor, SILVER) |
| Bags | 6 | Linked to real PNRs and flights |
| Bag events | 16 | Tracking history across all bags |
| Lost baggage cases | 2 | One SEARCHING, one OPEN |

## API specs

The OpenAPI specs this was built from live in `flights.yaml`, `bookings.yaml`, and `baggage.yaml`.
