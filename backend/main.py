from fastapi import FastAPI

from app.api.routes import router


app = FastAPI(
    title="AeroWatch API",
    description=(
        "Evidence-grounded aviation disruption "
        "investigation system."
    ),
    version="0.1.0",
)


app.include_router(
    router,
)


@app.get(
    "/",
)
def root():
    """
    Basic API information endpoint.
    """

    return {
        "name": "AeroWatch",
        "status": "online",
        "version": "0.1.0",
    }


@app.get(
    "/health",
)
def health():
    """
    Health check endpoint.
    """

    return {
        "status": "healthy",
    }