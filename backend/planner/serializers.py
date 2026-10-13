
from decimal import Decimal

from rest_framework import serializers


class RoutePlanRequestSerializer(serializers.Serializer):
    """
    Validate inputs for the RouteWise truck route planner.

    Required inputs:
    - origin: Starting location in the USA.
    - destination: Ending location in the USA.
    - departure_time: ISO 8601 date and time.
    - truck_load_lbs: Cargo weight in pounds.
    """

    origin = serializers.CharField(
        required=True,
        max_length=200,
        trim_whitespace=True,
    )

    destination = serializers.CharField(
        required=True,
        max_length=200,
        trim_whitespace=True,
    )

    departure_time = serializers.DateTimeField(
        required=True,
    )

    truck_load_lbs = serializers.DecimalField(
        required=True,
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("0.01"),
    )

    def validate_origin(self, value):
        """Reject an empty origin."""
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Origin cannot be empty."
            )

        return value

    def validate_destination(self, value):
        """Reject an empty destination."""
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Destination cannot be empty."
            )

        return value

    def validate(self, attrs):
        """Ensure the journey starts and ends at different locations."""
        origin = attrs["origin"]
        destination = attrs["destination"]

        if origin.casefold() == destination.casefold():
            raise serializers.ValidationError({
                "destination": (
                    "Origin and destination must be different."
                )
            })

        return attrs
