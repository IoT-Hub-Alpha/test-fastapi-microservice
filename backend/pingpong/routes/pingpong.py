import asyncio
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import httpx

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


@router.post("/start/")
async def start_endpoint(request: StartRequest):
    """
    Orchestrate a sequence of HTTP requests to another service.

    Steps:
    1. POST to http://127.0.0.1:8100/api/start/ with {"start": "start"}
    2. POST to http://127.0.0.1:8100/api/ping/ with {"ping": "ping"}
    3. Wait 3 seconds
    4. POST to http://127.0.0.1:8100/api/ping/ with {"ping": "boom"}
    5. Return success message
    """
    if request.start != "start":
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid request"}
        )

    base_url = "http://127.0.0.1:8100"

    try:
        async with httpx.AsyncClient() as client:
            # Step 1: Send ping request
            await client.post(
                f"{base_url}/api/ping/",
                json={"ping": "ping"},
                timeout=10.0
            )

            # Step 2: Send boom request
            await client.post(
                f"{base_url}/api/ping/",
                json={"ping": "boom"},
                timeout=10.0
            )

            # Step 3: Wait 3 seconds
            await asyncio.sleep(3)          

            # Step 4: Send start request
            await client.post(
                f"{base_url}/api/start/",
                json={"start": "start"},
                timeout=10.0
            )

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