"""Tests for RocketMQ 5.0 product definition."""

import pytest
import sys
from pathlib import Path

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent.parent / "skill" / "scripts"
sys.path.insert(0, str(scripts_dir))

from products.rocketmq import build_modules, format_summary, validate, PRODUCT, _get_product_type, _get_valid_process_specs


class TestBuildModules:
    """测试 build_modules 函数."""

    def test_basic_subscription(self):
        """测试包年包月基础配置."""
        params = {
            "region": "cn-hangzhou",
            "chip_type": "x86",
            "msg_process_spec": "rmq.su.2xlarge",
            "msg_store_spec": "rmq.ssu.2xlarge",
            "series_type": "standard",
            "flow_out_bandwidth": 0,
            "topic_paid": 0,
            "subscription_type": "Subscription",
        }
        modules = build_modules(params)

        # 应该返回2个模块（不含flow_out_bandwidth和topic_paid）
        assert len(modules) == 2
        module_codes = [m["module_code"] for m in modules]
        assert "msg_process_spec" in module_codes
        assert "msg_store_spec" in module_codes
        assert "flow_out_bandwidth" not in module_codes
        assert "topic_paid" not in module_codes

    def test_with_flow_out(self):
        """测试包含公网带宽的配置."""
        params = {
            "region": "cn-hangzhou",
            "chip_type": "x86",
            "msg_process_spec": "rmq.su.2xlarge",
            "msg_store_spec": "rmq.ssu.2xlarge",
            "series_type": "standard",
            "flow_out_bandwidth": 100,
            "flow_out_type": "payByTraffic",
            "topic_paid": 0,
            "subscription_type": "Subscription",
        }
        modules = build_modules(params)

        # 应该返回3个模块（含flow_out_bandwidth）
        assert len(modules) == 3
        module_codes = [m["module_code"] for m in modules]
        assert "flow_out_bandwidth" in module_codes

    def test_with_topic_paid(self):
        """测试包含付费Topic的配置."""
        params = {
            "region": "cn-hangzhou",
            "chip_type": "x86",
            "msg_process_spec": "rmq.su.2xlarge",
            "msg_store_spec": "rmq.ssu.2xlarge",
            "series_type": "standard",
            "flow_out_bandwidth": 0,
            "topic_paid": 10,
            "subscription_type": "Subscription",
        }
        modules = build_modules(params)

        # 应该返回3个模块（含topic_paid）
        assert len(modules) == 3
        module_codes = [m["module_code"] for m in modules]
        assert "topic_paid" in module_codes


class TestValidate:
    """测试 validate 函数."""

    def test_valid_params(self):
        """测试有效参数."""
        params = {
            "region": "cn-hangzhou",
            "chip_type": "x86",
            "msg_process_spec": "rmq.su.2xlarge",
            "msg_store_spec": "rmq.ssu.2xlarge",
            "series_type": "standard",
        }
        errors = validate(params)
        assert len(errors) == 0

    def test_missing_required(self):
        """测试缺少必填参数."""
        params = {"region": "cn-hangzhou"}
        errors = validate(params)
        assert len(errors) > 0
        assert any("chip_type" in e for e in errors)

    def test_invalid_chip_type(self):
        """测试无效 chip_type."""
        params = {
            "region": "cn-hangzhou",
            "chip_type": "invalid",
            "msg_process_spec": "rmq.su.2xlarge",
            "msg_store_spec": "rmq.ssu.2xlarge",
            "series_type": "standard",
        }
        errors = validate(params)
        assert any("chip_type" in e for e in errors)

    def test_invalid_series_type(self):
        """测试无效 series_type."""
        params = {
            "region": "cn-hangzhou",
            "chip_type": "x86",
            "msg_process_spec": "rmq.su.2xlarge",
            "msg_store_spec": "rmq.ssu.2xlarge",
            "series_type": "invalid",
        }
        errors = validate(params)
        assert any("series_type" in e for e in errors)

    def test_chip_type_mismatch(self):
        """测试 chip_type 与 msg_process_spec 不匹配."""
        params = {
            "region": "cn-hangzhou",
            "chip_type": "arm",
            "msg_process_spec": "rmq.su.8xlarge",  # arm 不支持 8xlarge
            "msg_store_spec": "rmq.ssu.2xlarge",
            "series_type": "standard",
        }
        errors = validate(params)
        assert any("msg_process_spec" in e for e in errors)


class TestFormatSummary:
    """测试 format_summary 函数."""

    def test_basic_summary(self):
        """测试基础摘要生成."""
        params = {
            "region": "cn-hangzhou",
            "chip_type": "x86",
            "msg_process_spec": "rmq.su.2xlarge",
            "msg_store_spec": "rmq.ssu.2xlarge",
            "series_type": "standard",
            "subscription_type": "Subscription",
        }
        summary = format_summary(params)

        assert summary["产品"] == "消息队列 RocketMQ 5.0"
        assert summary["付费模式"] == "包年包月"
        assert summary["地域"] == "cn-hangzhou"
        assert summary["架构类型"] == "X86"
        assert "公网带宽" not in summary

    def test_with_flow_out_summary(self):
        """测试包含公网的摘要."""
        params = {
            "region": "cn-hangzhou",
            "chip_type": "x86",
            "msg_process_spec": "rmq.su.2xlarge",
            "msg_store_spec": "rmq.ssu.2xlarge",
            "series_type": "standard",
            "flow_out_bandwidth": 100,
            "flow_out_type": "payByTraffic",
            "subscription_type": "Subscription",
        }
        summary = format_summary(params)

        assert "公网带宽" in summary
        assert summary["公网带宽"] == "100MB/s"
        assert summary["公网计费"] == "按流量计费"


class TestProductType:
    """测试 _get_product_type 函数."""

    def test_subscription(self):
        """测试包年包月 ProductType."""
        params = {"subscription_type": "Subscription"}
        assert _get_product_type(params) == "ons_rmqsub_public_cn"

    def test_payasyougo(self):
        """测试按量付费 ProductType."""
        params = {"subscription_type": "PayAsYouGo"}
        assert _get_product_type(params) == "ons_rmqpost_public_cn"

    def test_default(self):
        """测试默认 ProductType."""
        params = {}
        assert _get_product_type(params) == "ons_rmqsub_public_cn"


class TestProduct:
    """测试 PRODUCT dict."""

    def test_product_structure(self):
        """测试 PRODUCT 结构完整性."""
        required_fields = ["code", "name", "display_name", "product_type", "category", "params", "build_modules", "format_summary", "validate"]
        for field in required_fields:
            assert field in PRODUCT, f"Missing field: {field}"

    def test_params_length(self):
        """测试参数数量."""
        assert len(PRODUCT["params"]) == 9

    def test_param_names(self):
        """测试参数名称."""
        param_names = [p["name"] for p in PRODUCT["params"]]
        expected_names = ["region", "chip_type", "msg_process_spec", "msg_store_spec", "series_type", "flow_out_bandwidth", "flow_out_type", "topic_paid", "subscription_type"]
        for name in expected_names:
            assert name in param_names, f"Missing param: {name}"
