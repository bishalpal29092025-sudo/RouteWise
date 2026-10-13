
from decimal import Decimal


RISK_LEVELS = {
    "Low": 1,
    "Moderate": 2,
    "High": 3,
    "Severe": 4,
    "No Travel": 5,
}


def classify_wind(wind_mph: float) -> str:
    """Classify wind risk using the project's thresholds."""
    if wind_mph < 25:
        return "Low"
    if wind_mph < 35:
        return "Moderate"
    if wind_mph < 45:
        return "High"
    if wind_mph < 55:
        return "Severe"
    return "No Travel"


def classify_rain(rain_inches_per_hour: float) -> str:
    """Classify hourly rain intensity."""
    if rain_inches_per_hour < 0:
        raise ValueError("Rain cannot be negative.")
    if rain_inches_per_hour < 0.10:
        return "Low"
    if rain_inches_per_hour < 0.25:
        return "Moderate"
    if rain_inches_per_hour < 0.50:
        return "High"
    if rain_inches_per_hour <= 1.00:
        return "Severe"
    return "No Travel"


def classify_snow(snow_inches_per_hour: float) -> str:
    """Classify hourly snowfall intensity."""
    if snow_inches_per_hour < 0:
        raise ValueError("Snowfall cannot be negative.")
    if snow_inches_per_hour < 0.5:
        return "Low"
    if snow_inches_per_hour < 1.0:
        return "Moderate"
    if snow_inches_per_hour < 2.0:
        return "High"
    if snow_inches_per_hour <= 3.0:
        return "Severe"
    return "No Travel"


def calculate_checkpoint_risk(
    wind_mph: float,
    rain_inches_per_hour: float,
    snow_inches_per_hour: float,
    truck_load_lbs: float,
) -> dict:
    """
    Return individual risks and the most restrictive combined risk.

    Load rules may increase risk, but never reduce weather risk.
    """
    if truck_load_lbs <= 0:
        raise ValueError("Truck load must be positive.")

    wind_risk = classify_wind(wind_mph)
    rain_risk = classify_rain(rain_inches_per_hour)
    snow_risk = classify_snow(snow_inches_per_hour)

    risks = [wind_risk, rain_risk, snow_risk]
    load_risk = "Low"

    if wind_mph >= 55:
        load_risk = "No Travel"
    elif wind_mph >= 45 and truck_load_lbs > 30000:
        load_risk = "No Travel"
    elif wind_mph >= 35 and truck_load_lbs > 40000:
        load_risk = "Severe"

    risks.append(load_risk)

    final_risk = max(risks, key=lambda risk: RISK_LEVELS[risk])

    return {
        "wind_risk": wind_risk,
        "rain_risk": rain_risk,
        "snow_risk": snow_risk,
        "load_risk": load_risk,
        "final_risk": final_risk,
        "risk_value": RISK_LEVELS[final_risk],
    }


def average_risk(risk_levels: list[str]) -> float:
    """Calculate the mean of the documented numeric risk values."""
    if not risk_levels:
        raise ValueError("At least one risk level is required.")

    try:
        values = [RISK_LEVELS[level] for level in risk_levels]
    except KeyError as exc:
        raise ValueError(f"Unknown risk level: {exc.args[0]}") from exc

    return sum(values) / len(values)


def risk_miles_by_category(
    checkpoints: list[dict],
    route_distance_miles: float,
) -> dict:
    """
    Estimate risk miles from checkpoint intervals.

    Each checkpoint's risk applies from its distance along the route
    to the next checkpoint, or to the route end for the final point.
    """
    if route_distance_miles < 0:
        raise ValueError("Route distance cannot be negative.")

    totals = {level: 0.0 for level in RISK_LEVELS}

    if route_distance_miles == 0:
        return totals

    ordered = sorted(
        checkpoints,
        key=lambda point: point["distance_miles"],
    )

    if not ordered:
        raise ValueError("Checkpoints are required for a nonzero route.")

    for index, point in enumerate(ordered):
        start = max(0.0, float(point["distance_miles"]))

        if index + 1 < len(ordered):
            end = min(
                route_distance_miles,
                float(ordered[index + 1]["distance_miles"]),
            )
        else:
            end = route_distance_miles

        segment_miles = max(0.0, end - start)
        risk = point["final_risk"]

        if risk not in totals:
            raise ValueError(f"Unknown risk level: {risk}")

        totals[risk] += segment_miles

    return totals
