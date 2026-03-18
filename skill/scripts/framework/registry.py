"""
Product auto-discovery and registration.

Scans products/*.py, extracts PRODUCT dicts, and registers them
in a global registry for lookup by product code.
"""

import importlib
import os
import sys
from pathlib import Path


_REGISTRY = {}

# Cache for BSS API product list
_BSS_PRODUCTS_CACHE = None


def _get_bss_products():
    """Get product list from BSS API (cached)."""
    global _BSS_PRODUCTS_CACHE
    if _BSS_PRODUCTS_CACHE is not None:
        return _BSS_PRODUCTS_CACHE
    
    # Only validate if credentials are available
    if not os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_ID"):
        return None
    
    try:
        # Lazy import to avoid circular dependency
        import bss_client
        client = bss_client.create_client()
        products = bss_client.query_product_list(client, page_size=100)
        _BSS_PRODUCTS_CACHE = {p['product_code'] for p in products}
        return _BSS_PRODUCTS_CACHE
    except Exception:
        return None

# Required fields in every PRODUCT dict
_REQUIRED_FIELDS = {"code", "name", "display_name", "params", "build_modules", "format_summary"}


def _validate_product(product, source_file):
    """Validate that a PRODUCT dict has all required fields.

    Returns list of error strings (empty = valid).
    """
    errors = []
    if not isinstance(product, dict):
        return [f"{source_file}: PRODUCT is not a dict"]

    for field in _REQUIRED_FIELDS:
        if field not in product:
            errors.append(f"{source_file}: missing required field '{field}'")

    if "code" in product and not isinstance(product["code"], str):
        errors.append(f"{source_file}: 'code' must be a string")

    if "params" in product and not isinstance(product["params"], list):
        errors.append(f"{source_file}: 'params' must be a list")

    if "build_modules" in product and not callable(product["build_modules"]):
        errors.append(f"{source_file}: 'build_modules' must be callable")

    if "format_summary" in product and not callable(product["format_summary"]):
        errors.append(f"{source_file}: 'format_summary' must be callable")

    if "validate" in product and product["validate"] is not None:
        if not callable(product["validate"]):
            errors.append(f"{source_file}: 'validate' must be callable or None")
    
    # Validate BSS API product code (if available)
    if "code" in product:
        code = product["code"]
        bss_code = product.get("bss_product_code", code)
        
        # Skip local calculation products
        if code != "bailian":
            bss_products = _get_bss_products()
            if bss_products is not None and bss_code not in bss_products:
                errors.append(f"{source_file}: ProductCode '{bss_code}' not found in BSS API")

    return errors


def discover_products():
    """Scan products/ directory and register all valid PRODUCT dicts.

    This function is idempotent - safe to call multiple times.
    """
    global _REGISTRY

    products_dir = Path(__file__).parent.parent / "products"
    if not products_dir.is_dir():
        print(f"警告: 产品目录不存在: {products_dir}", file=sys.stderr)
        return

    # Ensure products package is importable
    scripts_dir = str(Path(__file__).parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)

    for py_file in sorted(products_dir.glob("*.py")):
        # Skip __init__.py, _base.py, and other private files
        if py_file.name.startswith("_"):
            continue

        module_name = f"products.{py_file.stem}"

        try:
            # Import or reload the module
            if module_name in sys.modules:
                module = importlib.reload(sys.modules[module_name])
            else:
                module = importlib.import_module(module_name)

            # Check for PRODUCT dict
            product = getattr(module, "PRODUCT", None)
            if product is None:
                print(f"警告: {py_file.name} 缺少 PRODUCT 定义，跳过", file=sys.stderr)
                continue

            # Validate
            errors = _validate_product(product, py_file.name)
            if errors:
                for err in errors:
                    print(f"警告: {err}", file=sys.stderr)
                continue

            # Register
            code = product["code"]
            _REGISTRY[code] = product

        except Exception as e:
            print(f"警告: 加载 {py_file.name} 失败: {e}", file=sys.stderr)
            continue


def get_product(code):
    """Get product definition by product code.

    Args:
        code: Product code, e.g. "ecs", "rds"

    Returns:
        PRODUCT dict or None if not found.
    """
    if not _REGISTRY:
        discover_products()
    return _REGISTRY.get(code)


def list_products():
    """List all registered products.

    Returns:
        List of PRODUCT dicts.
    """
    if not _REGISTRY:
        discover_products()
    return list(_REGISTRY.values())


def list_products_by_category(category):
    """List products filtered by category.

    Args:
        category: e.g. "compute", "database", "network"

    Returns:
        List of PRODUCT dicts in that category.
    """
    if not _REGISTRY:
        discover_products()
    return [p for p in _REGISTRY.values() if p.get("category") == category]


def get_all_codes():
    """Get list of all registered product codes."""
    if not _REGISTRY:
        discover_products()
    return sorted(_REGISTRY.keys())
