"""Tests for CDN product definition."""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "skill", "scripts"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from conftest import assert_valid_product, assert_valid_module_list
from products.cdn import PRODUCT, build_modules


class TestCDNModules(unittest.TestCase):

    def test_product_definition(self):
        assert_valid_product(self, PRODUCT)
        self.assertEqual(PRODUCT["code"], "cdn")
        self.assertEqual(PRODUCT["category"], "cdn_security")

    def test_build_modules(self):
        params = {"traffic_package": 1000}
        modules = build_modules(params)
        assert_valid_module_list(self, modules)
        self.assertEqual(len(modules), 1)
        self.assertIn("TrafficPackage:1000", modules[0]["config"])

    def test_format_summary(self):
        from products.cdn import format_summary
        summary = format_summary({"traffic_package": 1000})
        self.assertIn("流量包", summary)


if __name__ == "__main__":
    unittest.main()
