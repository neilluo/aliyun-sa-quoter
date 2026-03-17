"""Tests for Elasticsearch product definition."""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "skill", "scripts"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from conftest import (
    skip_without_credentials, create_test_client,
    assert_valid_product, assert_valid_module_list,
)
from products.elasticsearch import PRODUCT, build_modules, validate, _get_product_type, format_summary
from products._base import resolve_product_type


class TestElasticsearchModules(unittest.TestCase):
    """Unit tests for Elasticsearch product (no credentials needed)."""

    def test_product_definition(self):
        assert_valid_product(self, PRODUCT)
        self.assertEqual(PRODUCT["code"], "elasticsearch")
        self.assertEqual(PRODUCT["category"], "database")

    def test_product_type_dynamic(self):
        """ProductType should vary by subscription_type."""
        # Subscription (包年包月) uses "elasticsearchpre"
        self.assertEqual(resolve_product_type(PRODUCT, {"subscription_type": "Subscription"}), "elasticsearchpre")
        # PayAsYouGo (按量付费) uses "elasticsearch"
        self.assertEqual(resolve_product_type(PRODUCT, {"subscription_type": "PayAsYouGo"}), "elasticsearch")
        # Default should be "elasticsearchpre"
        self.assertEqual(resolve_product_type(PRODUCT, {}), "elasticsearchpre")

    def test_get_product_type_function(self):
        """Test _get_product_type function directly."""
        self.assertEqual(_get_product_type({"subscription_type": "Subscription"}), "elasticsearchpre")
        self.assertEqual(_get_product_type({"subscription_type": "PayAsYouGo"}), "elasticsearch")
        self.assertEqual(_get_product_type({}), "elasticsearchpre")

    def test_build_modules(self):
        params = {
            "region": "cn-hangzhou",
            "node_spec": "elasticsearch.g7.xlarge",
            "node_amount": 3,
            "disk_type": "cloud_ssd",
            "disk_size": 100,
            "performance_level": "PL1",
        }
        modules = build_modules(params)
        assert_valid_module_list(self, modules)
        self.assertEqual(len(modules), 2)
        codes = [m["module_code"] for m in modules]
        self.assertIn("NodeSpec", codes)
        self.assertIn("Disk", codes)

    def test_build_modules_config_values(self):
        """Test that module configs are built correctly."""
        params = {
            "region": "cn-beijing",
            "node_spec": "elasticsearch.r7.2xlarge",
            "node_amount": 5,
            "disk_type": "cloud_essd",
            "disk_size": 500,
            "performance_level": "PL2",
        }
        modules = build_modules(params)
        
        # Check NodeSpec module
        node_spec_mod = next(m for m in modules if m["module_code"] == "NodeSpec")
        self.assertEqual(node_spec_mod["config"], "NodeSpec:elasticsearch.r7.2xlarge,Region:cn-beijing,NodeAmount:5")
        self.assertEqual(node_spec_mod["price_type"], "Hour")
        
        # Check Disk module
        disk_mod = next(m for m in modules if m["module_code"] == "Disk")
        self.assertEqual(disk_mod["config"], "DataDiskType:cloud_essd,PerformanceLevel:PL2,Region:cn-beijing,NodeAmount:5,Disk:500")
        self.assertEqual(disk_mod["price_type"], "Hour")

    def test_build_modules_with_default_performance_level(self):
        """Test that default PL1 is used when performance_level not provided."""
        params = {
            "region": "cn-shanghai",
            "node_spec": "elasticsearch.g7.xlarge",
            "node_amount": 3,
            "disk_type": "cloud_ssd",
            "disk_size": 100,
        }
        modules = build_modules(params)
        disk_mod = next(m for m in modules if m["module_code"] == "Disk")
        self.assertIn("PerformanceLevel:PL1", disk_mod["config"])

    def test_format_summary(self):
        """Test format_summary returns correct Chinese summary."""
        # Test Subscription mode
        summary = format_summary({
            "subscription_type": "Subscription",
            "region": "cn-hangzhou",
            "node_spec": "elasticsearch.g7.xlarge",
            "node_amount": 3,
            "disk_type": "cloud_ssd",
            "disk_size": 100,
        })
        self.assertEqual(summary["产品"], "Elasticsearch")
        self.assertEqual(summary["付费模式"], "包年包月")
        self.assertEqual(summary["地域"], "cn-hangzhou")
        self.assertEqual(summary["数据节点规格"], "elasticsearch.g7.xlarge")
        self.assertEqual(summary["数据节点数量"], "3")
        self.assertEqual(summary["存储类型"], "cloud_ssd")
        self.assertEqual(summary["单节点存储"], "100GB")

        # Test PayAsYouGo mode
        summary = format_summary({
            "subscription_type": "PayAsYouGo",
            "region": "cn-beijing",
            "node_spec": "elasticsearch.r7.2xlarge",
            "node_amount": 5,
            "disk_type": "cloud_essd",
            "disk_size": 500,
        })
        self.assertEqual(summary["付费模式"], "按量付费")

    def test_validate_node_amount_range(self):
        """Test node_amount validation (2-50)."""
        # Too few nodes
        errors = validate({"node_amount": 1, "disk_size": 100, "disk_type": "cloud_ssd"})
        self.assertTrue(any("至少为 2" in e for e in errors))
        
        # Too many nodes
        errors = validate({"node_amount": 51, "disk_size": 100, "disk_type": "cloud_ssd"})
        self.assertTrue(any("不能超过 50" in e for e in errors))
        
        # Valid node amounts
        errors = validate({"node_amount": 2, "disk_size": 100, "disk_type": "cloud_ssd"})
        self.assertEqual(len(errors), 0)
        errors = validate({"node_amount": 50, "disk_size": 100, "disk_type": "cloud_ssd"})
        self.assertEqual(len(errors), 0)

    def test_validate_disk_size_range(self):
        """Test disk_size validation (20-20480 GB)."""
        # Too small disk
        errors = validate({"node_amount": 3, "disk_size": 10, "disk_type": "cloud_ssd"})
        self.assertTrue(any("至少为 20GB" in e for e in errors))
        
        # Too large disk
        errors = validate({"node_amount": 3, "disk_size": 30000, "disk_type": "cloud_ssd"})
        self.assertTrue(any("不能超过 20480GB" in e for e in errors))
        
        # Valid disk sizes
        errors = validate({"node_amount": 3, "disk_size": 20, "disk_type": "cloud_ssd"})
        self.assertEqual(len(errors), 0)
        errors = validate({"node_amount": 3, "disk_size": 20480, "disk_type": "cloud_ssd"})
        self.assertEqual(len(errors), 0)

    def test_validate_essd_requires_performance_level(self):
        """Test that ESSD disk requires performance level."""
        # ESSD without performance_level should fail
        errors = validate({"node_amount": 3, "disk_size": 100, "disk_type": "cloud_essd", "performance_level": ""})
        self.assertTrue(any("ESSD" in e and "性能级别" in e for e in errors))
        
        # ESSD with performance_level should pass
        errors = validate({"node_amount": 3, "disk_size": 100, "disk_type": "cloud_essd", "performance_level": "PL1"})
        self.assertEqual(len(errors), 0)

    def test_validate_all_valid_params(self):
        """Test that valid parameters pass validation."""
        errors = validate({
            "node_amount": 3,
            "disk_size": 100,
            "disk_type": "cloud_ssd",
            "performance_level": "PL1",
        })
        self.assertEqual(len(errors), 0)


class TestElasticsearchAPI(unittest.TestCase):
    """Integration tests for Elasticsearch (requires credentials)."""

    @skip_without_credentials
    def test_subscription_price(self):
        import bss_client
        client = create_test_client()
        params = {
            "region": "cn-hangzhou",
            "node_spec": "elasticsearch.g7.xlarge",
            "node_amount": 3,
            "disk_type": "cloud_ssd",
            "disk_size": 100,
            "performance_level": "PL1",
            "subscription_type": "Subscription",
        }
        modules = build_modules(params)
        pt = resolve_product_type(PRODUCT, params)
        result = bss_client.get_subscription_price(
            client, "elasticsearch", modules, region="cn-hangzhou", duration=1, product_type=pt,
        )
        self.assertIsNotNone(result)
        self.assertGreater(float(result["trade_amount"]), 0)

    @skip_without_credentials
    def test_payasyougo_price(self):
        import bss_client
        client = create_test_client()
        params = {
            "region": "cn-hangzhou",
            "node_spec": "elasticsearch.g7.xlarge",
            "node_amount": 3,
            "disk_type": "cloud_ssd",
            "disk_size": 100,
            "performance_level": "PL1",
            "subscription_type": "PayAsYouGo",
        }
        modules = build_modules(params)
        pt = resolve_product_type(PRODUCT, params)
        result = bss_client.get_pay_as_you_go_price(
            client, "elasticsearch", modules, region="cn-hangzhou", product_type=pt,
        )
        self.assertIsNotNone(result)
        self.assertGreater(float(result["trade_amount"]), 0)


if __name__ == "__main__":
    unittest.main()
