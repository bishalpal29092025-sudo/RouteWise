
import os
import requests


GRAPHHOPPER_GEOCODING_URL = (
    "https://graphhopper.com/api/1/geocode"
)
REQUEST_TIMEOUT_SECONDS = 15


class GeocodingServiceError(Exception):
    """Raised when a location cannot be geocoded."""


def geocode_us_location(location: str) -> dict:
    """
    Resolve a US location, preferring results whose city or name
    matches the requested location.
    """

    api_key = os.getenv("GRAPHHOPPER_API_KEY")

    if not api_key:
        raise GeocodingServiceError(
            "The GraphHopper API key is missing."
        )

    if not location or not location.strip():
        raise ValueError("Location cannot be empty.")

    query = location.strip()

    params = [
        ("q", query),
        ("limit", 10),
        ("key", api_key),
    ]

    try:
        response = requests.get(
            GRAPHHOPPER_GEOCODING_URL,
            params=params,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()

    except requests.Timeout as exc:
        raise GeocodingServiceError(
            "The location lookup timed out."
        ) from exc

    except requests.RequestException as exc:
        raise GeocodingServiceError(
            "Unable to look up this location."
        ) from exc

    except ValueError as exc:
        raise GeocodingServiceError(
            "The geocoding provider returned invalid JSON."
        ) from exc

    # Extract a city-like phrase from common US address formats.
    parts = [part.strip() for part in query.split(",") if part.strip()]
    requested_city = parts[0].casefold() if parts else ""

    hits = data.get("hits", [])
    candidates = []

    for hit in hits:
        country_code = (
            hit.get("countrycode") or ""
        ).strip().casefold()

        if country_code != "us":
            continue

        city = (hit.get("city") or "").strip()
        name = (hit.get("name") or "").strip()

        # Prefer exact city matches over businesses or unrelated places.
        if city.casefold() == requested_city:
            score = 0
        elif name.casefold() == requested_city:
            score = 1
        else:
            continue

        point = hit.get("point") or {}
        latitude = point.get("lat")
        longitude = point.get("lng")

        if latitude is None or longitude is None:
            continue

        candidates.append((
            score,
            {
                "location": city or name,
                "latitude": float(latitude),
                "longitude": float(longitude),
                "country": hit.get("country"),
            },
        ))

    if not candidates:
        raise GeocodingServiceError(
            "No suitable US city match was found. "
            "Try including the city, state, and country."
        )

    candidates.sort(key=lambda candidate: candidate[0])
    return candidates[0][1]
