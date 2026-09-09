import os
import time

from dotenv import load_dotenv
from groq import Groq
from groq import APIConnectionError
from groq import APITimeoutError
from groq import RateLimitError
from groq import InternalServerError


load_dotenv()


class LLMProvider:
    """
    Centralized LLM provider for AeroWatch.

    Responsibilities:
    - Manage Groq client configuration
    - Generate normal text responses
    - Generate JSON responses
    - Retry temporary failures
    - Handle rate limits with exponential backoff
    """

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is not configured."
            )

        self.client = Groq(
            api_key=api_key,
            timeout=float(
                os.getenv("GROQ_TIMEOUT", "30")
            ),
        )

        self.model = os.getenv(
            "GROQ_MODEL",
            "llama-3.3-70b-versatile",
        )

        self.max_retries = int(
            os.getenv("GROQ_MAX_RETRIES", "3")
        )

        self.base_retry_delay = float(
            os.getenv("GROQ_RETRY_DELAY", "2")
        )

    # ---------------------------------------------------------
    # Retry handling
    # ---------------------------------------------------------

    def _should_retry(self, error: Exception) -> bool:
        """
        Determine whether an exception is likely temporary
        and therefore safe to retry.
        """

        return isinstance(
            error,
            (
                RateLimitError,
                APIConnectionError,
                APITimeoutError,
                InternalServerError,
            ),
        )

    def _wait_before_retry(self, attempt: int) -> None:
        """
        Exponential backoff.

        Attempt 0 -> base delay
        Attempt 1 -> 2x base delay
        Attempt 2 -> 4x base delay
        """

        delay = self.base_retry_delay * (2 ** attempt)

        print(
            f"[LLMProvider] Temporary Groq failure. "
            f"Retrying in {delay:.1f}s..."
        )

        time.sleep(delay)

    # ---------------------------------------------------------
    # Normal text generation
    # ---------------------------------------------------------

    def generate(self, prompt: str) -> str:
        """
        Generate a normal text response from the configured
        Groq model.
        """

        last_error = None

        for attempt in range(self.max_retries + 1):

            try:

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are AeroWatch, an aviation "
                                "disruption analysis system. "
                                "You must reason only from the "
                                "evidence provided to you."
                            ),
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        },
                    ],
                    temperature=0,
                )

                return response.choices[0].message.content

            except Exception as error:

                last_error = error

                if (
                    not self._should_retry(error)
                    or attempt >= self.max_retries
                ):
                    raise RuntimeError(
                        "LLM generation failed after "
                        f"{attempt + 1} attempt(s): "
                        f"{error}"
                    ) from error

                self._wait_before_retry(attempt)

        raise RuntimeError(
            f"LLM generation failed: {last_error}"
        )

    # ---------------------------------------------------------
    # JSON generation
    # ---------------------------------------------------------

    def generate_json(self, prompt: str) -> str:
        """
        Generate a JSON response from the configured Groq model.

        Groq JSON Object Mode is used here. The caller is
        responsible for validating the returned JSON against
        the appropriate Pydantic schema.
        """

        last_error = None

        for attempt in range(self.max_retries + 1):

            try:

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are AeroWatch, an aviation "
                                "disruption analysis system. "
                                "You must reason only from the "
                                "evidence provided. "
                                "Return ONLY valid JSON. "
                                "Do not include markdown, "
                                "explanations, or code fences."
                            ),
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        },
                    ],
                    response_format={
                        "type": "json_object"
                    },
                    temperature=0,
                )

                return response.choices[0].message.content

            except Exception as error:

                last_error = error

                if (
                    not self._should_retry(error)
                    or attempt >= self.max_retries
                ):
                    raise RuntimeError(
                        "LLM JSON generation failed after "
                        f"{attempt + 1} attempt(s): "
                        f"{error}"
                    ) from error

                self._wait_before_retry(attempt)

        raise RuntimeError(
            f"LLM JSON generation failed: {last_error}"
        )