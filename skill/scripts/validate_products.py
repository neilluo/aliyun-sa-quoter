#!/usr/bin/env python3
"""
Product configuration validation script.

Validates that all registered products have correct ProductCode in BSS API.

Usage:
    python3 validate_products.py
    python3 validate_products.py --product ecs
"""

import argparse
import sys

import bss_client
from framework import registry


def main():
    parser = argparse.ArgumentParser(description="Validate product configurations")
    parser.add_argument("--product", help="Validate specific product only")
    args = parser.parse_args()
    
    # Create BSS client
    try:
        client = bss_client.create_client()
    except Exception as e:
        print(f"Error: Failed to create BSS client: {e}")
        sys.exit(1)
    
    # Get all products from BSS API
    try:
        api_products = bss_client.query_product_list(client, page_size=100)
        api_codes = set(p['product_code'] for p in api_products)
    except Exception as e:
        print(f"Error: Failed to query BSS API: {e}")
        sys.exit(1)
    
    # Get products to validate
    if args.product:
        product = registry.get_product(args.product)
        if not product:
            print(f"Error: Product '{args.product}' not found")
            sys.exit(1)
        products = [product]
    else:
        products = registry.list_products()
    
    # Validate each product
    print("\nProduct Code Validation:")
    print("=" * 80)
    
    errors = []
    for product in products:
        code = product["code"]
        
        # Skip local calculation products
        if code == "bailian":
            print(f"✅ {code:20} Local calculation product")
            continue
        
        # Check bss_product_code or code
        check_code = product.get("bss_product_code", code)
        
        if check_code in api_codes:
            print(f"✅ {code:20} OK (BSS: {check_code})")
        else:
            print(f"❌ {code:20} Not found in BSS API (checked: {check_code})")
            errors.append(code)
    
    print("=" * 80)
    
    if errors:
        print(f"\n❌ {len(errors)} products not found in BSS API: {', '.join(errors)}")
        sys.exit(1)
    else:
        print(f"\n✅ All products validated successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()
