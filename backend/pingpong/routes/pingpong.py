import asyncio
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import httpx
import os

router = APIRouter()


class PingRequest(BaseModel):
    ping: str = Field(..., description="Ping message: 'ping' or 'boom'")


class StartRequest(BaseModel):
    start: str = Field(..., description="Start command: 'start'")


@router.post("/ping/")
async def ping_endpoint(request: PingRequest):
    """
    Handle ping requests.

    - If receives "ping": return {"message": "pong"} with status 200
    - If receives "boom": return {"message": "i don't like \"BOOM\""} with status 400
    """
    if request.ping == "ping":
        return {"message": "pong"}
    if request.ping == "boom":
        return JSONResponse(
            status_code=400,
            content={"message": "i don't like \"BOOM\""}
        )
    return JSONResponse(
        status_code=400,
        content={"error": "Invalid request"}
    )


async def _start_cycle(django_host: str):
    """Background task function to execute the start cycle"""
    try:
        base_url = f"http://{django_host}:8100"
        async with httpx.AsyncClient() as client:
            # Step 1: Send ping request
            await client.post(
                f"{base_url}/api/ping/",
                json={"ping": "ping"},
                timeout=15.0
            )

            # Step 2: Wait 3 seconds
            await asyncio.sleep(3)

            # Step 3: Send boom request
            await client.post(
                f"{base_url}/api/ping/",
                json={"ping": "boom"},
                timeout=15.0
            )

            # Step 4: Wait 5 seconds for delay before next cycle
            await asyncio.sleep(5)

            # Step 5: Send start request to continue the cycle (non-blocking)
            await client.post(
                f"{base_url}/api/start/",
                json={"start": "start"},
                timeout=15.0
            )
    except Exception as e:
        print(f"Error in start cycle: {e}")


@router.post("/start/")
async def start_endpoint(request: StartRequest, background_tasks: BackgroundTasks):
    """
    Orchestrate a sequence of HTTP requests to another service.

    Steps:
    1. Send ping to Django
    2. Wait 3 seconds
    3. Send boom to Django
    4. Wait 5 seconds
    5. Send start request to Django to continue the cycle
    """
    if request.start != "start":
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid request"}
        )

    # Get Django host from environment variable (default to localhost for standalone)
    django_host = os.getenv("DJANGO_HOST", "127.0.0.1")

    # Start the cycle in a background task so this endpoint returns immediately
    background_tasks.add_task(_start_cycle, django_host)

    try:
        return {"message": "Requests sent successfully"}

    except httpx.ConnectError as e:
        return JSONResponse(
            status_code=503,
            content={"error": f"Failed to connect to upstream service: {str(e)}"}
        )
    except httpx.TimeoutException as e:
        return JSONResponse(
            status_code=504,
            content={"error": f"Upstream service timeout: {str(e)}"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Unexpected error: {str(e)}"}
        )