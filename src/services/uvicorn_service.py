import os
import uvicorn


def run_uvicorn():
    # Read Uvicorn host and port from environment variables
    uvicorn_host: str = os.getenv("UVICORN_HOST", "0.0.0.0")
    uvicorn_port: int = int(os.getenv("UVICORN_PORT", 8000))

    # Run Uvicorn server
    uvicorn.run("src.services.coin_api:app", host=uvicorn_host, port=uvicorn_port)
