
from math import asin, cos, radians, sin, sqrt


EARTH_RADIUS_MILES = 3958.7613
ALLOWED_INTERVALS_MILES = {10, 25, 50}


def haversine_miles(
    point_a: tuple[float, float],
    point_b: tuple[float, float],
) -> float:
    """Calculate distance between two (latitude, longitude) points."""
    lat1, lon1 = point_a
    lat2, lon2 = point_b

    lat1, lon1, lat2, lon2 = map(
        radians, (lat1, lon1, lat2, lon2)
    )

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    value = (
        sin(delta_lat / 2) ** 2
        + cos(lat1) * cos(lat2) * sin(delta_lon / 2) ** 2
    )

    return 2 * EARTH_RADIUS_MILES * asin(sqrt(min(1.0, value)))


def interpolate_coordinate(
    start: tuple[float, float],
    end: tuple[float, float],
    fraction: float,
) -> tuple[float, float]:
    """Linearly interpolate between two nearby coordinates."""
    return (
        start[0] + (end[0] - start[0]) * fraction,
        start[1] + (end[1] - start[1]) * fraction,
    )


def sample_route_checkpoints(
    coordinates: list[list[float]],
    interval_miles: int = 25,
) -> list[dict]:
    """
    Sample a route at regular mileage intervals.

    Input geometry coordinates must use GeoJSON order:
    [longitude, latitude].

    The returned checkpoints use latitude and longitude fields.
    """
    if interval_miles not in ALLOWED_INTERVALS_MILES:
        raise ValueError(
            "Interval must be 10, 25, or 50 miles."
        )

    if len(coordinates) < 2:
        raise ValueError(
            "At least two route coordinates are required."
        )

    points = []

    for coordinate in coordinates:
        if len(coordinate) < 2:
            raise ValueError("Each coordinate must contain longitude and latitude.")

        longitude = float(coordinate[0])
        latitude = float(coordinate[1])

        if not -180 <= longitude <= 180:
            raise ValueError("Longitude is outside the valid range.")

        if not -90 <= latitude <= 90:
            raise ValueError("Latitude is outside the valid range.")

        points.append((latitude, longitude))

    segments = []
    total_distance = 0.0

    for index in range(len(points) - 1):
        segment_distance = haversine_miles(
            points[index],
            points[index + 1],
        )

        segments.append({
            "start": points[index],
            "end": points[index + 1],
            "start_miles": total_distance,
            "distance_miles": segment_distance,
        })

        total_distance += segment_distance

    if total_distance <= 0:
        raise ValueError("Route must have a positive distance.")

    target_distances = []
    distance = 0.0

    while distance < total_distance:
        target_distances.append(distance)
        distance += interval_miles

    # Always include the route endpoint, even for a partial last segment.
    if not target_distances or target_distances[-1] != total_distance:
        target_distances.append(total_distance)

    checkpoints = []

    for target in target_distances:
        selected_segment = segments[-1]
        fraction = 1.0

        for segment in segments:
            segment_end = (
                segment["start_miles"] + segment["distance_miles"]
            )

            if target <= segment_end:
                selected_segment = segment

                if segment["distance_miles"] > 0:
                    fraction = (
                        target - segment["start_miles"]
                    ) / segment["distance_miles"]
                else:
                    fraction = 0.0

                break

        latitude, longitude = interpolate_coordinate(
            selected_segment["start"],
            selected_segment["end"],
            max(0.0, min(1.0, fraction)),
        )

        checkpoints.append({
            "checkpoint_index": len(checkpoints),
            "distance_miles": round(target, 3),
            "latitude": latitude,
            "longitude": longitude,
        })

    return checkpoints
