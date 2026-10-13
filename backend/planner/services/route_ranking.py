
from planner.services.risk import (
    RISK_LEVELS,
    average_risk,
    risk_miles_by_category,
)


def rank_routes(routes: list[dict]) -> dict:
    """
    Rank routes by safety first, using the project's exact priority:
    1. Fewest Severe-risk miles
    2. Fewest High-risk miles
    3. Lowest average risk
    4. Shortest travel time

    A route containing any No Travel checkpoint is never recommended.
    """

    if not routes:
        raise ValueError("At least one route is required.")

    evaluated_routes = []

    for route in routes:
        route_id = route.get("route_id")

        if not route_id:
            raise ValueError("Every route must have a route_id.")

        distance = float(route["distance_miles"])
        duration = float(route["duration_seconds"])
        checkpoints = route.get("checkpoints", [])

        if distance < 0:
            raise ValueError(f"{route_id}: distance cannot be negative.")

        if duration < 0:
            raise ValueError(f"{route_id}: duration cannot be negative.")

        if not checkpoints:
            raise ValueError(f"{route_id}: checkpoints are required.")

        risk_miles = risk_miles_by_category(checkpoints, distance)

        risk_levels = [
            checkpoint["final_risk"]
            for checkpoint in checkpoints
        ]

        for level in risk_levels:
            if level not in RISK_LEVELS:
                raise ValueError(
                    f"{route_id}: unknown risk level '{level}'."
                )

        has_no_travel = "No Travel" in risk_levels

        evaluated_routes.append({
            **route,
            "risk_miles": risk_miles,
            "average_risk": average_risk(risk_levels),
            "has_no_travel": has_no_travel,
        })

    # Never consider a route containing No Travel as a safe recommendation.
    eligible_routes = [
        route for route in evaluated_routes
        if not route["has_no_travel"]
    ]

    def ranking_key(route: dict) -> tuple:
        return (
            route["risk_miles"]["Severe"],
            route["risk_miles"]["High"],
            route["average_risk"],
            route["duration_seconds"],
        )

    evaluated_routes.sort(key=ranking_key)
    eligible_routes.sort(key=ranking_key)

    recommended_route_id = (
        eligible_routes[0]["route_id"]
        if eligible_routes
        else None
    )

    return {
        "routes": evaluated_routes,
        "recommended_route_id": recommended_route_id,
        "safety_status": (
            "safe_route_available"
            if recommended_route_id
            else "no_safe_route_available"
        ),
    }
