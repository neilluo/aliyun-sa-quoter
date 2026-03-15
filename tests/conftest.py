"""
Shared test fixtures and helpers for aliyun-quoter tests.
"""

import os
import sys
import unittest

# Ensure skill/scripts is importable
_SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "skill", "scripts")
_SCRIPTS_DIR = os.path.abspath(_SCRIPTS_DIR)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)


# --- Credential detection ---

HAS_CREDENTIALS = bool(
    os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_ID", "").strip()
    and os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_SECRET", "").strip()
)

skip_without_credentials = unittest.skipUnless(
    HAS_CREDENTIALS, "需要阿里云 AK/SK 凭证 (ALIBABA_CLOUD_ACCESS_KEY_ID / ALIBABA_CLOUD_ACCESS_KEY_SECRET)"
)


def create_test_client():
    """Create a bss_client (ak, sk) tuple for integration tests.

    Only call this inside tests decorated with @skip_without_credentials.
    """
    import bss_client
    return bss_client.create_client()


# --- Product validation helpers ---

REQUIRED_PRODUCT_FIELDS = {"code", "name", "display_name", "params", "build_modules", "format_summary"}

REQUIRED_PARAM_FIELDS = {"name", "label", "type", "required"}


def assert_valid_product(test_case, product):
    """Assert that a PRODUCT dict has the correct structure.

    Args:
        test_case: unittest.TestCase instance (for assertions)
        product: PRODUCT dict to validate
    """
    test_case.assertIsInstance(product, dict)
    for field in REQUIRED_PRODUCT_FIELDS:
        test_case.assertIn(field, product, f"PRODUCT missing required field: {field}")

    test_case.assertIsInstance(product["code"], str)
    test_case.assertIsInstance(product["name"], str)
    test_case.assertIsInstance(product["display_name"], str)
    test_case.assertIsInstance(product["params"], list)
    test_case.assertTrue(callable(product["build_modules"]))
    test_case.assertTrue(callable(product["format_summary"]))

    if "validate" in product and product["validate"] is not None:
        test_case.assertTrue(callable(product["validate"]))

    # Validate each param definition
    for param in product["params"]:
        test_case.assertIsInstance(param, dict)
        for field in REQUIRED_PARAM_FIELDS:
            test_case.assertIn(field, param, f"Param missing required field: {field}")
        test_case.assertIn(param["type"], ("string", "int", "float"),
                           f"Invalid param type: {param['type']}")


def assert_valid_module_list(test_case, modules):
    """Assert that a module list has the correct structure.

    Args:
        test_case: unittest.TestCase instance
        modules: List of module dicts from build_modules()
    """
    test_case.assertIsInstance(modules, list)
    test_case.assertGreater(len(modules), 0, "module_list should not be empty")

    for m in modules:
        test_case.assertIsInstance(m, dict)
        test_case.assertIn("module_code", m)
        test_case.assertIn("config", m)
        test_case.assertIn("price_type", m)
        test_case.assertIsInstance(m["module_code"], str)
        test_case.assertIsInstance(m["config"], str)
        test_case.assertIsInstance(m["price_type"], str)
