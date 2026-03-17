"""Tests for Kafka product definition."""

import pytest
import sys
from pathlib import Path

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent.parent / "skill" / "scripts"
sys.path.insert(0, str(scripts_dir))

from products.alikafka import build_modules, format_summary, validate, PRODUCT, _get_product_type


class TestBuildModules:
    """测试 build_modules 函数."""

    def test_basic_subscription(self):
        """测试包年包月基础配置."""
        params = {
            "region": "cn-hangzhou",
            "spec_type": "normal",
            "partition_num": 100,
            "topic_quota": 50,
            "disk_type": "1",
            "disk_size": 500,
            "eip_max": 0,
            "subscription_type": "Subscription",
        }
        modules = build_modules(params)

        assert len(modules) == 4
        module_codes = [m["module_code"] for m in modules]
        assert "PartitionNum" in module_codes
        assert "TopicQuota" in module_codes
        assert "IoMaxSpec" in module_codes
        assert "DiskSize" in module_codes
        assert "EipMax" not in module_codes

    def test_with_eip(self):
        """测试包含公网流量的配置."""
        params = {
            "region": "cn-hangzhou",
            "spec_type": "normal",
            "partition_num": 100,
            "topic_quota": 50,
            "disk_type": "1",
            "disk_size": 500,
            "eip_max": 100,
            "subscription_type": "Subscription",
        }
        modules = build_modules(params)

        assert len(modules) == 5
        module_codes = [m["module_code"] for m in modules]
        assert "EipMax" in module_codes

    def test_high_read_spec(self):
        """测试高读版规格自动选择 io_max_spec."""
        params = {
            "region": "cn-hangzhou",
            "spec_type": "professionalForHighRead",
            "partition_num": 100,
            "topic_quota": 50,
            "disk_type": "1",
            "disk_size": 500,
            "subscription_type": "Subscription",
        }
        modules = build_modules(params)

        io_max_spec_module = next(m for m in modules if m["module_code"] == "IoMaxSpec")
        assert "alikafka.hr." in io_max_spec_module["config"]


class TestValidate:
    """测试 validate 函数."""

    def test_valid_params(self):
        """测试有效参数."""
        params = {
            "region": "cn-hangzhou",
            "spec_type": "normal",
            "partition_num": 100,
            "topic_quota": 50,
            "disk_type": "1",
            "disk_size": 500,
        }
        errors = validate(params)
        assert len(errors) == 0

    def test_missing_required(self):
        """测试缺少必填参数."""
        params = {"region": "cn-hangzhou"}
        errors = validate(params)
        assert len(errors) > 0
        assert any("spec_type" in e for e in errors)

    def test_invalid_spec_type(self):
        """测试无效 spec_type."""
        params = {
            "region": "cn-hangzhou",
            "spec_type": "invalid",
            "partition_num": 100,
            "topic_quota": 50,
            "disk_type": "1",
            "disk_size": 500,
        }
        errors = validate(params)
        assert any("spec_type" in e for e in errors)

    def test_partition_num_out_of_range(self):
        """测试分区数超出范围."""
        params = {
            "region": "cn-hangzhou",
            "spec_type": "normal",
            "partition_num": 50000,
            "topic_quota": 50,
            "disk_type": "1",
            "disk_size": 500,
        }
        errors = validate(params)
        assert any("partition_num" in e for e in errors)


class TestFormatSummary:
    """测试 format_summary 函数."""

    def test_basic_summary(self):
        """测试基础摘要生成."""
        params = {
            "region": "cn-hangzhou",
            "spec_type": "normal",
            "partition_num": 100,
            "topic_quota": 50,
            "disk_type": "1",
            "disk_size": 500,
            "subscription_type": "Subscription",
        }
        summary = format_summary(params)

        assert summary["产品"] == "消息队列 Kafka"
        assert summary["付费模式"] == "包年包月"
        assert summary["地域"] == "cn-hangzhou"
        assert "公网流量峰值" not in summary

    def test_with_eip_summary(self):
        """测试包含公网的摘要."""
        params = {
            "region": "cn-hangzhou",
            "spec_type": "normal",
            "partition_num": 100,
            "topic_quota": 50,
            "disk_type": "1",
            "disk_size": 500,
            "eip_max": 100,
            "subscription_type": "Subscription",
        }
        summary = format_summary(params)

        assert "公网流量峰值" in summary
        assert summary["公网流量峰值"] == "100MB/s"


class TestProductType:
    """测试 _get_product_type 函数."""

    def test_subscription(self):
        """测试包年包月 ProductType."""
        params = {"subscription_type": "Subscription"}
        assert _get_product_type(params) == "alikafka_pre"

    def test_payasyougo(self):
        """测试按量付费 ProductType."""
        params = {"subscription_type": "PayAsYouGo"}
        assert _get_product_type(params) == "alikafka_post"

    def test_default(self):
        """测试默认 ProductType."""
        params = {}
        assert _get_product_type(params) == "alikafka_pre"


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
        expected_names = ["region", "spec_type", "partition_num", "topic_quota", "disk_type", "disk_size", "eip_max", "io_max_spec", "subscription_type"]
        for name in expected_names:
            assert name in param_names, f"Missing param: {name}"
