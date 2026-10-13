
from django.test import SimpleTestCase

from planner.services.geometry import simplify_coordinates


class SimplifyCoordinatesTests(SimpleTestCase):
    def test_preserves_route_start_and_end(self):
        coordinates = [
            [-74.0, 40.0],
            [-73.99, 40.001],
            [-73.98, 40.002],
        ]

        result = simplify_coordinates(coordinates)

        self.assertEqual(result[0], coordinates[0])
        self.assertEqual(result[-1], coordinates[-1])

    def test_reduces_points_on_a_straight_route(self):
        coordinates = [
            [-74.0 + index * 0.0001, 40.0]
            for index in range(101)
        ]

        result = simplify_coordinates(coordinates)

        self.assertLess(len(result), len(coordinates))
        self.assertEqual(result[0], coordinates[0])
        self.assertEqual(result[-1], coordinates[-1])

    def test_preserves_an_important_route_bend(self):
        coordinates = [
            [-74.0, 40.0],
            [-73.99, 40.0],
            [-73.98, 40.01],
            [-73.97, 40.0],
        ]

        result = simplify_coordinates(
            coordinates,
            tolerance_meters=100.0,
        )

        self.assertIn(coordinates[2], result)

    def test_rejects_zero_or_negative_tolerance(self):
        coordinates = [
            [-74.0, 40.0],
            [-73.99, 40.01],
            [-73.98, 40.02],
        ]

        for tolerance in (0, -1):
            with self.subTest(tolerance=tolerance):
                with self.assertRaises(ValueError):
                    simplify_coordinates(
                        coordinates,
                        tolerance_meters=tolerance,
                    )
