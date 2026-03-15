"""Tests for ECS product definition."""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "skill", "scripts"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from conftest import (
    skip_without_credentials, create_test_client,
    assert_valid_product, assert_valid_module_list,
)
from products.ecs import PRODUCT, build_modules, validate
from products._base import resolve_product_type


class TestECSModules(unittest.TestCase):
    """Unit tests for ECS product (no credentials needed)."""

    def test_product_definition(self):
        """PRODUCT dict should have complete structure."""
        assert_valid_product(self, PRODUCT)
        self.assertEqual(PRODUCT["code"], "ecs")
        self.assertEqual(PRODUCT["category"], "compute")

    def test_product_type_is_none(self):
        """ECS should not require ProductType."""
        pt = resolve_product_type(PRODUCT, {})
        self.assertIsNone(pt)

    def test_build_modules_basic(self):
        """Should build correct modules for a basic ECS config."""
        params = {"instance_type": "ecs.g7.xlarge"}
        modules = build_modules(params)
        assert_valid_module_list(self, modules)
        # Should have InstanceType + SystemDisk (no DataDisk, no bandwidth)
        self.assertEqual(len(modules), 2)
        codes = [m["module_code"] for m in modules]
        self.assertIn("InstanceType", codes)
        self.assertIn("SystemDisk", codes)

    def test_build_modules_with_data_disk(self):
        """Should include DataDisk module when data_disk_size > 0."""
        params = {
            "instance_type": "ecs.g7.xlarge",
            "data_disk_size": 200,
            "data_disk_category": "cloud_essd",
        }
        modules = build_modules(params)
        codes = [m["module_code"] for m in modules]
        self.assertIn("DataDisk", codes)

    def test_build_modules_with_bandwidth(self):
        """Should include InternetMaxBandwidthOut when bandwidth > 0."""
        params = {
            "instance_type": "ecs.g7.xlarge",
            "internet_bandwidth": 5,
        }
        modules = build_modules(params)
        codes = [m["module_code"] for m in modules]
        self.assertIn("InternetMaxBandwidthOut", codes)

    def test_build_modules_config_format(self):
        """Config strings should have correct format."""
        params = {"instance_type": "ecs.c7.xlarge", "image_os": "linux"}
        modules = build_modules(params)
        it_module = next(m for m in modules if m["module_code"] == "InstanceType")
        self.assertIn("InstanceType:ecs.c7.xlarge", it_module["config"])
        self.assertIn("InstanceTypeFamily:ecs.c7", it_module["config"])
        self.assertIn("ImageOs:linux", it_module["config"])

    def test_validate_small_system_disk(self):
        """Should reject system disk < 20GB."""
        errors = validate({"instance_type": "ecs.g7.xlarge", "system_disk_size": 10})
        self.assertTrue(any("20GB" in e for e in errors))

    def test_validate_passes(self):
        """Normal params should pass validation."""
        errors = validate({"instance_type": "ecs.g7.xlarge", "system_disk_size": 40})
        self.assertEqual(len(errors), 0)

    def test_format_summary(self):
        """format_summary should return meaningful dict."""
        from products.ecs import format_summary
        summary = format_summary({"instance_type": "ecs.g7.xlarge", "image_os": "linux"})
        self.assertIn("实例规格", summary)
        self.assertEqual(summary["实例规格"], "ecs.g7.xlarge")


class TestECSAPI(unittest.TestCase):
    """Integration tests for ECS (requires credentials)."""

    @skip_without_credentials
    def test_subscription_price(self):
        """Query ECS subscription price via real API."""
        import bss_client
        client = create_test_client()
        params = {"instance_type": "ecs.g7.xlarge", "image_os": "linux",
                  "system_disk_category": "cloud_essd", "system_disk_size": 40}
        modules = build_modules(params)
        result = bss_client.get_subscription_price(
            client, "ecs", modules, region="cn-hangzhou", duration=1,
            product_type=None,
        )
        self.assertIsNotNone(result)
        self.assertGreater(float(result["trade_amount"]), 0)

    @skip_without_credentials
    def test_payasyougo_price(self):
        """Query ECS pay-as-you-go price via real API."""
        import bss_client
        client = create_test_client()
        params = {"instance_type": "ecs.g7.xlarge", "image_os": "linux",
                  "system_disk_category": "cloud_essd", "system_disk_size": 40}
        modules = build_modules(params)
        result = bss_client.get_pay_as_you_go_price(
            client, "ecs", modules, region="cn-hangzhou",
            product_type=None,
        )
        self.assertIsNotNone(result)
        self.assertGreater(float(result["trade_amount"]), 0)


if __name__ == "__main__":
    unittest.main()
