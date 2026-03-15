"""
Tests for errors module - error classes and friendly error lookup.
"""

import sys
import os
import unittest

_SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "skill", "scripts")
_SCRIPTS_DIR = os.path.abspath(_SCRIPTS_DIR)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from errors import (
    QuoterError, CredentialError, ProductNotFoundError,
    ValidationError, BssApiError, NetworkError,
    get_friendly_error, format_error,
)


class TestErrorHierarchy(unittest.TestCase):
    """Test exception class hierarchy."""

    def test_all_inherit_quoter_error(self):
        self.assertTrue(issubclass(CredentialError, QuoterError))
        self.assertTrue(issubclass(ProductNotFoundError, QuoterError))
        self.assertTrue(issubclass(ValidationError, QuoterError))
        self.assertTrue(issubclass(BssApiError, QuoterError))
        self.assertTrue(issubclass(NetworkError, QuoterError))

    def test_validation_error_stores_list(self):
        e = ValidationError(["err1", "err2"])
        self.assertEqual(e.errors, ["err1", "err2"])

    def test_validation_error_wraps_string(self):
        e = ValidationError("single error")
        self.assertEqual(e.errors, ["single error"])

    def test_bss_api_error_attributes(self):
        e = BssApiError("test", code="E001", suggestion="try again")
        self.assertEqual(e.code, "E001")
        self.assertEqual(e.suggestion, "try again")


class TestGetFriendlyError(unittest.TestCase):
    """Test error code lookup from error_codes.json."""

    def test_known_code(self):
        msg, suggestion = get_friendly_error("PRICING_PLAN_RESULT_NOT_FOUND")
        self.assertIn("不可用", msg)
        self.assertTrue(len(suggestion) > 0)

    def test_unknown_code_returns_default(self):
        msg, suggestion = get_friendly_error("UNKNOWN_CODE_XYZ", "fallback msg")
        self.assertEqual(msg, "fallback msg")
        self.assertEqual(suggestion, "")

    def test_product_not_find(self):
        msg, _ = get_friendly_error("ProductNotFind")
        self.assertIn("产品", msg)

    def test_invalid_access_key(self):
        msg, suggestion = get_friendly_error("InvalidAccessKeyId.NotFound")
        self.assertIn("AccessKeyId", msg)
        self.assertTrue(len(suggestion) > 0)


class TestFormatError(unittest.TestCase):
    """Test format_error() output."""

    def test_validation_error_format(self):
        e = ValidationError(["缺少参数 A", "参数 B 无效"])
        result = format_error(e)
        self.assertIn("参数验证失败", result)
        self.assertIn("缺少参数 A", result)
        self.assertIn("参数 B 无效", result)

    def test_credential_error_format(self):
        e = CredentialError("AK/SK 未设置")
        result = format_error(e)
        self.assertIn("AK/SK 未设置", result)

    def test_product_not_found_error_format(self):
        e = ProductNotFoundError("产品 xyz 不存在")
        result = format_error(e)
        self.assertIn("xyz", result)

    def test_bss_api_error_with_suggestion(self):
        e = BssApiError("询价失败", code="E001", suggestion="检查参数")
        result = format_error(e)
        self.assertIn("E001", result)
        self.assertIn("检查参数", result)


if __name__ == "__main__":
    unittest.main()
