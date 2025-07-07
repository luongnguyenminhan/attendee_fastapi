from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def setup_cors_middleware(app: FastAPI):
    """Setup CORS middleware for the FastAPI app"""

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify exact origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )
