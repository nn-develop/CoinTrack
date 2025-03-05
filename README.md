# CoinTrack API

A FastAPI-based cryptocurrency tracking application that allows managing coin data with integration to CoinGecko API.

## Features
- CRUD operations for cryptocurrency data
- Integration with CoinGecko API for validating and enriching coin data
- Redis caching for improved performance
- PostgreSQL database for persistent storage
- Alembic migrations for database versioning
- Async API implementation
- Health check endpoints
- Periodic coin data updates

## Prerequisites
- Docker and Docker Compose

## Quick Start
1. Clone the repository:
    ```bash
    git clone https://github.com/nn-develop/CoinTrack.git
    ```
2. Build and start the application using Docker Compose:
    ```bash
    docker compose up --build
    ```

This will start:
- PostgreSQL database
- The CoinTrack backend container which will automatically (with main.py):
  - Sets up and configures the PostgreSQL database
  - Runs Alembic migrations
  - Runs tests (just a few as a sample)
  - Finally launches the FastAPI application via Uvicorn on port 8000
- Redis cache service on port 6379

Access the API at `http://localhost:8000`.

## API Documentation
The API documentation is automatically generated and can be accessed at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Health Endpoints
- `GET /health` - Basic health check
- `GET /health/readiness` - Checks database and Redis connections
- `GET /health/liveness` - Confirms service is running
- `GET /health/version` - Returns API version information

### Coin Endpoints
- `POST /coins/` - Create a new coin
- `GET /coins/{coin_id}` - Get coin by ID
- `PUT /coins/{coin_id}` - Update coin data
- `DELETE /coins/{coin_id}` - Delete a coin
- `GET /coins/` - List all coins
- `POST /coins/update-coins/` - Trigger manual coin data update

## Data Model
Each coin record contains:
- `id` (string): Unique identifier for the coin (e.g., "bitcoin")
- `symbol` (string): Trading symbol for the coin (e.g., "btc")
- `name` (string): Full name of the coin (e.g., "Bitcoin")
- `target_price` (float, optional): Target price for notifications/tracking

## Project Structure
- `main.py`: Application entry point
- `src`: Core application code
- `api/routes/`: API route definitions
- `models/`: Database models
- `schemas/`: Pydantic models for request/response validation
- `services/`: Business logic
- `coingecko/`: CoinGecko API integration
- `database_utils/`: Database connection and operations
- `redis_cache/`: Redis cache implementation
- `alembic/`: Database migration files
- `logger.py`: Custom logging setup

## Environment Variables
The application uses the following environment variables (defined in `.env`):

| Variable              | Description                  | Default            |
|-----------------------|------------------------------|--------------------|
| POSTGRES_USER         | PostgreSQL username          | cointrack_user     |
| POSTGRES_PASSWORD     | PostgreSQL password          | cointrack_password |
| POSTGRES_DB           | PostgreSQL database name     | cointrack_db       |
| POSTGRES_HOST         | PostgreSQL host              | postgres           |
| POSTGRES_PORT         | PostgreSQL port              | 5432               |
| REDIS_HOST            | Redis host                   | redis              |
| REDIS_PORT            | Redis port                   | 6379               |
| REDIS_DB              | Redis database index         | 0                  |
| COINGECKO_API_KEY     | CoinGecko API key            | your_api_key       |
| UVICORN_HOST          | Host for the Uvicorn server  | 0.0.0.0            |
| UVICORN_PORT          | Port for the Uvicorn server  | 8000               |
| LOG_LEVEL             | Logging level                | INFO               |
