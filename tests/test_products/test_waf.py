"""Tests for WAF product definition."""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "skill", "scripts"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from conftest import (
    skip_without_credentials, create_test_client,
    assert_valid_product, assert_valid_module_list,
)
from products.waf import PRODUCT, build_modules, validate, format_summary
from framework.base import resolve_product_type


class TestWAFProductDefinition(unittest.TestCase):
    """Unit tests for WAF product definition (no credentials needed)."""

    def test_product_definition(self):
        assert_valid_product(self, PRODUCT)
        self.assertEqual(PRODUCT["code"], "waf")
        self.assertEqual(PRODUCT["category"], "security")

    def test_product_type_subscription(self):
        """包年包月模式应返回 waf_v3prepaid_public_cn."""
        params = {"billing_mode": "subscription"}
        self.assertEqual(resolve_product_type(PRODUCT, params), "waf_v3prepaid_public_cn")

    def test_product_type_payasyougo(self):
        """按量付费模式应返回 waf_v2_public_cn."""
        params = {"billing_mode": "payasyougo"}
        self.assertEqual(resolve_product_type(PRODUCT, params), "waf_v2_public_cn")


class TestWAFSubscriptionModules(unittest.TestCase):
    """Tests for WAF subscription mode module building."""

    def test_basic_version_3(self):
        """基础高级版配置."""
        params = {
            "billing_mode": "subscription",
            "package_code": "version_3",
            "region": "cn-hangzhou",
        }
        modules = build_modules(params)
        assert_valid_module_list(self, modules)
        self.assertEqual(len(modules), 1)
        self.assertEqual(modules[0]["module_code"], "PackageCode")
        self.assertIn("PackageCode:version_3", modules[0]["config"])

    def test_version_4_with_qps(self):
        """企业版带QPS扩展."""
        params = {
            "billing_mode": "subscription",
            "package_code": "version_4",
            "region": "cn-hangzhou",
            "qps_package": 10,
        }
        modules = build_modules(params)
        codes = [m["module_code"] for m in modules]
        self.assertIn("PackageCode", codes)
        self.assertIn("QPSPackage", codes)

    def test_with_bot_web(self):
        """启用Bot Web防护."""
        params = {
            "billing_mode": "subscription",
            "package_code": "version_4",
            "region": "cn-hangzhou",
            "bot_web": 1,
        }
        modules = build_modules(params)
        codes = [m["module_code"] for m in modules]
        self.assertIn("botWeb", codes)

    def test_with_bot_app(self):
        """启用Bot APP防护."""
        params = {
            "billing_mode": "subscription",
            "package_code": "version_4",
            "region": "cn-hangzhou",
            "bot_app": 1,
        }
        modules = build_modules(params)
        codes = [m["module_code"] for m in modules]
        self.assertIn("botApp", codes)

    def test_with_apisec(self):
        """启用API安全."""
        params = {
            "billing_mode": "subscription",
            "package_code": "version_4",
            "region": "cn-hangzhou",
            "apisec": 1,
        }
        modules = build_modules(params)
        codes = [m["module_code"] for m in modules]
        self.assertIn("apisec", codes)

    def test_with_ext_domain_package(self):
        """域名扩展包."""
        params = {
            "billing_mode": "subscription",
            "package_code": "version_4",
            "region": "cn-hangzhou",
            "ext_domain_package": 5,
        }
        modules = build_modules(params)
        codes = [m["module_code"] for m in modules]
        self.assertIn("ExtDomainPackage", codes)

    def test_with_domain_vip(self):
        """独享IP."""
        params = {
            "billing_mode": "subscription",
            "package_code": "version_4",
            "region": "cn-hangzhou",
            "domain_vip": 2,
        }
        modules = build_modules(params)
        codes = [m["module_code"] for m in modules]
        self.assertIn("domainVip", codes)

    def test_with_log_storage(self):
        """日志存储."""
        params = {
            "billing_mode": "subscription",
            "package_code": "version_4",
            "region": "cn-hangzhou",
            "log_storage": 100,
        }
        modules = build_modules(params)
        codes = [m["module_code"] for m in modules]
        self.assertIn("LogStorage", codes)

    def test_with_waf_gslb(self):
        """智能负载均衡."""
        params = {
            "billing_mode": "subscription",
            "package_code": "version_4",
            "region": "cn-hangzhou",
            "waf_gslb": 1,
        }
        modules = build_modules(params)
        codes = [m["module_code"] for m in modules]
        self.assertIn("WafGslb", codes)

    def test_with_hybrid_cloud_node(self):
        """混合云节点."""
        params = {
            "billing_mode": "subscription",
            "package_code": "version_4",
            "region": "cn-hangzhou",
            "hybrid_cloud_node": 2,
        }
        modules = build_modules(params)
        codes = [m["module_code"] for m in modules]
        self.assertIn("HybridCloudNode", codes)

    def test_with_blue_teaming(self):
        """重保场景."""
        params = {
            "billing_mode": "subscription",
            "package_code": "version_4",
            "region": "cn-hangzhou",
            "blue_teaming": 1,
        }
        modules = build_modules(params)
        codes = [m["module_code"] for m in modules]
        self.assertIn("BlueTeaming", codes)

    def test_with_spike_throttle(self):
        """洪峰限流."""
        params = {
            "billing_mode": "subscription",
            "package_code": "version_4",
            "region": "cn-hangzhou",
            "spike_throttle": 100,
        }
        modules = build_modules(params)
        codes = [m["module_code"] for m in modules]
        self.assertIn("spikeThrottle", codes)

    def test_with_elastic_qps(self):
        """弹性QPS."""
        params = {
            "billing_mode": "subscription",
            "package_code": "version_4",
            "region": "cn-hangzhou",
            "elastic_qps": 1000,
        }
        modules = build_modules(params)
        codes = [m["module_code"] for m in modules]
        self.assertIn("ElasticQps", codes)

    def test_full_config(self):
        """完整配置."""
        params = {
            "billing_mode": "subscription",
            "package_code": "version_5",
            "region": "cn-hangzhou",
            "qps_package": 10,
            "ext_domain_package": 5,
            "bot_web": 1,
            "bot_app": 1,
            "apisec": 1,
            "domain_vip": 2,
            "log_storage": 100,
            "waf_gslb": 1,
            "hybrid_cloud_node": 2,
            "blue_teaming": 1,
            "spike_throttle": 100,
            "elastic_qps": 1000,
        }
        modules = build_modules(params)
        assert_valid_module_list(self, modules)
        codes = [m["module_code"] for m in modules]
        expected_codes = [
            "PackageCode", "QPSPackage", "ExtDomainPackage", "botWeb", "botApp",
            "apisec", "domainVip", "LogStorage", "WafGslb", "HybridCloudNode",
            "BlueTeaming", "spikeThrottle", "ElasticQps",
        ]
        for code in expected_codes:
            self.assertIn(code, codes)


class TestWAFPayAsYouGoModules(unittest.TestCase):
    """Tests for WAF pay-as-you-go mode module building."""

    def test_basic_secu(self):
        """基础SeCU配置."""
        params = {
            "billing_mode": "payasyougo",
            "secu": 100,
            "region": "cn-hangzhou",
        }
        modules = build_modules(params)
        assert_valid_module_list(self, modules)
        self.assertEqual(len(modules), 1)
        self.assertEqual(modules[0]["module_code"], "SeCU")
        self.assertIn("SeCU:100", modules[0]["config"])

    def test_secu_default_value(self):
        """SeCU默认值为1."""
        params = {
            "billing_mode": "payasyougo",
            "region": "cn-hangzhou",
        }
        modules = build_modules(params)
        self.assertIn("SeCU:1", modules[0]["config"])


class TestWAFValidation(unittest.TestCase):
    """Tests for WAF parameter validation."""

    def test_missing_billing_mode(self):
        """billing_mode是必填参数."""
        errors = validate({})
        self.assertTrue(any("billing_mode" in e for e in errors))

    def test_invalid_billing_mode(self):
        """无效的billing_mode."""
        errors = validate({"billing_mode": "invalid"})
        self.assertTrue(any("billing_mode" in e.lower() for e in errors))

    def test_subscription_missing_package_code(self):
        """包年包月模式下package_code必填."""
        errors = validate({"billing_mode": "subscription"})
        self.assertTrue(any("package_code" in e for e in errors))

    def test_subscription_invalid_package_code(self):
        """无效的package_code."""
        errors = validate({"billing_mode": "subscription", "package_code": "invalid"})
        self.assertTrue(any("package_code" in e for e in errors))

    def test_subscription_valid_package_codes(self):
        """有效的package_code."""
        for code in ["version_3", "version_4", "version_5"]:
            errors = validate({"billing_mode": "subscription", "package_code": code})
            self.assertEqual(len(errors), 0, f"package_code={code} 不应报错")

    def test_payasyougo_missing_secu(self):
        """按量付费模式下secu必填."""
        errors = validate({"billing_mode": "payasyougo"})
        self.assertTrue(any("secu" in e.lower() for e in errors))

    def test_payasyougo_invalid_secu(self):
        """secu必须大于等于1."""
        errors = validate({"billing_mode": "payasyougo", "secu": 0})
        self.assertTrue(any("secu" in e.lower() for e in errors))

    def test_valid_subscription(self):
        """有效的包年包月参数."""
        errors = validate({
            "billing_mode": "subscription",
            "package_code": "version_4",
        })
        self.assertEqual(len(errors), 0)

    def test_valid_payasyougo(self):
        """有效的按量付费参数."""
        errors = validate({
            "billing_mode": "payasyougo",
            "secu": 100,
        })
        self.assertEqual(len(errors), 0)


class TestWAFSummary(unittest.TestCase):
    """Tests for WAF summary formatting."""

    def test_subscription_summary(self):
        """包年包月模式摘要."""
        summary = format_summary({
            "billing_mode": "subscription",
            "package_code": "version_4",
            "region": "cn-hangzhou",
            "qps_package": 10,
            "bot_web": 1,
        })
        self.assertEqual(summary["产品"], "WAF")
        self.assertEqual(summary["版本"], "企业版")
        self.assertEqual(summary["计费模式"], "包年包月")
        self.assertIn("QPS扩展(10)", summary.get("扩展包", ""))
        self.assertIn("Bot-Web", summary.get("安全功能", ""))

    def test_payasyougo_summary(self):
        """按量付费模式摘要."""
        summary = format_summary({
            "billing_mode": "payasyougo",
            "secu": 100,
            "region": "cn-hangzhou",
        })
        self.assertEqual(summary["产品"], "WAF")
        self.assertEqual(summary["计费模式"], "按量付费")
        self.assertEqual(summary["SeCU"], 100)

    def test_version_mapping(self):
        """版本映射."""
        version_tests = [
            ("version_3", "高级版"),
            ("version_4", "企业版"),
            ("version_5", "旗舰版"),
        ]
        for code, expected_name in version_tests:
            summary = format_summary({
                "billing_mode": "subscription",
                "package_code": code,
            })
            self.assertEqual(summary["版本"], expected_name)


class TestWAFAPI(unittest.TestCase):
    """Integration tests for WAF (requires credentials)."""

    @skip_without_credentials
    def test_subscription_price_basic(self):
        """包年包月基础版本询价."""
        import bss_client
        client = create_test_client()
        params = {
            "billing_mode": "subscription",
            "package_code": "version_4",
            "region": "cn-hangzhou",
        }
        modules = build_modules(params)
        pt = resolve_product_type(PRODUCT, params)
        result = bss_client.get_subscription_price(
            client, "waf", modules, region="cn-hangzhou", duration=1, product_type=pt,
        )
        self.assertIsNotNone(result)
        self.assertGreater(float(result["trade_amount"]), 0)

    @skip_without_credentials
    def test_subscription_price_with_extensions(self):
        """包年包月带扩展功能询价."""
        import bss_client
        client = create_test_client()
        params = {
            "billing_mode": "subscription",
            "package_code": "version_4",
            "region": "cn-hangzhou",
            "qps_package": 10,
            "bot_web": 1,
            "apisec": 1,
        }
        modules = build_modules(params)
        pt = resolve_product_type(PRODUCT, params)
        result = bss_client.get_subscription_price(
            client, "waf", modules, region="cn-hangzhou", duration=1, product_type=pt,
        )
        self.assertIsNotNone(result)
        self.assertGreater(float(result["trade_amount"]), 0)

    @skip_without_credentials
    def test_payasyougo_price(self):
        """按量付费询价."""
        import bss_client
        client = create_test_client()
        params = {
            "billing_mode": "payasyougo",
            "secu": 100,
            "region": "cn-hangzhou",
        }
        modules = build_modules(params)
        pt = resolve_product_type(PRODUCT, params)
        result = bss_client.get_pay_as_you_go_price(
            client, "waf", modules, region="cn-hangzhou", product_type=pt,
        )
        self.assertIsNotNone(result)
        self.assertGreater(float(result["trade_amount"]), 0)


if __name__ == "__main__":
    unittest.main()
