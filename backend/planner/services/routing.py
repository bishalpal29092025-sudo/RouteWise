
import os

import requests


GRAPHHOPPER_API_URL = "https://graphhopper.com/api/1/route"
REQUEST_TIMEOUT_SECONDS = 20


class RoutingServiceError(Exception):
    """Raised when the routing provider cannot return a usable route."""


def get_routes(
    origin_lat: float,
    origin_lon: float,
    destination_lat: float,
    destination_lon: float,
    alternatives: int = 2,
) -> dict:
    """
    Request road routes from GraphHopper.

    Coordinates must be supplied as latitude and longitude.
    The caller must geocode and validate the US locations first.
    """

    api_key = os.getenv("GRAPHHOPPER_API_KEY")

    if not api_key:
        raise RoutingServiceError(
            "GraphHopper API key is missing from the environment."
        )

    if not 0 <= alternatives <= 2:
        raise ValueError(
            "alternatives must be between 0 and 2."
        )

    params = [
        ("point", f"{origin_lat},{origin_lon}"),
        ("point", f"{destination_lat},{destination_lon}"),
        ("profile", "car"),
        ("points_encoded", "false"),
        ("instructions", "false"),
        ("key", api_key),
    ]

    if alternatives:
        params.append(("algorithm", "alternative_route"))
        params.append(("alternative_route.max_paths", alternatives + 1))

    try:
        response = requests.get(
            GRAPHHOPPER_API_URL,
            params=params,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()

    except requests.Timeout as exc:
        raise RoutingServiceError(
            "GraphHopper request timed out."
        ) from exc

    except requests.RequestException as exc:
        raise RoutingServiceError(
            "Unable to retrieve routes from GraphHopper."
        ) from exc

    except ValueError as exc:
        raise RoutingServiceError(
            "GraphHopper returned invalid JSON."
        ) from exc

    paths = data.get("paths", [])

    if not paths:
        provider_message = data.get(
            "message",
            "No route was returned for these locations.",
        )
        raise RoutingServiceError(provider_message)

    routes = []

    for index, path in enumerate(paths):
        points = path.get("points", {}).get("coordinates", [])

        if len(points) < 2:
            continue

        routes.append(
            {
                "route_id": f"route-{index + 1}",
                "distance_meters": path.get("distance"),
                "duration_milliseconds": path.get("time"),
                "geometry": {
                    "type": "LineString",
                    "coordinates": points,
                },
            }
        )

    if not routes:
        raise RoutingServiceError(
            "GraphHopper returned no usable route geometry."
        )

    return {
        "provider": "GraphHopper",
        "routes": routes,
    }
