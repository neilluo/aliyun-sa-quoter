"""Tests for EIP product definition."""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "skill", "scripts"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from conftest import (
    skip_without_credentials, create_test_client,
    assert_valid_product, assert_valid_module_list,
)
from products.eip import PRODUCT, build_modules
from products._base import resolve_product_type


class TestEIPModules(unittest.TestCase):

    def test_product_definition(self):
        assert_valid_product(self, PRODUCT)
        self.assertEqual(PRODUCT["code"], "eip")

    def test_product_type(self):
        self.assertEqual(resolve_product_type(PRODUCT, {}), "eip")

    def test_build_modules(self):
        params = {"bandwidth": 5, "internet_charge_type": "PayByTraffic"}
        modules = build_modules(params)
        assert_valid_module_list(self, modules)
        self.assertEqual(len(modules), 2)
        codes = [m["module_code"] for m in modules]
        self.assertIn("Bindwidth", codes)
        self.assertIn("InternetChargeType", codes)

    def test_build_modules_config(self):
        params = {"bandwidth": 10, "internet_charge_type": "PayByBandwidth"}
        modules = build_modules(params)
        bw = next(m for m in modules if m["module_code"] == "Bindwidth")
        self.assertEqual(bw["config"], "Bindwidth:10")


class TestEIPAPI(unittest.TestCase):

    @skip_without_credentials
    def test_subscription_price(self):
        import bss_client
        client = create_test_client()
        modules = build_modules({"bandwidth": 5, "internet_charge_type": "PayByTraffic"})
        result = bss_client.get_subscription_price(
            client, "eip", modules, region="cn-hangzhou", duration=1, product_type="eip",
        )
        self.assertIsNotNone(result)
        self.assertGreater(float(result["trade_amount"]), 0)


if __name__ == "__main__":
    unittest.main()
