"""
Tests for formatters module - format_product_info, format_registered_products, etc.
"""

import sys
import os
import unittest

_SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "skill", "scripts")
_SCRIPTS_DIR = os.path.abspath(_SCRIPTS_DIR)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

import formatters
import registry


class TestFormatRegisteredProducts(unittest.TestCase):
    """Tests for format_registered_products()."""

    def test_output_has_table_header(self):
        products = registry.list_products()
        result = formatters.format_registered_products(products)
        self.assertIn("已注册产品", result)
        self.assertIn("产品代码", result)
        self.assertIn("产品名称", result)
        self.assertIn("分类", result)

    def test_output_lists_all_products(self):
        products = registry.list_products()
        result = formatters.format_registered_products(products)
        for p in products:
            self.assertIn(p["code"], result)
            self.assertIn(p["display_name"], result)

    def test_output_shows_required_params(self):
        products = registry.list_products()
        result = formatters.format_registered_products(products)
        # ECS has instance_type as required
        self.assertIn("instance_type", result)

    def test_output_shows_count(self):
        products = registry.list_products()
        result = formatters.format_registered_products(products)
        self.assertIn(f"共 {len(products)} 个产品", result)

    def test_empty_list(self):
        result = formatters.format_registered_products([])
        self.assertIn("共 0 个产品", result)

    def test_category_chinese_names(self):
        products = registry.list_products()
        result = formatters.format_registered_products(products)
        # ECS is in compute category
        self.assertIn("计算", result)
        # RDS is in database category
        self.assertIn("数据库", result)


class TestFormatProductInfo(unittest.TestCase):
    """Tests for format_product_info()."""

    def test_ecs_basic_info(self):
        ecs = registry.get_product("ecs")
        result = formatters.format_product_info(ecs)
        self.assertIn("ECS 云服务器", result)
        self.assertIn("`ecs`", result)
        self.assertIn("无", result)  # ProductType is None

    def test_rds_dynamic_product_type(self):
        rds = registry.get_product("rds")
        result = formatters.format_product_info(rds)
        self.assertIn("动态", result)

    def test_slb_static_product_type(self):
        slb = registry.get_product("slb")
        result = formatters.format_product_info(slb)
        self.assertIn("slb", result)

    def test_param_table_present(self):
        ecs = registry.get_product("ecs")
        result = formatters.format_product_info(ecs)
        self.assertIn("参数定义", result)
        self.assertIn("参数名", result)
        self.assertIn("必填", result)
        self.assertIn("`instance_type`", result)

    def test_required_shown(self):
        ecs = registry.get_product("ecs")
        result = formatters.format_product_info(ecs)
        # instance_type is required -> should show "是"
        lines = result.split("\n")
        instance_line = [l for l in lines if "instance_type" in l][0]
        self.assertIn("是", instance_line)

    def test_example_command_present(self):
        ecs = registry.get_product("ecs")
        result = formatters.format_product_info(ecs)
        self.assertIn("示例", result)
        self.assertIn("quoter.py price ecs", result)

    def test_choices_listed(self):
        ecs = registry.get_product("ecs")
        result = formatters.format_product_info(ecs)
        # image_os has choices: linux, windows
        self.assertIn("linux, windows", result)

    def test_defaults_shown(self):
        ecs = registry.get_product("ecs")
        result = formatters.format_product_info(ecs)
        # system_disk_size default is 40
        lines = result.split("\n")
        disk_line = [l for l in lines if "system_disk_size" in l][0]
        self.assertIn("40", disk_line)


class TestFormatPriceResult(unittest.TestCase):
    """Tests for format_price_result() (existing function)."""

    def test_basic_output(self):
        result = formatters.format_price_result(
            product_name="ECS 云服务器",
            config_summary={"实例规格": "ecs.g7.xlarge"},
            price_data={
                "original_amount": 100.0,
                "discount_amount": 0,
                "trade_amount": 100.0,
                "currency": "CNY",
                "module_details": [],
            },
            billing_method="subscription",
            duration=1,
            region="cn-hangzhou",
        )
        self.assertIn("ECS 云服务器", result)
        self.assertIn("100.00", result)
        self.assertIn("包年包月", result)

    def test_yearly_billing_text(self):
        result = formatters.format_price_result(
            product_name="ECS",
            config_summary={},
            price_data={"trade_amount": 1200, "currency": "CNY"},
            billing_method="subscription",
            duration=12,
        )
        self.assertIn("1年", result)

    def test_payasyougo_text(self):
        result = formatters.format_price_result(
            product_name="ECS",
            config_summary={},
            price_data={"trade_amount": 0.5, "currency": "CNY"},
            billing_method="payAsYouGo",
        )
        self.assertIn("按量付费", result)

    def test_discount_shown(self):
        result = formatters.format_price_result(
            product_name="ECS",
            config_summary={},
            price_data={
                "original_amount": 100.0,
                "discount_amount": 15.0,
                "trade_amount": 85.0,
                "currency": "CNY",
                "module_details": [],
            },
            billing_method="subscription",
        )
        self.assertIn("原价", result)
        self.assertIn("优惠", result)
        self.assertIn("-15.00", result)


class TestFormatCredentialCheck(unittest.TestCase):
    """Tests for format_credential_check()."""

    def test_success(self):
        result = formatters.format_credential_check(True)
        self.assertIn("通过", result)

    def test_failure(self):
        result = formatters.format_credential_check(False, "连接超时")
        self.assertIn("失败", result)
        self.assertIn("连接超时", result)


if __name__ == "__main__":
    unittest.main()
