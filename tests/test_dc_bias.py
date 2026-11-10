import unittest

from dc_bias import compute_dc_bias

REF = dict(vcc=12.0, r1=100_000.0, r2=22_000.0, rc=2_200.0, re=1_000.0,
           beta=100.0, vbe=0.70)


class ReferenceCaseTest(unittest.TestCase):
    def test_reference_operating_point(self):
        r = compute_dc_bias(**REF)
        self.assertAlmostEqual(r.vth, 2.163934, places=5)
        self.assertAlmostEqual(r.rth, 18_032.787, places=2)
        self.assertAlmostEqual(r.ib, 12.2986e-6, delta=1e-9)
        self.assertAlmostEqual(r.ic, 1.229858e-3, delta=1e-8)
        self.assertAlmostEqual(r.ie, 1.242157e-3, delta=1e-8)
        self.assertAlmostEqual(r.ve, 1.242157, places=5)
        self.assertAlmostEqual(r.vb, 1.942157, places=5)
        self.assertAlmostEqual(r.vc, 9.294312, places=5)
        self.assertAlmostEqual(r.vce, 8.052155, places=5)
        self.assertEqual(r.region, "active")
        self.assertEqual(r.warnings, ())


class ValidationTest(unittest.TestCase):
    def test_zero_resistor_rejected(self):
        for key in ("r1", "r2", "rc", "re"):
            with self.subTest(key=key), self.assertRaises(ValueError):
                compute_dc_bias(**{**REF, key: 0.0})

    def test_negative_resistor_rejected(self):
        with self.assertRaises(ValueError):
            compute_dc_bias(**{**REF, "rc": -2_200.0})

    def test_zero_beta_rejected(self):
        with self.assertRaises(ValueError):
            compute_dc_bias(**{**REF, "beta": 0.0})

    def test_zero_vcc_rejected(self):
        with self.assertRaises(ValueError):
            compute_dc_bias(**{**REF, "vcc": 0.0})

    def test_extreme_values_still_compute(self):
        r = compute_dc_bias(**{**REF, "r1": 1e12, "beta": 1e9})
        self.assertTrue(all(isinstance(v, float) for v in (r.vb, r.vce, r.ic)))


class RegionTest(unittest.TestCase):
    def test_cutoff_when_vth_not_above_vbe(self):
        r = compute_dc_bias(**{**REF, "r2": 4_700.0})
        self.assertAlmostEqual(r.vth, 0.5387, places=4)
        self.assertEqual(r.region, "cutoff")
        self.assertEqual(r.ib, 0.0)
        self.assertEqual(r.ic, 0.0)
        self.assertEqual(r.ie, 0.0)
        self.assertAlmostEqual(r.vb, r.vth, places=9)
        self.assertAlmostEqual(r.vce, 12.0 - r.vth, places=9)
        self.assertTrue(r.warnings)
        self.assertTrue(any("Forward-Active" in w for w in r.warnings))

    def test_saturation_reports_unclamped_values(self):
        r = compute_dc_bias(vcc=12.0, r1=47_000.0, r2=10_000.0, rc=4_700.0,
                            re=470.0, beta=150.0, vbe=0.70)
        self.assertEqual(r.region, "saturation")
        self.assertAlmostEqual(r.vce, -1.76549, delta=0.01)
        self.assertLess(r.vce, 0.2)
        self.assertTrue(r.warnings)

    def test_vbe_outside_normal_range_warns_but_computes(self):
        r = compute_dc_bias(**{**REF, "vbe": 0.30})
        self.assertEqual(r.region, "active")
        self.assertTrue(any("VBE" in w for w in r.warnings))
