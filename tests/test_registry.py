"""Tests for the product registry and auto-discovery mechanism."""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skill", "scripts"))

from framework.registry import discover_products, get_product, list_products, list_products_by_category, get_all_codes


class TestRegistry(unittest.TestCase):
    """Unit tests for registry.py"""

    def test_discover_products(self):
        """All 6 base products should be discovered."""
        discover_products()
        codes = get_all_codes()
        self.assertGreaterEqual(len(codes), 6)
        for expected in ["ecs", "rds", "slb", "eip", "oss", "cdn"]:
            self.assertIn(expected, codes, f"Product '{expected}' not discovered")

    def test_get_product_found(self):
        """get_product should return a valid PRODUCT dict."""
        product = get_product("ecs")
        self.assertIsNotNone(product)
        self.assertEqual(product["code"], "ecs")
        self.assertEqual(product["name"], "ECS")

    def test_get_product_not_found(self):
        """get_product should return None for unknown codes."""
        self.assertIsNone(get_product("nonexistent_product_xyz"))

    def test_list_products(self):
        """list_products should return a list of dicts."""
        products = list_products()
        self.assertIsInstance(products, list)
        self.assertGreater(len(products), 0)
        for p in products:
            self.assertIsInstance(p, dict)
            self.assertIn("code", p)

    def test_list_products_by_category(self):
        """Should filter products by category."""
        db_products = list_products_by_category("database")
        self.assertTrue(any(p["code"] == "rds" for p in db_products))

        network_products = list_products_by_category("network")
        self.assertTrue(any(p["code"] == "slb" for p in network_products))
        self.assertTrue(any(p["code"] == "eip" for p in network_products))

    def test_product_structure_complete(self):
        """Every registered product should have all required fields."""
        required = {"code", "name", "display_name", "params", "build_modules", "format_summary"}
        for product in list_products():
            for field in required:
                self.assertIn(field, product,
                              f"Product '{product.get('code', '?')}' missing field '{field}'")


if __name__ == "__main__":
    unittest.main()
