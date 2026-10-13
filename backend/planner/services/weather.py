
"""Retrieve and cache hourly weather forecasts from Open-Meteo."""

import hashlib
import json
import logging
import time

import requests
from django.core.cache import cache


logger = logging.getLogger(__name__)

OPEN_METEO_API_URL = "https://api.open-meteo.com/v1/forecast"

REQUEST_TIMEOUT_SECONDS = 15
RATE_LIMIT_RETRY_DELAY_SECONDS = 2
MAX_RATE_LIMIT_RETRIES = 1
WEATHER_CACHE_TTL_SECONDS = 600  # 10 minutes


class WeatherServiceError(Exception):
    """Raised when weather data cannot be retrieved."""


def get_weather_forecasts(
    locations: list[tuple[float, float]],
    forecast_days: int = 2,
) -> list[dict]:
    """
    Retrieve hourly forecasts for multiple locations.

    Successful responses are cached for 10 minutes to reduce
    repeated requests to Open-Meteo.

    Args:
        locations: List of (latitude, longitude) pairs.
        forecast_days: Number of forecast days, from 1 to 16.

    Returns:
        Forecast dictionaries in the same order as locations.

    Raises:
        ValueError: If inputs are invalid.
        WeatherServiceError: If weather data cannot be retrieved.
    """
    if not locations:
        raise ValueError("At least one location is required.")

    if not 1 <= forecast_days <= 16:
        raise ValueError("forecast_days must be between 1 and 16.")

    normalized_locations = []

    for location in locations:
        if not isinstance(location, (tuple, list)) or len(location) != 2:
            raise ValueError(
                "Each location must contain latitude and longitude."
            )

        latitude, longitude = location

        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except (TypeError, ValueError) as exc:
            raise ValueError("Coordinates must be numeric.") from exc

        if not -90 <= latitude <= 90:
            raise ValueError("Latitude must be between -90 and 90.")

        if not -180 <= longitude <= 180:
            raise ValueError("Longitude must be between -180 and 180.")

        normalized_locations.append((latitude, longitude))

    params = {
        "latitude": ",".join(
            str(latitude) for latitude, _ in normalized_locations
        ),
        "longitude": ",".join(
            str(longitude) for _, longitude in normalized_locations
        ),
        "hourly": "wind_speed_10m,precipitation,rain,snowfall",
        "wind_speed_unit": "mph",
        "precipitation_unit": "inch",
        "forecast_days": forecast_days,
        "timezone": "UTC",
    }

    # Generate a stable key for identical forecast requests.
    cache_payload = json.dumps(
        {
            "locations": [
                [round(latitude, 5), round(longitude, 5)]
                for latitude, longitude in normalized_locations
            ],
            "forecast_days": forecast_days,
            "hourly": params["hourly"],
            "wind_speed_unit": params["wind_speed_unit"],
            "precipitation_unit": params["precipitation_unit"],
            "timezone": params["timezone"],
        },
        sort_keys=True,
    )

    cache_hash = hashlib.sha256(
        cache_payload.encode("utf-8")
    ).hexdigest()

    cache_key = f"weather_forecast:{cache_hash}"

    # Cache problems must not prevent a fresh weather request.
    try:
        cached_results = cache.get(cache_key)
    except Exception:
        logger.warning(
            "Weather cache lookup failed; requesting fresh weather."
        )
        cached_results = None

    if cached_results is not None:
        logger.info("Using cached Open-Meteo forecast.")
        return cached_results

    # Request weather and retry once if the provider rate-limits us.
    data = None

    for attempt in range(MAX_RATE_LIMIT_RETRIES + 1):
        try:
            response = requests.get(
                OPEN_METEO_API_URL,
                params=params,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )

            if response.status_code == 429:
                # Log the provider response to help diagnose the limit.
                # Truncate it to avoid excessively large log entries.
                logger.warning(
                    "Open-Meteo HTTP 429 response details: %s",
                    response.text[:500],
                )

                if attempt < MAX_RATE_LIMIT_RETRIES:
                    logger.warning(
                        "Open-Meteo returned HTTP 429. "
                        "Retrying once after a short delay."
                    )
                    response.close()
                    time.sleep(RATE_LIMIT_RETRY_DELAY_SECONDS)
                    continue

                logger.warning(
                    "Open-Meteo rate limit remains after retry."
                )
                response.close()

                raise WeatherServiceError(
                    "Open-Meteo rate limit reached. "
                    "Please try again later."
                )

            response.raise_for_status()

            try:
                data = response.json()
            except ValueError as exc:
                logger.warning("Open-Meteo returned invalid JSON.")
                raise WeatherServiceError(
                    "The weather provider returned invalid JSON."
                ) from exc
            finally:
                response.close()

            break

        except WeatherServiceError:
            raise

        except requests.Timeout as exc:
            logger.warning("Open-Meteo request timed out.")
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

            raise WeatherServiceError(
                "Unable to retrieve weather data."
            ) from exc

    if data is None:
        raise WeatherServiceError("Unable to retrieve weather data.")

    # Open-Meteo returns an object for one location and a list
    # for multiple locations.
    if len(normalized_locations) == 1 and isinstance(data, dict):
        data = [data]

    if (
        not isinstance(data, list)
        or len(data) != len(normalized_locations)
    ):
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

    # Cache only validated, successful responses.
    # A cache write failure should not discard fresh weather data.
    try:
        cache.set(
            cache_key,
            results,
            timeout=WEATHER_CACHE_TTL_SECONDS,
        )
    except Exception:
        logger.warning(
            "Weather cache write failed; returning fresh forecast."
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
