# FastAPI Ping/Pong Microservice

A lightweight FastAPI microservice that implements ping/pong messaging and inter-service communication patterns. This service is designed as a test/demo microservice for learning about distributed systems and API integration.

## Features

- **Ping/Pong Endpoint**: Simple message echo service with status-based responses
- **Start Endpoint**: Orchestrates multiple HTTP requests with timing sequences
- **Health Check**: Built-in `/health` endpoint for service monitoring
- **Interactive API Docs**: Auto-generated Swagger UI and OpenAPI schema
- **CORS Support**: Pre-configured CORS middleware for cross-origin requests
- **Docker Ready**: Complete Docker configuration for containerized deployment

## Quick Start

### 1. Set Up Python Virtual Environment

```bash
python3.13 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Development Server

```bash
uvicorn backend.pingpong.main:app --host 0.0.0.0 --port 8101 --reload
```

The server will start on `http://127.0.0.1:8101`

### 4. Access API Documentation

- **Swagger UI**: http://127.0.0.1:8101/docs
- **ReDoc**: http://127.0.0.1:8101/redoc
- **OpenAPI Schema**: http://127.0.0.1:8101/openapi.json

## Project Structure

```
test-fastapi-microservice/
├── backend/
│   └── pingpong/
│       ├── __init__.py
│       ├── main.py              # FastAPI application setup
│       └── routes/
│           ├── __init__.py
│           └── pingpong.py      # API endpoint implementations
├── venv/                        # Python virtual environment
├── requirements.txt             # Project dependencies
├── Dockerfile                   # Docker configuration
├── .dockerignore               # Docker build exclusions
├── .gitignore                  # Git exclusions
└── README.md                   # This file
```

## API Endpoints

### 1. Health Check

**Endpoint**: `GET /health`

Check if the service is running.

**Response** (200):
```json
{
  "status": "healthy"
}
```

### 2. Ping/Pong Service

**Endpoint**: `POST /api/ping/`

**Request**:
```json
{
  "ping": "ping"
}
```

**Success Response** (200):
```json
{
  "message": "pong"
}
```

**Boom Response** (400):
```json
{
  "message": "i don't like \"BOOM\""
}
```

**Invalid Input Response** (400):
```json
{
  "error": "Invalid request"
}
```

### 3. Start Service

**Endpoint**: `POST /api/start/`

Initiates a sequence of requests to an upstream service (typically running on port 8100).

**Request**:
```json
{
  "start": "start"
}
```

**Sequence**:
1. Sends `POST /api/start/` to `http://127.0.0.1:8100/api/start/`
2. Sends `POST /api/ping/` with `{"ping": "ping"}` to `http://127.0.0.1:8100/api/ping/`
3. Waits 3 seconds
4. Sends `POST /api/ping/` with `{"ping": "boom"}` to `http://127.0.0.1:8100/api/ping/`

**Success Response** (200):
```json
{
  "message": "Requests sent successfully"
}
```

**Error Responses**:
- 503: Service Unavailable (connection failed)
- 504: Gateway Timeout (request timeout)
- 500: Internal Server Error

## Testing the Endpoints

### Test 1: Health Check
```bash
curl http://127.0.0.1:8101/health
```

### Test 2: Ping with "ping"
```bash
curl -X POST http://127.0.0.1:8101/api/ping/ \
  -H "Content-Type: application/json" \
  -d '{"ping": "ping"}'
```

Expected: `{"message": "pong"}` (Status 200)

### Test 3: Ping with "boom"
```bash
curl -X POST http://127.0.0.1:8101/api/ping/ \
  -H "Content-Type: application/json" \
  -d '{"ping": "boom"}'
```

Expected: `{"message": "i don't like \"BOOM\""}` (Status 400)

### Test 4: Start Endpoint
```bash
curl -X POST http://127.0.0.1:8101/api/start/ \
  -H "Content-Type: application/json" \
  -d '{"start": "start"}'
```

Expected: `{"message": "Requests sent successfully"}` (Status 200)

Note: This requires another service running on port 8100.

## Docker Setup

### Build the Docker Image

```bash
docker build -t fastapi-test-microservice .
```

### Run the Container

```bash
docker run -p 8101:8101 fastapi-test-microservice
```

The service will be accessible at `http://127.0.0.1:8101`

### Run with Docker Compose

If you have another service on port 8100, you can use Docker Compose to orchestrate both:

```bash
docker run -p 8101:8101 fastapi-test-microservice
docker run -p 8100:8100 other-microservice  # Another terminal
```

## Dependencies

- **FastAPI** (0.135.1): Modern, fast web framework for building APIs
- **Uvicorn** (0.41.0): ASGI server for running FastAPI applications
- **Pydantic** (2.12.5): Data validation using Python type annotations
- **httpx** (0.28.1): Async HTTP client library for making requests
- **python-dotenv** (1.2.2): Environment variable management
- **Starlette** (0.52.1): ASGI web framework (dependency of FastAPI)

See `requirements.txt` for complete dependency list with versions.

## Development

### Code Structure

- `backend/pingpong/main.py`: FastAPI application setup, middleware configuration, and router inclusion
- `backend/pingpong/routes/pingpong.py`: API endpoint implementations using Pydantic models for validation

### Adding New Endpoints

1. Create a new function in `backend/pingpong/routes/pingpong.py` with the `@router.post()` decorator
2. Use Pydantic models for request/response validation
3. Use `HTTPException` for error responses with appropriate status codes

Example:
```python
class MyRequest(BaseModel):
    field: str

@router.post("/my-endpoint")
async def my_endpoint(request: MyRequest):
    return {"response": "data"}
```

## Environment Variables

Currently, the application doesn't require environment variables. To add them:

1. Create a `.env` file in the project root
2. Use `python-dotenv` to load variables: `from dotenv import load_dotenv`

Example `.env`:
```
UPSTREAM_SERVICE_URL=http://127.0.0.1:8100
LOG_LEVEL=INFO
```

## Performance Notes

- Async/await pattern ensures efficient handling of concurrent requests
- Proper timeout handling (10 seconds) for HTTP client connections
- CORS middleware is enabled for cross-origin requests

## License

This is a test/demo project for learning purposes.

## Support

For FastAPI documentation, visit: https://fastapi.tiangolo.com/