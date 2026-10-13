
"""API endpoints for RouteWise."""

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from planner.serializers import RoutePlanRequestSerializer
from planner.services.geocoding import GeocodingServiceError
from planner.services.routing import RoutingServiceError
from planner.services.route_planner import plan_weather_aware_route
from planner.services.weather import WeatherServiceError


@api_view(["GET"])
def health_check(request):
    """Confirm that the RouteWise backend is running."""
    return Response(
        {
            "status": "healthy",
            "message": "RouteWise backend is running.",
            "service": "Weather-Aware Truck Routing API",
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
def route_plan(request):
    """Validate a request and generate a weather-aware route plan."""

    serializer = RoutePlanRequestSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            {
                "status": "error",
                "message": "Invalid route-planning request.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    validated = serializer.validated_data

    try:
        result = plan_weather_aware_route(
            origin=validated["origin"],
            destination=validated["destination"],
            departure_time=validated["departure_time"],
            truck_load_lbs=float(validated["truck_load_lbs"]),
        )

    except (GeocodingServiceError, RoutingServiceError,
            WeatherServiceError) as exc:
        return Response(
            {
                "status": "error",
                "message": str(exc),
                "routing_status": "failed",
                "weather_status": "unavailable",
            },
            status=status.HTTP_502_BAD_GATEWAY,
        )

    except ValueError as exc:
        return Response(
            {
                "status": "error",
                "message": str(exc),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(result, status=status.HTTP_200_OK)
