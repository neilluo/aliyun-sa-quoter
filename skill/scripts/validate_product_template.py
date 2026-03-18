#!/usr/bin/env python3
"""
Product development validation template.

Run this script when developing a new product to ensure configuration is correct.

Usage:
    python3 validate_product_template.py products/myproduct.py
"""

import argparse
import importlib.util
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

import bss_client
from framework import registry


def validate_new_product(file_path: str) -> bool:
    """Validate a new product file before adding to registry."""
    print(f"\n{'='*80}")
    print(f"Validating: {file_path}")
    print('='*80)
    
    # Load the product module
    spec = importlib.util.spec_from_file_location("product", file_path)
    module = importlib.util.module_from_spec(spec)
    
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        print(f"❌ Failed to load module: {e}")
        return False
    
    # Get PRODUCT dict
    if not hasattr(module, 'PRODUCT'):
        print("❌ PRODUCT dict not found")
        return False
    
    product = module.PRODUCT
    errors = []
    warnings = []
    
    # 1. Validate required fields
    required_fields = ['code', 'name', 'display_name', 'product_type', 'category', 
                       'params', 'build_modules', 'format_summary']
    for field in required_fields:
        if field not in product:
            errors.append(f"Missing required field: {field}")
    
    if errors:
        for e in errors:
            print(f"❌ {e}")
        return False
    
    code = product['code']
    bss_code = product.get('bss_product_code', code)
    raw_product_type = product.get('product_type')
    
    # Resolve product type if it's a function
    if callable(raw_product_type):
        # Build test params for product type resolution
        test_params = {}
        for p in product.get('params', []):
            if p.get('default') is not None:
                test_params[p['name']] = p['default']
            elif p.get('examples'):
                test_params[p['name']] = p['examples'][0]
        product_type = raw_product_type(test_params)
    else:
        product_type = raw_product_type
    
    print(f"\n1. Product Code: {code}")
    print(f"   BSS API Code: {bss_code}")
    print(f"   Product Type: {product_type}")
    
    # 2. Validate BSS API connectivity
    try:
        client = bss_client.create_client()
        print("\n2. BSS API Connection: ✅ OK")
    except Exception as e:
        print(f"\n2. BSS API Connection: ❌ Failed - {e}")
        return False
    
    # 3. Validate ProductCode exists
    try:
        api_products = bss_client.query_product_list(client, page_size=100)
        api_codes = {p['product_code'] for p in api_products}
        
        if bss_code in api_codes:
            print(f"\n3. Product Code Validation: ✅ '{bss_code}' exists in BSS API")
        else:
            print(f"\n3. Product Code Validation: ❌ '{bss_code}' NOT found in BSS API")
            print(f"   Available codes: {sorted(api_codes)[:20]}...")  # Show first 20
            errors.append(f"ProductCode '{bss_code}' not in BSS API")
    except Exception as e:
        print(f"\n3. Product Code Validation: ❌ Failed - {e}")
        errors.append(f"Failed to query BSS API: {e}")
    
    if errors:
        print("\n" + "="*80)
        print("VALIDATION FAILED")
        print("="*80)
        return False
    
    # 4. Validate modules (if product code exists)
    print("\n4. Module Validation:")
    try:
        # Get valid modules from BSS API
        from ai_friendly.constants import BillingType
        
        # Handle product_type (None vs "" vs "xxx")
        if product_type is None:
            # Try without ProductType first
            try:
                valid_modules = bss_client.describe_pricing_modules(
                    client, bss_code, BillingType.SUBSCRIPTION, None
                )
            except Exception:
                # Try with empty string
                valid_modules = bss_client.describe_pricing_modules(
                    client, bss_code, BillingType.SUBSCRIPTION, ""
                )
        else:
            valid_modules = bss_client.describe_pricing_modules(
                client, bss_code, BillingType.SUBSCRIPTION, product_type
            )
        valid_codes = {m['module_code'] for m in valid_modules}
        print(f"   BSS API modules: {sorted(valid_codes)}")
        
        # Build test modules
        params = {}
        for p in product.get('params', []):
            if p.get('default') is not None:
                params[p['name']] = p['default']
            elif p.get('examples'):
                params[p['name']] = p['examples'][0]
        
        try:
            modules = product['build_modules'](params)
            print(f"   Generated modules: {[m['module_code'] for m in modules]}")
            
            # Check each module
            for m in modules:
                if m['module_code'] in valid_codes:
                    print(f"   ✅ {m['module_code']}: OK")
                else:
                    print(f"   ⚠️  {m['module_code']}: Not in BSS API (may be attribute)")
                    warnings.append(f"Module '{m['module_code']}' not in BSS API")
        except Exception as e:
            print(f"   ❌ Failed to build modules: {e}")
            errors.append(f"Module build failed: {e}")
    except Exception as e:
        print(f"   ❌ Failed to get valid modules: {e}")
        warnings.append(f"Could not validate modules: {e}")
    
    # 5. Test price query
    print("\n5. Price Query Test:")
    try:
        from ai_friendly.constants import BillingType
        from framework.base import resolve_product_type
        
        # Resolve product type
        if callable(product_type):
            resolved_type = product_type(params)
        else:
            resolved_type = product_type
        
        # Try price query
        result = bss_client.get_subscription_price(
            client, bss_code, modules, 'cn-beijing', 1, 1, resolved_type
        )
        
        if result.get('module_details'):
            total = sum(md.get('original_cost', 0) or md.get('cost_after_discount', 0) 
                       for md in result['module_details'])
            print(f"   ✅ Price query successful: ¥{total:.2f}")
        else:
            print(f"   ⚠️  Price query returned no module details")
            warnings.append("Price query returned empty module details")
    except Exception as e:
        print(f"   ❌ Price query failed: {e}")
        errors.append(f"Price query failed: {e}")
    
    # Summary
    print("\n" + "="*80)
    if errors:
        print("VALIDATION FAILED")
        print("="*80)
        for e in errors:
            print(f"❌ {e}")
        return False
    elif warnings:
        print("VALIDATION PASSED WITH WARNINGS")
        print("="*80)
        for w in warnings:
            print(f"⚠️  {w}")
        return True
    else:
        print("VALIDATION PASSED")
        print("="*80)
        return True


def main():
    parser = argparse.ArgumentParser(description="Validate new product configuration")
    parser.add_argument("file", help="Path to product Python file")
    args = parser.parse_args()
    
    success = validate_new_product(args.file)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
