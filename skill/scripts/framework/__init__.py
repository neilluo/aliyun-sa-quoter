"""Framework core modules for aliyun-sa-quoter.

This package contains the core framework components:
- builders: ModuleBuilder DSL for constructing BSS modules
- validators: ValidationRule and Validator for parameter validation
- registry: Product auto-discovery and registration
- base: Base interfaces and helper functions
"""

from .builders import ModuleBuilder, create_builder, build_modules_from_specs
from .validators import (
    ValidationRule,
    Validator,
    create_range_validator,
    create_choices_validator,
    validate_required,
    validate_choices,
    validate_range,
)
from .base import (
    resolve_product_type,
    fill_defaults,
    coerce_types,
    check_required,
    validate_params,
)
from .registry import (
    discover_products,
    get_product,
    list_products,
    list_products_by_category,
    get_all_codes,
)

__all__ = [
    # Builders
    "ModuleBuilder",
    "create_builder",
    "build_modules_from_specs",
    # Validators
    "ValidationRule",
    "Validator",
    "create_range_validator",
    "create_choices_validator",
    "validate_required",
    "validate_choices",
    "validate_range",
    # Base
    "resolve_product_type",
    "fill_defaults",
    "coerce_types",
    "check_required",
    "validate_params",
    # Registry
    "discover_products",
    "get_product",
    "list_products",
    "list_products_by_category",
    "get_all_codes",
]
