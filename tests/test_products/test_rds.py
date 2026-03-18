"""Tests for RDS product definition."""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "skill", "scripts"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from conftest import (
    skip_without_credentials, create_test_client,
    assert_valid_product, assert_valid_module_list,
)
from products.rds import PRODUCT, build_modules, validate
from framework.base import resolve_product_type


class TestRDSModules(unittest.TestCase):
    """Unit tests for RDS product (no credentials needed)."""

    def test_product_definition(self):
        assert_valid_product(self, PRODUCT)
        self.assertEqual(PRODUCT["code"], "rds")
        self.assertEqual(PRODUCT["category"], "database")

    def test_product_type_dynamic(self):
        """ProductType should vary by series."""
        self.assertEqual(resolve_product_type(PRODUCT, {"series": "HighAvailability"}), "rds")
        self.assertEqual(resolve_product_type(PRODUCT, {"series": "AlwaysOn"}), "rds")
        self.assertEqual(resolve_product_type(PRODUCT, {"series": "Basic"}), "bards")
        # Default (no series) should be "rds"
        self.assertEqual(resolve_product_type(PRODUCT, {}), "rds")

    def test_build_modules(self):
        params = {
            "engine": "mysql", "engine_version": "8.0",
            "series": "HighAvailability", "instance_class": "mysql.n2.medium.2c",
            "storage_type": "local_ssd", "storage_size": 100,
        }
        modules = build_modules(params)
        assert_valid_module_list(self, modules)
        self.assertEqual(len(modules), 7)
        codes = [m["module_code"] for m in modules]
        for expected in ["Engine", "EngineVersion", "Series", "DBInstanceStorageType",
                         "DBInstanceStorage", "DBInstanceClass", "DBNetworkType"]:
            self.assertIn(expected, codes)

    def test_build_modules_config_values(self):
        params = {
            "engine": "postgresql", "engine_version": "14.0",
            "series": "HighAvailability", "instance_class": "pg.n2.medium.2c",
        }
        modules = build_modules(params)
        engine_mod = next(m for m in modules if m["module_code"] == "Engine")
        self.assertEqual(engine_mod["config"], "Engine:postgresql")

    def test_validate_local_ssd_basic_fails(self):
        """local_ssd should only work with HighAvailability."""
        errors = validate({"storage_type": "local_ssd", "series": "Basic", "engine": "mysql"})
        self.assertTrue(any("local_ssd" in e for e in errors))

    def test_validate_local_ssd_ha_passes(self):
        errors = validate({"storage_type": "local_ssd", "series": "HighAvailability", "engine": "mysql", "storage_size": 100})
        self.assertEqual(len(errors), 0)

    def test_validate_storage_size_not_multiple_of_5(self):
        errors = validate({"storage_type": "cloud_essd", "series": "Basic", "engine": "mysql", "storage_size": 103})
        self.assertTrue(any("5 的倍数" in e for e in errors))

    def test_validate_mssql_basic_fails(self):
        errors = validate({"engine": "mssql", "series": "Basic", "storage_type": "cloud_essd", "storage_size": 100})
        self.assertTrue(any("SQL Server" in e for e in errors))

    def test_format_summary(self):
        from products.rds import format_summary
        summary = format_summary({
            "engine": "mysql", "engine_version": "8.0",
            "instance_class": "mysql.n2.medium.2c",
        })
        self.assertIn("数据库引擎", summary)
        self.assertIn("实例规格", summary)


class TestRDSAPI(unittest.TestCase):
    """Integration tests for RDS (requires credentials)."""

    @skip_without_credentials
    def test_subscription_price(self):
        import bss_client
        client = create_test_client()
        params = {
            "engine": "mysql", "engine_version": "8.0",
            "series": "HighAvailability", "instance_class": "mysql.n2.medium.2c",
            "storage_type": "local_ssd", "storage_size": 100,
        }
        modules = build_modules(params)
        pt = resolve_product_type(PRODUCT, params)
        result = bss_client.get_subscription_price(
            client, "rds", modules, region="cn-hangzhou", duration=1, product_type=pt,
        )
        self.assertIsNotNone(result)
        self.assertGreater(float(result["trade_amount"]), 0)

    @skip_without_credentials
    def test_payasyougo_price(self):
        import bss_client
        client = create_test_client()
        params = {
            "engine": "mysql", "engine_version": "8.0",
            "series": "HighAvailability", "instance_class": "mysql.n2.medium.2c",
            "storage_type": "local_ssd", "storage_size": 100,
        }
        modules = build_modules(params)
        pt = resolve_product_type(PRODUCT, params)
        result = bss_client.get_pay_as_you_go_price(
            client, "rds", modules, region="cn-hangzhou", product_type=pt,
        )
        self.assertIsNotNone(result)
        self.assertGreater(float(result["trade_amount"]), 0)


if __name__ == "__main__":
    unittest.main()
