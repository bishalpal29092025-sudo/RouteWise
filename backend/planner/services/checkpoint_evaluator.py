
from planner.services.risk import calculate_checkpoint_risk
from planner.services.weather import WeatherServiceError


def evaluate_checkpoint(
    checkpoint: dict,
    weather: dict,
    truck_load_lbs: float,
) -> dict:
    """
    Combine checkpoint details, matched weather, and truck load
    to calculate the checkpoint's final risk.
    """

    required_fields = (
        "wind_mph",
        "rain_inches",
        "snowfall_inches",
    )

    missing_fields = [
        field
        for field in required_fields
        if weather.get(field) is None
    ]

    if missing_fields:
        raise WeatherServiceError(
            "Weather data is incomplete: "
            + ", ".join(missing_fields)
        )

    risk = calculate_checkpoint_risk(
        wind_mph=weather["wind_mph"],
        rain_inches_per_hour=weather["rain_inches"],
        snow_inches_per_hour=weather["snowfall_inches"],
        truck_load_lbs=float(truck_load_lbs),
    )

    return {
        **checkpoint,
        "weather": weather,
        **risk,
    }
