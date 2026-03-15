"""Tests for OSS product definition."""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "skill", "scripts"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from conftest import assert_valid_product, assert_valid_module_list
from products.oss import PRODUCT, build_modules


class TestOSSModules(unittest.TestCase):

    def test_product_definition(self):
        assert_valid_product(self, PRODUCT)
        self.assertEqual(PRODUCT["code"], "oss")
        self.assertEqual(PRODUCT["category"], "storage")

    def test_build_modules(self):
        params = {"storage_class": "Standard", "capacity": 500}
        modules = build_modules(params)
        assert_valid_module_list(self, modules)
        self.assertEqual(len(modules), 1)
        self.assertIn("Capacity:500", modules[0]["config"])
        self.assertIn("StorageClass:Standard", modules[0]["config"])

    def test_format_summary(self):
        from products.oss import format_summary
        summary = format_summary({"storage_class": "Standard", "capacity": 500})
        self.assertIn("存储类型", summary)
        self.assertIn("容量", summary)


if __name__ == "__main__":
    unittest.main()
