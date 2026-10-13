
from datetime import datetime, timedelta, timezone


def add_checkpoint_arrival_times(
    checkpoints: list[dict],
    departure_time: datetime,
    route_distance_miles: float,
    route_duration_seconds: float,
) -> list[dict]:
    """
    Add estimated arrival timestamps to route checkpoints.

    The initial estimate assumes constant average speed across the route.
    The departure time must be timezone-aware.
    """

    if departure_time.tzinfo is None or departure_time.utcoffset() is None:
        raise ValueError("Departure time must include a timezone.")

    if route_distance_miles <= 0:
        raise ValueError("Route distance must be positive.")

    if route_duration_seconds < 0:
        raise ValueError("Route duration cannot be negative.")

    departure_utc = departure_time.astimezone(timezone.utc)
    result = []

    for checkpoint in checkpoints:
        distance = float(checkpoint["distance_miles"])

        if distance < 0 or distance > route_distance_miles:
            raise ValueError(
                "Checkpoint distance must be within the route."
            )

        fraction = distance / route_distance_miles
        elapsed_seconds = route_duration_seconds * fraction

        arrival_time = departure_utc + timedelta(
            seconds=elapsed_seconds
        )

        result.append({
            **checkpoint,
            "arrival_time": arrival_time.isoformat(),
        })

    return result
