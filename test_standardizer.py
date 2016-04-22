from __future__ import absolute_import
import unittest
import standardizer


class TestStandardizer(unittest.TestCase):
    def test_linear_mapping(self):
        mapped_value = standardizer.Standardizer.get_mapped_value(
            normalized_value=1.0, min_value=0.0, max_value=3.0, skew_factor=1.0
        )
        self.assertAlmostEqual(mapped_value, 3.0)

        mapped_value = standardizer.Standardizer.get_mapped_value(
            normalized_value=0.5, min_value=0.0, max_value=3.0, skew_factor=1.0
        )
        self.assertAlmostEqual(mapped_value, 1.5)

        mapped_value = standardizer.Standardizer.get_mapped_value(
            normalized_value=0.0, min_value=0.0, max_value=3.0, skew_factor=1.0
        )
        self.assertAlmostEqual(mapped_value, 0.0)

    def test_skewed_mapping(self):
        mapped_value = standardizer.Standardizer.get_mapped_value(
            normalized_value=1.0, min_value=0.0, max_value=3.0, skew_factor=0.3
        )
        self.assertAlmostEqual(mapped_value, 3.0)

        mapped_value = standardizer.Standardizer.get_mapped_value(
            normalized_value=0.5, min_value=0.0, max_value=3.0, skew_factor=0.3
        )
        self.assertLess(mapped_value, 1.5)
        self.assertGreater(mapped_value, 0.0)

        mapped_value = standardizer.Standardizer.get_mapped_value(
            normalized_value=0.013, min_value=0.0, max_value=3.0, skew_factor=0.3
        )
        self.assertLess(mapped_value, 0.013)
        self.assertGreater(mapped_value, 0.0)

        mapped_value = standardizer.Standardizer.get_mapped_value(
            normalized_value=0.0, min_value=0.0, max_value=3.0, skew_factor=0.3
        )
        self.assertAlmostEqual(mapped_value, 0.0)


if __name__ == '__main__':
    unittest.main()
