import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    """
    Central application configuration for AeroWatch.

    Values are loaded from environment variables when available,
    with safe defaults for local development.
    """

    # ---------------------------------------------------------
    # Application
    # ---------------------------------------------------------

    APP_NAME: str = os.getenv(
        "APP_NAME",
        "AeroWatch",
    )

    APP_VERSION: str = os.getenv(
        "APP_VERSION",
        "0.1.0",
    )

    MAX_REVISIONS: int = int(
        os.getenv(
            "MAX_REVISIONS",
            "2",
        )
    )

    # ---------------------------------------------------------
    # Groq / LLM
    # ---------------------------------------------------------

    GROQ_API_KEY: str = os.getenv(
        "GROQ_API_KEY",
        "",
    )

    GROQ_TIMEOUT: float = float(
        os.getenv(
            "GROQ_TIMEOUT",
            "30",
        )
    )

    GROQ_MAX_RETRIES: int = int(
        os.getenv(
            "GROQ_MAX_RETRIES",
            "3",
        )
    )

    GROQ_RETRY_DELAY: float = float(
        os.getenv(
            "GROQ_RETRY_DELAY",
            "2",
        )
    )

    GROQ_MODEL: str = os.getenv(
        "GROQ_MODEL",
        "llama-3.3-70b-versatile",
    )

    # ---------------------------------------------------------
    # Weather provider
    # ---------------------------------------------------------

    WEATHER_TIMEOUT: float = float(
        os.getenv(
            "WEATHER_TIMEOUT",
            "10",
        )
    )

    WEATHER_MAX_RETRIES: int = int(
        os.getenv(
            "WEATHER_MAX_RETRIES",
            "3",
        )
    )

    WEATHER_RETRY_DELAY: float = float(
        os.getenv(
            "WEATHER_RETRY_DELAY",
            "1",
        )
    )


settings = Settings()