
"""Orchestrate routing, checkpoints, weather, and safety ranking."""

from datetime import datetime, timezone

from planner.services.checkpoint_evaluator import evaluate_checkpoint
from planner.services.checkpoints import sample_route_checkpoints
from planner.services.geocoding import geocode_us_location
from planner.services.geometry import simplify_coordinates
from planner.services.route_ranking import rank_routes
from planner.services.routing import get_routes
from planner.services.timing import add_checkpoint_arrival_times
from planner.services.weather import get_weather_forecasts, WeatherServiceError
from planner.services.weather_matching import match_weather_to_arrival


METERS_PER_MILE = 1609.344
MILLISECONDS_PER_SECOND = 1000

# Keep requests reasonably small for URL length and response handling.
WEATHER_BATCH_SIZE = 20
MAX_FORECAST_DAYS = 16


def plan_weather_aware_route(
    origin: str,
    destination: str,
    departure_time: datetime,
    truck_load_lbs: float,
    checkpoint_interval_miles: int = 25,
) -> dict:
    """Build, evaluate, and rank weather-aware route alternatives."""

    if departure_time.utcoffset() is None:
        raise ValueError("Departure time must include a timezone.")

    if truck_load_lbs <= 0:
        raise ValueError("Truck load must be greater than zero.")

    if checkpoint_interval_miles not in {10, 25, 50}:
        raise ValueError(
            "Checkpoint interval must be 10, 25, or 50 miles."
        )

    departure_utc = departure_time.astimezone(timezone.utc)
    now_utc = datetime.now(timezone.utc)

    if departure_utc < now_utc:
        raise ValueError("Departure time must be in the future.")

    # Step 1: Convert location names into coordinates.
    origin_result = geocode_us_location(origin)
    destination_result = geocode_us_location(destination)

    # Step 2: Retrieve available route alternatives.
    routing_result = get_routes(
        origin_result["latitude"],
        origin_result["longitude"],
        destination_result["latitude"],
        destination_result["longitude"],
        alternatives=2,
    )

    if not routing_result.get("routes"):
        raise ValueError("The routing provider returned no routes.")

    # Step 3: Generate checkpoints and estimated arrival times.
    prepared_routes = []
    weather_tasks = []

    for route in routing_result["routes"]:
        distance_miles = (
            float(route["distance_meters"]) / METERS_PER_MILE
        )
        duration_seconds = (
            float(route["duration_milliseconds"])
            / MILLISECONDS_PER_SECOND
        )

        if distance_miles <= 0:
            raise ValueError(
                f"Route {route.get('route_id')} has no positive distance."
            )

        # IMPORTANT: Generate checkpoints using the original,
        # full-resolution route coordinates.
        original_coordinates = route["geometry"]["coordinates"]

        checkpoints = sample_route_checkpoints(
            original_coordinates,
            interval_miles=checkpoint_interval_miles,
        )

        timed_checkpoints = add_checkpoint_arrival_times(
            checkpoints,
            departure_utc,
            distance_miles,
            duration_seconds,
        )

        # Simplify only the geometry sent to the frontend.
        # Weather checkpoints above still use the original coordinates.
        simplified_geometry = {
            **route["geometry"],
            "coordinates": simplify_coordinates(
                original_coordinates,
                tolerance_meters=100.0,
            ),
        }

        prepared_routes.append({
            **route,
            "geometry": simplified_geometry,
            "distance_miles": distance_miles,
            "duration_seconds": duration_seconds,
            "checkpoints": timed_checkpoints,
        })

        for checkpoint_index, checkpoint in enumerate(timed_checkpoints):
            arrival = datetime.fromisoformat(
                checkpoint["arrival_time"].replace("Z", "+00:00")
            )

            days_until_arrival = max(
                1,
                (arrival.date() - now_utc.date()).days + 1,
            )

            if days_until_arrival > MAX_FORECAST_DAYS:
                raise WeatherServiceError(
                    "A checkpoint arrival falls outside the supported "
                    "16-day weather forecast horizon."
                )

            weather_tasks.append({
                "route_index": len(prepared_routes) - 1,
                "checkpoint_index": checkpoint_index,
                "latitude": checkpoint["latitude"],
                "longitude": checkpoint["longitude"],
                "arrival_time": checkpoint["arrival_time"],
                "forecast_days": days_until_arrival,
            })

    # Step 4: Request weather in batches instead of one request
    # for every checkpoint.
    for batch_start in range(0, len(weather_tasks), WEATHER_BATCH_SIZE):
        batch = weather_tasks[
            batch_start:batch_start + WEATHER_BATCH_SIZE
        ]

        # All locations in this batch use the longest required horizon,
        # so each forecast covers every arrival in the batch.
        batch_forecast_days = max(
            task["forecast_days"] for task in batch
        )

        locations = [
            (task["latitude"], task["longitude"])
            for task in batch
        ]

        forecasts = get_weather_forecasts(
            locations,
            forecast_days=batch_forecast_days,
        )

        if len(forecasts) != len(batch):
            raise WeatherServiceError(
                "Weather forecast count did not match checkpoint count."
            )

        # Step 5: Match forecasts to arrivals and evaluate safety.
        for task, forecast in zip(batch, forecasts):
            weather = match_weather_to_arrival(
                forecast["hourly"],
                task["arrival_time"],
            )

            route = prepared_routes[task["route_index"]]
            checkpoint = route["checkpoints"][task["checkpoint_index"]]

            evaluated_checkpoint = evaluate_checkpoint(
                checkpoint,
                weather,
                truck_load_lbs,
            )

            route["checkpoints"][task["checkpoint_index"]] = (
                evaluated_checkpoint
            )

    # Step 6: Rank routes using the existing safety-first ranking rules.
    ranking = rank_routes(prepared_routes)

    return {
        "status": "success",
        "origin": origin_result,
        "destination": destination_result,
        "departure_time": departure_utc.isoformat(),
        "truck_load_lbs": truck_load_lbs,
        "routing_provider": routing_result["provider"],
        "weather_provider": "Open-Meteo",
        "checkpoint_interval_miles": checkpoint_interval_miles,
        "routing_profile": "car",
        "truck_specific_routing": False,
        "limitations": [
            "The routing provider uses a car profile, not a "
            "truck-specific routing profile.",
            "Checkpoint distances and arrival times are estimates.",
            "Weather forecasts are hourly and may not represent "
            "conditions between checkpoints.",
        ],
        **ranking,
    }
