import unittest

from app import app


class GetFormTest(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_get_index_returns_form(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        body = resp.get_data(as_text=True)
        for field in ("vcc", "r1", "r2", "rc", "re", "beta", "vbe"):
            self.assertIn(f'name="{field}"', body)

    def test_get_index_prefills_reference_values(self):
        body = self.client.get("/").get_data(as_text=True)
        self.assertIn('value="100000"', body)
        self.assertIn("Calculate DC Bias", body)


class CalculateTest(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def post(self, **overrides):
        data = {"vcc": "12", "r1": "100000", "r2": "22000", "rc": "2200",
                "re": "1000", "beta": "100", "vbe": "0.70"}
        data.update(overrides)
        return self.client.post("/calculate", data=data)

    def test_reference_case_renders_results(self):
        resp = self.post()
        self.assertEqual(resp.status_code, 200)
        body = resp.get_data(as_text=True)
        for expected in ("1.942", "1.242", "9.294", "8.052", "1.230", "region-active"):
            self.assertIn(expected, body)

    def test_zero_resistor_shows_error(self):
        resp = self.post(r1="0")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("R1", resp.get_data(as_text=True))

    def test_non_numeric_shows_error_not_crash(self):
        resp = self.post(rc="abc")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("ตัวเลข", resp.get_data(as_text=True))

    def test_comma_and_suffix_rejected(self):
        for bad in ("1,000", "100k"):
            with self.subTest(value=bad):
                resp = self.post(r1=bad)
                self.assertEqual(resp.status_code, 400)

    def test_cutoff_warning_shown(self):
        resp = self.post(r2="4700")
        self.assertEqual(resp.status_code, 200)
        body = resp.get_data(as_text=True)
        self.assertIn("region-cutoff", body)
        self.assertIn("Forward-Active", body)
        self.assertIn("0.000", body)  # IC ถูก clamp เป็น 0 mA

    def test_saturation_warning_shown(self):
        resp = self.client.post("/calculate", data={
            "vcc": "12", "r1": "47000", "r2": "10000", "rc": "4700",
            "re": "470", "beta": "150", "vbe": "0.70"})
        body = resp.get_data(as_text=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("region-saturation", body)


if __name__ == "__main__":
    unittest.main()
