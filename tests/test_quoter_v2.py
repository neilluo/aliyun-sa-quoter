"""
新版 quoter 测试 - 结合代码功能和实际测试场景

测试范围:
1. 参数解析 (_parse_params)
2. 批量查询 (_query_batch)
3. ECS 模块构建 (build_modules with exclude_system_disk)
4. 批量结果格式化 (format_batch_results)
5. 集成测试 (需要 AK/SK)
"""

import sys
import os
import unittest
import json
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skill", "scripts"))

# Import skip_without_credentials from conftest
import sys
conftest_path = os.path.join(os.path.dirname(__file__))
sys.path.insert(0, conftest_path)
from conftest import skip_without_credentials


class TestParseParams(unittest.TestCase):
    """Tests for _parse_params function."""

    def setUp(self):
        from quoter import _parse_params
        self.parse = _parse_params

    def test_single_object(self):
        """Should wrap single object in list."""
        result = self.parse('{"instance_type":"ecs.c6.4xlarge"}')
        self.assertEqual(result, [{"instance_type": "ecs.c6.4xlarge"}])

    def test_array(self):
        """Should return array as-is."""
        result = self.parse('[{"a":1},{"b":2}]')
        self.assertEqual(result, [{"a": 1}, {"b": 2}])

    def test_empty_array(self):
        """Should handle empty array."""
        result = self.parse('[]')
        self.assertEqual(result, [])

    def test_nested_object(self):
        """Should handle nested objects."""
        result = self.parse('{"instance_type":"ecs.c6.4xlarge","data_disk":{"size":100}}')
        self.assertEqual(result[0]["instance_type"], "ecs.c6.4xlarge")

    def test_invalid_json(self):
        """Should raise ValueError for invalid JSON."""
        with self.assertRaises(ValueError) as ctx:
            self.parse('invalid json')
        self.assertIn("Invalid JSON", str(ctx.exception))


class TestECSBuildModulesV2(unittest.TestCase):
    """Tests for ECS build_modules with new features."""

    def setUp(self):
        from products.ecs import build_modules
        self.build = build_modules

    def test_basic_config(self):
        """Basic config should have InstanceType + SystemDisk."""
        params = {"instance_type": "ecs.c6.4xlarge"}
        modules = self.build(params)
        codes = [m["module_code"] for m in modules]
        self.assertIn("InstanceType", codes)
        self.assertIn("SystemDisk", codes)
        self.assertEqual(len(modules), 2)

    def test_exclude_system_disk(self):
        """exclude_system_disk=True should set SystemDisk.Size=0."""
        params = {
            "instance_type": "ecs.c6.4xlarge",
            "exclude_system_disk": True,
        }
        modules = self.build(params)
        sd_module = next(m for m in modules if m["module_code"] == "SystemDisk")
        self.assertIn("SystemDisk.Size:0", sd_module["config"])

    def test_exclude_system_disk_with_data_disk(self):
        """Can exclude system disk but keep data disk."""
        params = {
            "instance_type": "ecs.c6.4xlarge",
            "exclude_system_disk": True,
            "data_disk_size": 500,
        }
        modules = self.build(params)
        codes = [m["module_code"] for m in modules]
        self.assertIn("InstanceType", codes)
        self.assertIn("SystemDisk", codes)
        self.assertIn("DataDisk", codes)
        
        sd_module = next(m for m in modules if m["module_code"] == "SystemDisk")
        self.assertIn("SystemDisk.Size:0", sd_module["config"])

    def test_normal_system_disk(self):
        """Default should have normal system disk size."""
        params = {
            "instance_type": "ecs.c6.4xlarge",
            "system_disk_size": 100,
        }
        modules = self.build(params)
        sd_module = next(m for m in modules if m["module_code"] == "SystemDisk")
        self.assertIn("SystemDisk.Size:100", sd_module["config"])

    def test_data_disk_only(self):
        """Can have data disk without system disk (when excluded)."""
        params = {
            "instance_type": "ecs.c6.4xlarge",
            "exclude_system_disk": True,
            "data_disk_size": 200,
        }
        modules = self.build(params)
        dd_module = next(m for m in modules if m["module_code"] == "DataDisk")
        self.assertIn("DataDisk.Size:200", dd_module["config"])


class TestFormatBatchResults(unittest.TestCase):
    """Tests for format_batch_results function."""

    def setUp(self):
        from formatters import format_batch_results
        self.format = format_batch_results

    def test_basic_batch_output(self):
        """Should format multiple results as table."""
        results = [
            (0, {
                "config_summary": {"实例规格": "ecs.c6.4xlarge"},
                "instance_price": 1496.0,
                "disk_price": 100.0,
                "total": 1596.0,
            }),
            (1, {
                "config_summary": {"实例规格": "ecs.r9i.2xlarge"},
                "instance_price": 1269.91,
                "disk_price": 200.0,
                "total": 1469.91,
            }),
        ]
        errors = []
        output = self.format("ECS", results, errors, "subscription", duration=1, quantity=1, region="cn-beijing")
        
        self.assertIn("批量报价结果", output)
        self.assertIn("ecs.c6.4xlarge", output)
        self.assertIn("ecs.r9i.2xlarge", output)
        self.assertIn("1496.00", output)
        self.assertIn("1269.91", output)

    def test_batch_with_errors(self):
        """Should include error section when some queries fail."""
        results = [
            (0, {
                "config_summary": {"实例规格": "ecs.c6.4xlarge"},
                "instance_price": 1496.0,
                "disk_price": 0.0,
                "total": 1496.0,
            }),
        ]
        errors = [(1, "Invalid instance type: ecs.invalid.xlarge")]
        output = self.format("ECS", results, errors, "subscription")
        
        self.assertIn("错误", output)
        self.assertIn("配置 2", output)
        self.assertIn("Invalid instance type", output)

    def test_batch_with_quantity(self):
        """Should multiply total by quantity."""
        results = [
            (0, {
                "config_summary": {"实例规格": "ecs.c6.4xlarge"},
                "instance_price": 1000.0,
                "disk_price": 0.0,
                "total": 1000.0,
            }),
        ]
        output = self.format("ECS", results, [], "subscription", duration=1, quantity=3)
        self.assertIn("3000.00", output)  # 1000 * 3

    def test_yearly_billing_text(self):
        """Should show yearly billing text."""
        results = []
        output = self.format("ECS", results, [], "subscription", duration=12)
        self.assertIn("1年", output)

    def test_empty_results(self):
        """Should handle empty results gracefully."""
        output = self.format("ECS", [], [], "subscription", duration=1)
        self.assertIn("批量报价结果", output)
        self.assertIn("总计", output)


class TestQuoterIntegration(unittest.TestCase):
    """Integration tests requiring real BSS API calls."""

    @skip_without_credentials
    def test_single_query_exclude_system_disk(self):
        """Real API: Query ECS with exclude_system_disk."""
        import subprocess
        result = subprocess.run(
            [
                "python3", "skill/scripts/quoter.py", "price", "ecs",
                "--params", '{"instance_type":"ecs.c6.4xlarge","exclude_system_disk":true}',
                "--region", "cn-beijing",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("应付金额", result.stdout)
        # SystemDisk should be 0 or not present in breakdown
        lines = result.stdout.split("\n")
        system_disk_lines = [l for l in lines if "SystemDisk" in l and "应付金额" not in l]
        if system_disk_lines:
            # If SystemDisk is shown, it should be 0
            self.assertIn("0.00", system_disk_lines[0])

    @skip_without_credentials
    def test_batch_query_real_api(self):
        """Real API: Batch query multiple instances."""
        import subprocess
        result = subprocess.run(
            [
                "python3", "skill/scripts/quoter.py", "price", "ecs",
                "--params", '[{"instance_type":"ecs.c6.4xlarge"},{"instance_type":"ecs.r9i.2xlarge"}]',
                "--region", "cn-beijing",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("批量报价结果", result.stdout)
        self.assertIn("ecs.c6.4xlarge", result.stdout)
        self.assertIn("ecs.r9i.2xlarge", result.stdout)
        self.assertIn("总计", result.stdout)


if __name__ == "__main__":
    unittest.main()