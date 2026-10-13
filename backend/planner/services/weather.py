
"""Retrieve hourly weather forecasts from Open-Meteo."""

import requests


OPEN_METEO_API_URL = "https://api.open-meteo.com/v1/forecast"
REQUEST_TIMEOUT_SECONDS = 15


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
        "latitude": ",".join(str(lat) for lat, _ in locations),
        "longitude": ",".join(str(lon) for _, lon in locations),
        "hourly": "wind_speed_10m,precipitation,rain,snowfall",
        "wind_speed_unit": "mph",
        "precipitation_unit": "inch",
        "forecast_days": forecast_days,
        "timezone": "UTC",
    }

    try:
        response = requests.get(
            OPEN_METEO_API_URL,
            params=params,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()

    except requests.Timeout as exc:
        raise WeatherServiceError(
            "The weather request timed out."
        ) from exc

    except requests.RequestException as exc:
        raise WeatherServiceError(
            "Unable to retrieve weather data."
        ) from exc

    except ValueError as exc:
        raise WeatherServiceError(
            "The weather provider returned invalid JSON."
        ) from exc

    # A single location returns an object; multiple locations
    # return a list of forecast objects.
    if len(locations) == 1 and isinstance(data, dict):
        data = [data]

    if not isinstance(data, list) or len(data) != len(locations):
        raise WeatherServiceError(
            "The provider returned an unexpected number of forecasts."
        )

    results = []

    for index, item in enumerate(data):
        hourly = item.get("hourly")

        if not hourly or not hourly.get("time"):
            raise WeatherServiceError(
                f"No hourly forecast was returned for location {index}."
            )

        results.append({
            "provider": "Open-Meteo",
            "latitude": item.get("latitude"),
            "longitude": item.get("longitude"),
            "timezone": item.get("timezone"),
            "hourly": hourly,
        })

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
