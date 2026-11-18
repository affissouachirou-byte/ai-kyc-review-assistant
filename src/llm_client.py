import os

from openai import (
    OpenAI,
    OpenAIError,
    APIConnectionError,
    APIStatusError,
)
from pydantic import ValidationError

from output_schema import KYCReviewOutput


MODEL_NAME = "gpt-4o-mini"
API_TIMEOUT = 30.0
MAX_RETRIES = 1


class KYCGenerationError(Exception):
    """Base exception for AI generation failures."""


class KYCTransientError(KYCGenerationError):
    """Temporary API failure eligible for deterministic fallback."""


class KYCConfigurationError(KYCGenerationError):
    """Invalid credentials or non-recoverable API configuration."""


class KYCResponseError(KYCGenerationError):
    """AI response could not be validated."""


def generate_ai_kyc_review(prompt: str) -> KYCReviewOutput:
    """Generate a structured, validated AI KYC assessment."""

    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key or not api_key.strip():
        raise KYCConfigurationError(
            "OpenAI credentials are missing."
        )

    if "\n" in api_key or "\r" in api_key:
        raise KYCConfigurationError(
            "OpenAI credentials have invalid formatting."
        )

    client = OpenAI(
        api_key=api_key,
        timeout=API_TIMEOUT,
        max_retries=MAX_RETRIES,
    )

    try:
        response = client.responses.parse(
            model=MODEL_NAME,
            input=prompt,
            text_format=KYCReviewOutput,
        )

    except APIConnectionError:
        raise KYCTransientError(
            "OpenAI connection or timeout failure."
        ) from None

    except APIStatusError as error:
        if error.status_code in (500, 502, 503, 504):
            raise KYCTransientError(
                "Temporary OpenAI server failure."
            ) from None

        raise KYCConfigurationError(
            "Non-recoverable OpenAI API status."
        ) from None

    except ValidationError:
        raise KYCResponseError(
            "AI response failed schema validation."
        ) from None

    except OpenAIError:
        raise KYCResponseError(
            "OpenAI generation failed."
        ) from None

    if response.output_parsed is None:
        raise KYCResponseError(
            "No validated structured response returned."
        )

    return response.output_parsed
