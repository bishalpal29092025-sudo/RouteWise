
from django.test import SimpleTestCase

from planner.services.risk import (
    classify_wind,
    classify_rain,
    classify_snow,
    calculate_checkpoint_risk,
)


class WindRiskTests(SimpleTestCase):
    def test_wind_thresholds(self):
        self.assertEqual(classify_wind(24.9), "Low")
        self.assertEqual(classify_wind(25), "Moderate")
        self.assertEqual(classify_wind(35), "High")
        self.assertEqual(classify_wind(45), "Severe")
        self.assertEqual(classify_wind(55), "No Travel")


class RainRiskTests(SimpleTestCase):
    def test_rain_thresholds(self):
        self.assertEqual(classify_rain(0.09), "Low")
        self.assertEqual(classify_rain(0.10), "Moderate")
        self.assertEqual(classify_rain(0.25), "High")
        self.assertEqual(classify_rain(0.50), "Severe")
        self.assertEqual(classify_rain(1.00), "Severe")
        self.assertEqual(classify_rain(1.01), "No Travel")


class SnowRiskTests(SimpleTestCase):
    def test_snow_thresholds(self):
        self.assertEqual(classify_snow(0.49), "Low")
        self.assertEqual(classify_snow(0.50), "Moderate")
        self.assertEqual(classify_snow(1.00), "High")
        self.assertEqual(classify_snow(2.00), "Severe")
        self.assertEqual(classify_snow(3.00), "Severe")
        self.assertEqual(classify_snow(3.01), "No Travel")


class TruckLoadRiskTests(SimpleTestCase):
    def test_heavy_load_increases_risk_in_high_wind(self):
        result = calculate_checkpoint_risk(
            wind_mph=40,
            rain_inches_per_hour=0,
            snow_inches_per_hour=0,
            truck_load_lbs=45000,
        )

        self.assertEqual(result["wind_risk"], "High")
        self.assertEqual(result["load_risk"], "Severe")
        self.assertEqual(result["final_risk"], "Severe")

    def test_heavy_load_and_severe_wind_can_make_travel_unsafe(self):
        result = calculate_checkpoint_risk(
            wind_mph=46,
            rain_inches_per_hour=0,
            snow_inches_per_hour=0,
            truck_load_lbs=35000,
        )

        self.assertEqual(result["final_risk"], "No Travel")
