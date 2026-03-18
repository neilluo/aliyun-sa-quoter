"""Tests for NAS product definition."""

import pytest
import sys
from pathlib import Path

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent.parent / "skill" / "scripts"
sys.path.insert(0, str(scripts_dir))

from products.nas import build_modules, format_summary, validate, PRODUCT


class TestBuildModules:
    """测试 build_modules 函数."""

    def test_basic_payasyougo(self):
        """测试按量付费基础配置."""
        params = {
            "region": "cn-hangzhou",
            "file_system_type": "standard",
            "storage_type": "Performance",
            "protocol_type": "NFS",
            "capacity": 100,
            "data_transfer": 0,
            "subscription_type": "PayAsYouGo",
        }
        modules = build_modules(params)

        # 应该返回2个模块（不含DataTransfer）
        assert len(modules) == 2
        module_codes = [m["module_code"] for m in modules]
        assert "FileSystem" in module_codes
        assert "Capacity" in module_codes
        assert "DataTransfer" not in module_codes

    def test_with_data_transfer(self):
        """测试包含数据传出流量的配置."""
        params = {
            "region": "cn-hangzhou",
            "file_system_type": "standard",
            "storage_type": "Performance",
            "protocol_type": "NFS",
            "capacity": 100,
            "data_transfer": 500,
            "subscription_type": "PayAsYouGo",
        }
        modules = build_modules(params)

        # 应该返回3个模块（含DataTransfer）
        assert len(modules) == 3
        module_codes = [m["module_code"] for m in modules]
        assert "DataTransfer" in module_codes

    def test_extreme_file_system(self):
        """测试极速型文件系统."""
        params = {
            "region": "cn-hangzhou",
            "file_system_type": "extreme",
            "storage_type": "Performance",
            "protocol_type": "NFS",
            "capacity": 1000,
            "subscription_type": "PayAsYouGo",
        }
        modules = build_modules(params)

        # 检查 FileSystem 模块配置
        file_system_module = next(m for m in modules if m["module_code"] == "FileSystem")
        assert "extreme" in file_system_module["config"]


class TestValidate:
    """测试 validate 函数."""

    def test_valid_params(self):
        """测试有效参数."""
        params = {
            "region": "cn-hangzhou",
            "file_system_type": "standard",
            "storage_type": "Performance",
            "protocol_type": "NFS",
            "capacity": 100,
        }
        errors = validate(params)
        assert len(errors) == 0

    def test_missing_required(self):
        """测试缺少必填参数."""
        params = {"region": "cn-hangzhou"}
        errors = validate(params)
        assert len(errors) > 0
        assert any("file_system_type" in e for e in errors)

    def test_invalid_file_system_type(self):
        """测试无效 file_system_type."""
        params = {
            "region": "cn-hangzhou",
            "file_system_type": "invalid",
            "storage_type": "Performance",
            "protocol_type": "NFS",
            "capacity": 100,
        }
        errors = validate(params)
        assert any("file_system_type" in e for e in errors)

    def test_capacity_too_small(self):
        """测试容量过小."""
        params = {
            "region": "cn-hangzhou",
            "file_system_type": "standard",
            "storage_type": "Performance",
            "protocol_type": "NFS",
            "capacity": 50,  # 小于100
        }
        errors = validate(params)
        assert any("capacity" in e for e in errors)

    def test_cpfs_capacity_too_small(self):
        """测试 CPFS 容量小于 4TB."""
        params = {
            "region": "cn-hangzhou",
            "file_system_type": "cpfs",
            "storage_type": "Performance",
            "protocol_type": "NFS",
            "capacity": 1000,  # 小于4TB
        }
        errors = validate(params)
        assert any("capacity" in e for e in errors)


class TestFormatSummary:
    """测试 format_summary 函数."""

    def test_basic_summary(self):
        """测试基础摘要生成."""
        params = {
            "region": "cn-hangzhou",
            "file_system_type": "standard",
            "storage_type": "Performance",
            "protocol_type": "NFS",
            "capacity": 100,
            "subscription_type": "PayAsYouGo",
        }
        summary = format_summary(params)

        assert summary["产品"] == "文件存储 NAS"
        assert summary["付费模式"] == "按量付费"
        assert summary["地域"] == "cn-hangzhou"
        assert summary["文件系统类型"] == "通用型"
        assert summary["存储类型"] == "性能型"
        assert summary["协议类型"] == "NFS"
        assert "数据传出流量" not in summary

    def test_with_data_transfer_summary(self):
        """测试包含数据传出流量的摘要."""
        params = {
            "region": "cn-hangzhou",
            "file_system_type": "standard",
            "storage_type": "Performance",
            "protocol_type": "NFS",
            "capacity": 100,
            "data_transfer": 500,
            "subscription_type": "PayAsYouGo",
        }
        summary = format_summary(params)

        assert "数据传出流量" in summary
        assert summary["数据传出流量"] == "500GB"


class TestProductType:
    """测试 _get_product_type 函数."""

    def test_subscription(self):
        """测试包年包月 ProductType."""
        params = {"subscription_type": "Subscription"}
        assert _get_product_type(params) == "naspost"

    def test_payasyougo(self):
        """测试按量付费 ProductType."""
        params = {"subscription_type": "PayAsYouGo"}
        assert _get_product_type(params) == "naspost"

    def test_default(self):
        """测试默认 ProductType."""
        params = {}
        assert _get_product_type(params) == "naspost"


class TestProduct:
    """测试 PRODUCT dict."""

    def test_product_structure(self):
        """测试 PRODUCT 结构完整性."""
        required_fields = ["code", "name", "display_name", "product_type", "category", "params", "build_modules", "format_summary", "validate"]
        for field in required_fields:
            assert field in PRODUCT, f"Missing field: {field}"

    def test_params_length(self):
        """测试参数数量."""
        assert len(PRODUCT["params"]) == 7

    def test_param_names(self):
        """测试参数名称."""
        param_names = [p["name"] for p in PRODUCT["params"]]
        expected_names = ["region", "file_system_type", "storage_type", "protocol_type", "capacity", "data_transfer", "subscription_type"]
        for name in expected_names:
            assert name in param_names, f"Missing param: {name}"
