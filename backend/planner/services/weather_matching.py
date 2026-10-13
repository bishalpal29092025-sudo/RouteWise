
from datetime import datetime, timezone

from planner.services.weather import WeatherServiceError


def match_weather_to_arrival(
    hourly_forecast: dict,
    arrival_time: str,
) -> dict:
    """
    Match a checkpoint's arrival time to the forecast for that hour.

    Forecast timestamps are interpreted as UTC because weather.py
    requests timezone="UTC".

    If the arrival hour is unavailable, return an explicit error
    rather than silently using unrelated weather data.
    """

    times = hourly_forecast.get("time", [])

    if not times:
        raise WeatherServiceError(
            "No hourly forecast timestamps are available."
        )

    try:
        arrival = datetime.fromisoformat(
            arrival_time.replace("Z", "+00:00")
        )

        if arrival.tzinfo is None:
            raise ValueError("Arrival time must include a timezone.")

        arrival = arrival.astimezone(timezone.utc)

        forecast_times = [
            datetime.fromisoformat(timestamp).replace(
                tzinfo=timezone.utc
            )
            for timestamp in times
        ]

    except (TypeError, ValueError) as exc:
        raise ValueError(
            "Arrival time or forecast timestamps are invalid."
        ) from exc

    # Use the forecast hour at or immediately before arrival.
    matching_index = None

    for index, forecast_time in enumerate(forecast_times):
        if forecast_time <= arrival:
            matching_index = index
        else:
            break

    if matching_index is None:
        raise WeatherServiceError(
            "No forecast is available at or before this arrival time."
        )

    if (
        arrival - forecast_times[matching_index]
    ).total_seconds() >= 3600:
        raise WeatherServiceError(
            "The arrival time is outside the available hourly forecast."
        )

    def get_hourly_value(field: str):
        values = hourly_forecast.get(field, [])

        if matching_index >= len(values):
            return None

        return values[matching_index]

    snowfall_cm = get_hourly_value("snowfall")

    return {
        "forecast_time": forecast_times[
            matching_index
        ].isoformat(),
        "arrival_time": arrival.isoformat(),
        "wind_mph": get_hourly_value("wind_speed_10m"),
        "rain_inches": get_hourly_value("rain"),
        "snowfall_inches": (
            None
            if snowfall_cm is None
            else snowfall_cm / 2.54
        ),
        "provider": "Open-Meteo",
    }
