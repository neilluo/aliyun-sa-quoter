"""Tests for SLB product definition."""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "skill", "scripts"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from conftest import (
    skip_without_credentials, create_test_client,
    assert_valid_product, assert_valid_module_list,
)
from products.slb import PRODUCT, build_modules, validate
from framework.base import resolve_product_type


class TestSLBModules(unittest.TestCase):

    def test_product_definition(self):
        assert_valid_product(self, PRODUCT)
        self.assertEqual(PRODUCT["code"], "slb")
        self.assertEqual(PRODUCT["category"], "network")

    def test_product_type(self):
        self.assertEqual(resolve_product_type(PRODUCT, {}), "slb")

    def test_build_modules_by_traffic(self):
        params = {"spec": "slb.s3.large", "internet_charge_type": 1}
        modules = build_modules(params)
        assert_valid_module_list(self, modules)
        self.assertEqual(len(modules), 3)

    def test_build_modules_by_bandwidth(self):
        params = {"spec": "slb.s2.medium", "internet_charge_type": 0, "bandwidth": 5000}
        modules = build_modules(params)
        self.assertEqual(len(modules), 4)
        codes = [m["module_code"] for m in modules]
        self.assertIn("Bandwidth", codes)

    def test_validate_bandwidth_required(self):
        errors = validate({"internet_charge_type": 0, "bandwidth": 0})
        self.assertTrue(len(errors) > 0)

    def test_validate_passes(self):
        errors = validate({"internet_charge_type": 1})
        self.assertEqual(len(errors), 0)


class TestSLBAPI(unittest.TestCase):

    @skip_without_credentials
    def test_subscription_price(self):
        import bss_client
        client = create_test_client()
        modules = build_modules({"spec": "slb.s3.large", "internet_charge_type": 1})
        result = bss_client.get_subscription_price(
            client, "slb", modules, region="cn-hangzhou", duration=1, product_type="slb",
        )
        self.assertIsNotNone(result)
        self.assertGreater(float(result["trade_amount"]), 0)


if __name__ == "__main__":
    unittest.main()
