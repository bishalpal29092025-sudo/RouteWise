import logging
import time

import requests


logger = logging.getLogger(__name__)

OPEN_METEO_API_URL = "https://api.open-meteo.com/v1/forecast"
REQUEST_TIMEOUT_SECONDS = 15
RATE_LIMIT_RETRY_DELAY_SECONDS = 2
MAX_RATE_LIMIT_RETRIES = 1


class WeatherServiceError(Exception):
    """Raised when weather data cannot be retrieved."""


def get_weather_forecasts(
    locations: list[tuple[float, float]],
    forecast_days: int = 2,
) -> list[dict]:
    """
    Retrieve hourly forecasts for multiple locations.

    Args:
        locations: List of (latitude, longitude) pairs.
        forecast_days: Number of forecast days, from 1 to 16.

    Returns:
        A list of forecast dictionaries in the same order as locations.

    Raises:
        ValueError: If the input locations or forecast days are invalid.
        WeatherServiceError: If the weather provider request fails.
    """
    if not locations:
        raise ValueError("At least one location is required.")

    if not 1 <= forecast_days <= 16:
        raise ValueError("forecast_days must be between 1 and 16.")

    for latitude, longitude in locations:
        if not -90 <= latitude <= 90:
            raise ValueError("Latitude must be between -90 and 90.")

        if not -180 <= longitude <= 180:
            raise ValueError("Longitude must be between -180 and 180.")

    params = {
        "latitude": ",".join(
            str(latitude) for latitude, _ in locations
        ),
        "longitude": ",".join(
            str(longitude) for _, longitude in locations
        ),
        "hourly": "wind_speed_10m,precipitation,rain,snowfall",
        "wind_speed_unit": "mph",
        "precipitation_unit": "inch",
        "forecast_days": forecast_days,
        "timezone": "UTC",
    }

    # Retry once if Open-Meteo rate-limits this request.
    for attempt in range(MAX_RATE_LIMIT_RETRIES + 1):
        try:
            response = requests.get(
                OPEN_METEO_API_URL,
                params=params,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )

            if (
                response.status_code == 429
                and attempt < MAX_RATE_LIMIT_RETRIES
            ):
                logger.warning(
                    "Open-Meteo returned HTTP 429. "
                    "Retrying once after a short delay."
                )
                response.close()
                time.sleep(RATE_LIMIT_RETRY_DELAY_SECONDS)
                continue

            response.raise_for_status()
            data = response.json()
            break

        except requests.Timeout as exc:
            logger.warning(
                "Open-Meteo request timed out: %s",
                type(exc).__name__,
            )
            raise WeatherServiceError(
                "The weather request timed out."
            ) from exc

        except requests.RequestException as exc:
            error_response = getattr(exc, "response", None)

            if error_response is not None:
                logger.warning(
                    "Open-Meteo returned HTTP %s.",
                    error_response.status_code,
                )
            else:
                logger.warning(
                    "Open-Meteo connection failed: %s",
                    type(exc).__name__,
                )

            if (
                error_response is not None
                and error_response.status_code == 429
            ):
                raise WeatherServiceError(
                    "Open-Meteo rate limit reached. "
                    "Please try again later."
                ) from exc

            raise WeatherServiceError(
                "Unable to retrieve weather data."
            ) from exc

        except ValueError as exc:
            logger.warning(
                "Open-Meteo returned invalid JSON: %s",
                type(exc).__name__,
            )
            raise WeatherServiceError(
                "The weather provider returned invalid JSON."
            ) from exc

    else:
        raise WeatherServiceError(
            "Unable to retrieve weather data."
        )

    # A single location returns an object.
    # Multiple locations return a list of forecast objects.
    if len(locations) == 1 and isinstance(data, dict):
        data = [data]

    if not isinstance(data, list) or len(data) != len(locations):
        logger.warning(
            "Open-Meteo returned an unexpected response format."
        )
        raise WeatherServiceError(
            "The provider returned an unexpected number of forecasts."
        )

    results = []

    for index, item in enumerate(data):
        if not isinstance(item, dict):
            raise WeatherServiceError(
                f"Invalid weather response for location {index}."
            )

        hourly = item.get("hourly")

        if not isinstance(hourly, dict) or not hourly.get("time"):
            raise WeatherServiceError(
                f"No hourly forecast was returned for location {index}."
            )

        results.append(
            {
                "provider": "Open-Meteo",
                "latitude": item.get("latitude"),
                "longitude": item.get("longitude"),
                "timezone": item.get("timezone"),
                "hourly": hourly,
            }
        )

    return results


def get_weather_forecast(
    latitude: float,
    longitude: float,
    forecast_days: int = 2,
) -> dict:
    """
    Retrieve hourly weather for one location.

    Kept compatible with existing code that uses this function.
    """
    return get_weather_forecasts(
        [(latitude, longitude)],
        forecast_days=forecast_days,
    )[0]