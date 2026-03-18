"""
Product definition interface and helper utilities.

Every product file (e.g. ecs.py, rds.py) must export a module-level
PRODUCT dict following this interface:

PRODUCT = {
    # === Metadata ===
    "code": str,               # BSS ProductCode, e.g. "ecs"
    "name": str,               # Short English name, e.g. "ECS"
    "display_name": str,       # Chinese display name, e.g. "ECS 云服务器"
    "product_type": ...,       # str | None | callable(params_dict) -> str|None
    "category": str,           # "compute" | "database" | "network" | "storage" | "cdn_security" | "middleware"

    # === Parameter definitions ===
    "params": [
        {
            "name": str,       # JSON key, e.g. "instance_type"
            "label": str,      # Chinese label, e.g. "实例规格"
            "type": str,       # "string" | "int" | "float"
            "required": bool,  # Whether this param is mandatory
            "default": any,    # Default value (None = no default)
            "choices": list|None,  # None = free input, list = valid values
            "description": str,    # Description (for AI)
            "examples": list,      # Example values
        },
        ...
    ],

    # === Functions ===
    "build_modules": callable,    # fn(params_dict) -> list[module_dict]
    "format_summary": callable,   # fn(params_dict) -> dict[str, str]
    "validate": callable | None,  # fn(params_dict) -> list[str] (errors, empty=pass)
}

Module dict format (returned by build_modules):
    {"module_code": str, "config": str, "price_type": str}
"""


def resolve_product_type(product, params):
    """Resolve the ProductType for a product given params.

    Args:
        product: PRODUCT dict
        params: User parameter dict

    Returns:
        ProductType string or None.
    """
    pt = product.get("product_type")
    if pt is None:
        return None
    if callable(pt):
        return pt(params)
    return pt


def fill_defaults(product, params):
    """Fill in default values for missing optional parameters.

    Args:
        product: PRODUCT dict
        params: User parameter dict (modified in place)

    Returns:
        params dict with defaults filled in.
    """
    for p in product.get("params", []):
        name = p["name"]
        if name not in params and p.get("default") is not None:
            params[name] = p["default"]
    return params


def coerce_types(product, params):
    """Convert parameter values to their declared types.

    Args:
        product: PRODUCT dict
        params: User parameter dict (modified in place)

    Returns:
        params dict with types coerced.
    """
    type_map = {"string": str, "int": int, "float": float, "bool": bool}

    for p in product.get("params", []):
        name = p["name"]
        if name in params and params[name] is not None:
            target_type = type_map.get(p.get("type", "string"), str)
            try:
                params[name] = target_type(params[name])
            except (ValueError, TypeError):
                pass  # Will be caught by validation
    return params


def check_required(product, params):
    """Check that all required parameters are present.

    Returns:
        List of error strings (empty = all present).
    """
    errors = []
    for p in product.get("params", []):
        if p.get("required") and p["name"] not in params:
            errors.append(f"缺少必填参数: {p['label']} ({p['name']})")
    return errors


def validate_params(product, params):
    """Run full parameter validation: required check + product-specific rules.

    Returns:
        List of error strings (empty = valid).
    """
    errors = check_required(product, params)

    # Check choices
    for p in product.get("params", []):
        name = p["name"]
        choices = p.get("choices")
        if choices and name in params and params[name] not in choices:
            errors.append(
                f"参数 {p['label']} ({name}) 的值 '{params[name]}' 无效，"
                f"可选值: {', '.join(str(c) for c in choices)}"
            )

    # Product-specific validation
    validate_fn = product.get("validate")
    if validate_fn:
        product_errors = validate_fn(params)
        if product_errors:
            errors.extend(product_errors)

    return errors
