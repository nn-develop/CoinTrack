import os
import uvicorn


def run_uvicorn():
    uvicorn_host: str = os.getenv("UVICORN_HOST", "0.0.0.0")
    uvicorn_port: int = int(os.getenv("UVICORN_PORT", 8000))
    uvicorn.run("main:app", host=uvicorn_host, port=uvicorn_port)
