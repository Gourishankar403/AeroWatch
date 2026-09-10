from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router


app = FastAPI(
    title="AeroWatch API",
    description=(
        "Evidence-grounded aviation disruption "
        "investigation system."
    ),
    version="0.1.0",
)


# Allow the React/Vite frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register API routes
app.include_router(router)


@app.get("/")
def root():
    return {
        "name": "AeroWatch",
        "status": "online",
        "version": "0.1.0",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }