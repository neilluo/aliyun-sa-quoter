#!/usr/bin/env python3
"""
Alibaba Cloud Quoter - Query product pricing via BSS OpenAPI.

Usage:
  quoter.py check                              Check AK/SK credentials
  quoter.py products [--category C]            List available products
  quoter.py modules <product> [--type T]       Describe pricing modules
  quoter.py info <product>                     Show product parameter definitions
  quoter.py price <product> --params '{}'      Query product price

Run from this file's directory.
"""

import argparse
import json
import sys
from pathlib import Path

# Ensure scripts directory is importable
sys.path.insert(0, str(Path(__file__).parent))

import bss_client
import formatters
import registry
from errors import (
    CredentialError, ProductNotFoundError, ValidationError,
    BssApiError, format_error,
)
from products._base import (
    resolve_product_type, fill_defaults, coerce_types, validate_params,
)


def cmd_check(args):
    """Check AK/SK credentials and API connectivity."""
    try:
        bss_client.check_credentials()
    except bss_client.CredentialError as e:
        print(str(e))
        return 1

    try:
        client = bss_client.create_client()
        products = bss_client.query_product_list(client)
        print(formatters.format_credential_check(True))
        print(f"成功连接阿里云 BSS API，获取到 {len(products)} 个产品。")
        return 0
    except bss_client.BssApiError as e:
        print(formatters.format_credential_check(False, str(e)))
        return 1
    except Exception as e:
        print(formatters.format_credential_check(False, str(e)))
        return 1


def cmd_products(args):
    """List registered products (from local product definitions)."""
    category = getattr(args, "category", None)
    if category:
        products = registry.list_products_by_category(category)
    else:
        products = registry.list_products()

    if not products:
        print("未找到已注册的产品。")
        return 1

    print(formatters.format_registered_products(products))
    return 0


def cmd_modules(args):
    """Describe pricing modules for a product via BSS API."""
    try:
        client = bss_client.create_client()
        modules = bss_client.describe_pricing_modules(
            client, args.product, args.type
        )
        print(formatters.format_pricing_modules(args.product, modules))
        return 0
    except bss_client.CredentialError as e:
        print(str(e))
        return 1
    except bss_client.BssApiError as e:
        print(f"错误: {e}")
        return 1


def cmd_info(args):
    """Show product parameter definitions."""
    product = registry.get_product(args.product)
    if not product:
        codes = registry.get_all_codes()
        print(f"错误: 未知产品 '{args.product}'。已注册产品: {', '.join(codes)}")
        return 1

    print(formatters.format_product_info(product))
    return 0


def cmd_price(args):
    """Query product price using registry-based architecture."""
    product_code = args.product

    # 1. Look up product definition
    product = registry.get_product(product_code)
    if not product:
        codes = registry.get_all_codes()
        print(f"错误: 未知产品 '{product_code}'。已注册产品: {', '.join(codes)}")
        return 1

    # 2. Parse --params JSON
    try:
        params = json.loads(args.params)
    except json.JSONDecodeError as e:
        print(f"错误: --params JSON 解析失败: {e}")
        print(f"示例: --params '{{\"instance_type\":\"ecs.g7.xlarge\"}}'")
        return 1

    # 3. Fill defaults
    fill_defaults(product, params)

    # 4. Type coercion
    coerce_types(product, params)

    # 5+6. Validate (required check + product rules)
    errors = validate_params(product, params)
    if errors:
        print(format_error(ValidationError(errors)))
        return 1

    # 7. Build modules
    try:
        modules = product["build_modules"](params)
    except Exception as e:
        print(f"错误: 参数构建失败: {e}")
        return 1

    # 8. Resolve ProductType
    product_type = resolve_product_type(product, params)

    # 9. Create client and call BSS API
    try:
        client = bss_client.create_client()
    except bss_client.CredentialError as e:
        print(str(e))
        return 1

    try:
        billing = args.billing

        if billing == "subscription":
            price_data = bss_client.get_subscription_price(
                client, product_code, modules,
                region=args.region,
                duration=args.duration,
                quantity=args.quantity,
                product_type=product_type,
            )
        else:
            price_data = bss_client.get_pay_as_you_go_price(
                client, product_code, modules,
                region=args.region,
                product_type=product_type,
            )

        # 10. Format output
        config_summary = product["format_summary"](params)
        result = formatters.format_price_result(
            product_name=product["display_name"],
            config_summary=config_summary,
            price_data=price_data,
            billing_method=billing,
            duration=args.duration if billing == "subscription" else None,
            quantity=args.quantity,
            region=args.region,
        )
        print(result)
        return 0

    except bss_client.BssApiError as e:
        print(f"错误: {e}")
        return 1
    except Exception as e:
        print(f"错误: 询价失败: {e}")
        return 1


def build_parser():
    """Build argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="quoter.py",
        description="阿里云产品报价查询工具 - 通过 BSS OpenAPI 查询精准价格",
    )
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # check
    subparsers.add_parser("check", help="检查 AK/SK 凭证和 API 连通性")

    # products
    p_products = subparsers.add_parser("products", help="列出已注册产品")
    p_products.add_argument("--category", default=None,
                            help="按分类筛选 (compute/database/network/storage/cdn_security/middleware)")

    # modules
    p_modules = subparsers.add_parser("modules", help="查询产品计价模块 (来自 BSS API)")
    p_modules.add_argument("product", help="产品代码")
    p_modules.add_argument("--type", default="Subscription",
                           choices=["Subscription", "PayAsYouGo"],
                           help="订阅类型 (默认: Subscription)")

    # info
    p_info = subparsers.add_parser("info", help="查看产品参数定义")
    p_info.add_argument("product", help="产品代码")

    # price
    p_price = subparsers.add_parser("price", help="查询产品价格")
    p_price.add_argument("product", help="产品代码")
    p_price.add_argument("--params", required=True,
                         help="产品参数 JSON，如 '{\"instance_type\":\"ecs.g7.xlarge\"}'")
    p_price.add_argument("--region", default="cn-hangzhou", help="地域 ID (默认: cn-hangzhou)")
    p_price.add_argument("--billing", default="subscription",
                         choices=["subscription", "payAsYouGo"],
                         help="计费方式 (默认: subscription)")
    p_price.add_argument("--duration", type=int, default=1, help="包月时长/月 (默认: 1)")
    p_price.add_argument("--quantity", type=int, default=1, help="数量 (默认: 1)")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    handlers = {
        "check": cmd_check,
        "products": cmd_products,
        "modules": cmd_modules,
        "info": cmd_info,
        "price": cmd_price,
    }

    handler = handlers.get(args.command)
    if handler:
        return handler(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main() or 0)
