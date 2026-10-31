import unittest
from jal_saarthi.engine import build_daily_plan, summarize_plan, assess_drought_risk

class WaterEngineTests(unittest.TestCase):
    def setUp(self):
        self.daily = {
            "time": ["2026-11-01", "2026-11-02"],
            "temperature_2m_max": [31, 32],
            "temperature_2m_min": [20, 21],
            "precipitation_sum": [0, 10],
            "et0_fao_evapotranspiration": [5, 5],
        }

    def test_daily_rows_and_nonnegative_irrigation(self):
        df = build_daily_plan(self.daily, "Wheat", "Loamy", "Vegetative", 1, 0.75)
        self.assertEqual(len(df), 2)
        self.assertTrue((df["Net irrigation (mm)"] >= 0).all())

    def test_volume_scales_with_area(self):
        one = build_daily_plan(self.daily, "Wheat", "Loamy", "Vegetative", 1, 0.75)
        two = build_daily_plan(self.daily, "Wheat", "Loamy", "Vegetative", 2, 0.75)
        self.assertAlmostEqual(two["Estimated water volume (m³)"].sum(),
                               2 * one["Estimated water volume (m³)"].sum(), places=1)

    def test_lower_efficiency_needs_higher_gross_depth(self):
        good = build_daily_plan(self.daily, "Wheat", "Loamy", "Vegetative", 1, 0.9)
        low = build_daily_plan(self.daily, "Wheat", "Loamy", "Vegetative", 1, 0.6)
        self.assertGreater(low["Gross irrigation (mm)"].sum(),
                           good["Gross irrigation (mm)"].sum())

    def test_summary_and_risk(self):
        df = build_daily_plan(self.daily, "Wheat", "Loamy", "Vegetative", 1, 0.75)
        summary = summarize_plan(df, 1)
        self.assertGreaterEqual(summary["gross_volume_m3"], 0)
        self.assertIn(assess_drought_risk(df)[0], ["Low", "Moderate", "High"])

if __name__ == "__main__":
    unittest.main()
