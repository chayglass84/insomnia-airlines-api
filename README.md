# Insomnia Airlines API

A simple local REST API for the fictional Insomnia Airlines, covering airports, routes, and scheduled flights.

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

| Method | Path | Description |
|--------|------|-------------|
| GET | `/airports` | List airports (`?country=CA`) |
| POST | `/airports` | Add an airport |
| GET | `/airports/{iataCode}` | Get one airport |
| PUT | `/airports/{iataCode}` | Update an airport |
| DELETE | `/airports/{iataCode}` | Remove an airport |
| GET | `/routes` | List routes (`?origin=YYZ&destination=SFO`) |
| POST | `/routes` | Publish a route |
| GET | `/routes/{routeId}` | Get one route |
| DELETE | `/routes/{routeId}` | Withdraw a route |
| GET | `/flights` | List flights (`?origin=YYZ&departureDate=2026-05-08&status=SCHEDULED`) |
| POST | `/flights` | Schedule a flight |
| GET | `/flights/{flightNumber}?departureDate=` | Get one flight |
| PATCH | `/flights/{flightNumber}?departureDate=` | Update status, gate, or times |
| DELETE | `/flights/{flightNumber}?departureDate=` | Cancel a flight |

## Seed data

10 airports (YYZ, YUL, YVR, SEA, SFO, ORD, IAH, IAD, BOS, FLL), 10 routes, and 10 flights pre-loaded on startup. Mutations work within a session; restarting the server resets everything.

## API spec

The OpenAPI spec this was built from lives in `flights.yaml`.
