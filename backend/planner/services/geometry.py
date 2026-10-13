
"""Utilities for reducing route-map geometry size."""

from math import cos, radians, sqrt


def simplify_coordinates(
    coordinates: list[list[float]],
    tolerance_meters: float = 100.0,
) -> list[list[float]]:
    """Reduce map coordinates while approximately preserving route shape.

    Coordinates use GeoJSON order: [longitude, latitude].
    The first and last coordinates are always preserved.
    """
    if len(coordinates) <= 2:
        return coordinates.copy()

    if tolerance_meters <= 0:
        raise ValueError("Tolerance must be greater than zero.")

    mean_latitude = sum(point[1] for point in coordinates) / len(coordinates)
    meters_per_degree_latitude = 111_320.0
    meters_per_degree_longitude = (
        111_320.0 * cos(radians(mean_latitude))
    )

    def perpendicular_distance(
        point: list[float],
        start: list[float],
        end: list[float],
    ) -> float:
        """Approximate the point's distance from a line segment in meters."""
        px = point[0] * meters_per_degree_longitude
        py = point[1] * meters_per_degree_latitude
        sx = start[0] * meters_per_degree_longitude
        sy = start[1] * meters_per_degree_latitude
        ex = end[0] * meters_per_degree_longitude
        ey = end[1] * meters_per_degree_latitude

        dx = ex - sx
        dy = ey - sy

        if dx == 0 and dy == 0:
            return sqrt((px - sx) ** 2 + (py - sy) ** 2)

        fraction = max(
            0.0,
            min(1.0, ((px - sx) * dx + (py - sy) * dy)
                / (dx * dx + dy * dy)),
        )

        closest_x = sx + fraction * dx
        closest_y = sy + fraction * dy

        return sqrt(
            (px - closest_x) ** 2 + (py - closest_y) ** 2
        )

    def simplify_section(
        start_index: int,
        end_index: int,
        keep: set[int],
    ) -> None:
        """Keep important bends using the Douglas–Peucker method."""
        maximum_distance = 0.0
        furthest_index = None

        for index in range(start_index + 1, end_index):
            distance = perpendicular_distance(
                coordinates[index],
                coordinates[start_index],
                coordinates[end_index],
            )

            if distance > maximum_distance:
                maximum_distance = distance
                furthest_index = index

        if furthest_index is not None and maximum_distance > tolerance_meters:
            keep.add(furthest_index)
            simplify_section(start_index, furthest_index, keep)
            simplify_section(furthest_index, end_index, keep)

    kept_indices = {0, len(coordinates) - 1}
    simplify_section(0, len(coordinates) - 1, kept_indices)

    return [
        coordinates[index]
        for index in sorted(kept_indices)
    ]
