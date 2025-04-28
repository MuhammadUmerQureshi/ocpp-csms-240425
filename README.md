# OCPP Server with Database Integration

This application is an OCPP (Open Charge Point Protocol) Central System server with database integration for managing EV charging stations.

## Features

- OCPP 1.6 WebSocket server (JSON mode)
- REST API endpoints for managing charging stations
- Database integration using SQLAlchemy
- Full charging process management (boot notification, status, charging sessions, etc.)
- Support for multiple companies, sites, and chargers

## Requirements

- Python 3.8+
- FastAPI
- SQLAlchemy
- OCPP library
- Database (SQLite, PostgreSQL, MySQL)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ocpp-server
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
alembic upgrade head
```

## Configuration

The application can be configured using environment variables:

- `DATABASE_URL`: The database connection string (default: `sqlite:///./ocpp_server.db`)
- `LOG_LEVEL`: Logging level (default: `INFO`)

## Running the Server

```bash
uvicorn app.main:app --reload
```

The server will be available at http://localhost:8000.

API documentation is available at http://localhost:8000/docs.

## Database Structure

The database has the following main tables:

- Companies: Manages EV charging station companies
- Sites: Physical locations where chargers are installed
- Chargers: Individual charging stations
- Connectors: Charging ports on each charger
- Drivers: EV drivers who use the charging stations
- RFIDCards: RFID cards assigned to drivers
- ChargeSessions: Records of charging sessions
- EventsData: Data recorded during charging sessions

## API Endpoints

### OCPP WebSocket Endpoint

- `/ocpp/{charge_point_id}`: WebSocket connection for OCPP 1.6 communication

### REST API Endpoints

#### OCPP Command Endpoints

- GET `/charge_points`: List connected charge points
- POST `/charge_points/{charge_point_id}/reset`: Reset a charge point
- POST `/charge_points/{charge_point_id}/change_configuration`: Change configuration
- POST `/charge_points/{charge_point_id}/unlock`: Unlock a connector
- GET `/charge_points/{charge_point_id}/configuration`: Get configuration
- POST `/charge_points/{charge_point_id}/availability`: Change availability
- POST `/charge_points/{charge_point_id}/remote_start`: Start a charging session
- POST `/charge_points/{charge_point_id}/remote_stop`: Stop a charging session
- POST `/charge_points/{charge_point_id}/charging_profile`: Set a charging profile
- POST `/charge_points/{charge_point_id}/reserve_now`: Reserve a connector
- POST `/charge_points/{charge_point_id}/cancel_reservation`: Cancel a reservation

#### Database Endpoints

- Companies: CRUD operations at `/db/companies/`
- Sites: CRUD operations at `/db/sites/` and `/db/companies/{company_id}/sites/`
- Chargers: CRUD operations at `/db/chargers/` and `/db/companies/{company_id}/sites/{site_id}/chargers/`
- Connectors: CRUD operations for connectors
- Drivers: CRUD operations for EV drivers
- RFID Cards: CRUD operations for RFID cards
- Charge Sessions: CRUD operations for charge sessions

#### OCPP-DB Integration Endpoints

- POST `/db/ocpp/charger/register`: Register a charger from OCPP
- POST `/db/ocpp/connector/status`: Update connector status
- POST `/db/ocpp/session/start`: Start a charging session
- POST `/db/ocpp/session/end`: End a charging session
- POST `/db/ocpp/meter-values`: Record meter values
- POST `/db/ocpp/charger/heartbeat`: Record heartbeat

## License

This project is licensed under the MIT License - see the LICENSE file for details.