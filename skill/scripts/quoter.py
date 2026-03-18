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
from concurrent.futures import ThreadPoolExecutor, as_completed

# Ensure scripts directory is importable
sys.path.insert(0, str(Path(__file__).parent))

import bss_client
import formatters
from framework import registry
from errors import (
    CredentialError, ProductNotFoundError, ValidationError,
    BssApiError, format_error,
)
from framework.base import (
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
        # Get product_type from registry if available
        product = registry.get_product(args.product)
        product_type = product.get("product_type") if product else None
        # Use bss_product_code if available (e.g., polardb -> drds)
        bss_product_code = product.get("bss_product_code", args.product) if product else args.product
        modules = bss_client.describe_pricing_modules(
            client, bss_product_code, args.type, product_type
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


def _is_local_calculation_product(modules):
    """Check if product uses local calculation (not BSS API)."""
    return modules and len(modules) == 1 and modules[0].get("module_code") == "__LOCAL_CALCULATION__"


def _format_bailian_price(result):
    """Format bailian price calculation result as Markdown.

    Args:
        result: dict from bailian.calculate_price()

    Returns Markdown string.
    """
    lines = ["# 百炼大模型报价", ""]

    # Configuration summary
    lines.append("## 配置摘要")
    lines.append(f"- 模型: {result['model']}")
    lines.append(f"- 地域: {result['region']}")
    lines.append(f"- 输入 Token: {result['input_tokens']:,}")
    lines.append(f"- 输出 Token: {result['output_tokens']:,}")
    lines.append(f"- 思考模式: {'是' if result['thinking'] else '否'}")
    lines.append(f"- Batch 调用: {'是' if result['batch'] else '否'}")
    if result.get("context_cache"):
        lines.append(f"- 上下文缓存: 是")
    lines.append("")

    # Price breakdown
    lines.append("## 价格明细")
    lines.append("| 项目 | Token 数 | 单价(元/百万) | 小计(元) |")
    lines.append("|------|---------|--------------|---------|")
    lines.append(f"| 输入 | {result['input_tokens']:,} | {result['input_unit_price']:.2f} | {result['input_price']:.2f} |")
    lines.append(f"| 输出 | {result['output_tokens']:,} | {result['output_unit_price']:.2f} | {result['output_price']:.2f} |")
    lines.append("")

    # Discounts
    if result.get("discounts_applied"):
        lines.append("### 已应用折扣")
        for discount in result["discounts_applied"]:
            lines.append(f"- {discount}")
        lines.append("")

    # Total
    lines.append("## 总价")
    lines.append(f"**{result['total_price']:.2f} 元**")
    lines.append("")

    # Footer
    lines.append("---")
    lines.append("价格数据最后更新: 2026-03-11")

    return "\n".join(lines)


def _parse_params(params_str):
    """Parse params JSON - supports single object or array."""
    try:
        data = json.loads(params_str)
        if isinstance(data, list):
            return data
        return [data]
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")


def _query_single_sync(product_code, params, product, billing, region, duration, quantity):
    """Execute a single price query (synchronous version for batch)."""
    # 7. Build modules
    modules = product["build_modules"](params)

    # 8. Check if this is a local calculation product (e.g., bailian)
    if _is_local_calculation_product(modules):
        from products.bailian import calculate_price
        result = calculate_price(params)
        return {
            "type": "local",
            "config_summary": product["format_summary"](params),
            "result": result,
            "total": result.get("total_price", 0),
        }

    # 9. Resolve ProductType
    product_type = resolve_product_type(product, params)

    # 10. Get BSS API ProductCode
    bss_product_code = product.get("bss_product_code", product_code)

    # 11. Create client and call BSS API
    client = bss_client.create_client()

    if billing == "subscription":
        price_data = bss_client.get_subscription_price(
            client, bss_product_code, modules,
            region=region,
            duration=duration,
            quantity=quantity,
            product_type=product_type,
        )
    else:
        price_data = bss_client.get_pay_as_you_go_price(
            client, bss_product_code, modules,
            region=region,
            product_type=product_type,
        )

    config_summary = product["format_summary"](params)

    # Calculate total from module_details
    original = price_data.get("original_amount")
    trade = price_data.get("trade_amount")

    if original is None and price_data.get("module_details"):
        original = sum(
            (md.get("original_cost") or 0) for md in price_data["module_details"]
        )
    if trade is None and price_data.get("module_details"):
        trade = sum(
            (md.get("cost_after_discount") or md.get("original_cost") or 0)
            for md in price_data["module_details"]
        )

    original = original or 0
    trade = trade or 0

    # Extract module prices
    instance_price = 0
    disk_price = 0
    for md in price_data.get("module_details", []):
        cost = md.get("cost_after_discount") or md.get("original_cost") or 0
        if md["module_code"] == "InstanceType":
            instance_price = float(cost)
        elif md["module_code"] in ("SystemDisk", "DataDisk"):
            disk_price += float(cost)

    return {
        "type": "bss",
        "config_summary": config_summary,
        "price_data": price_data,
        "instance_price": instance_price,
        "disk_price": disk_price,
        "total": trade,
        "original": original,
    }


def _query_batch(product_code, params_list, args):
    """Execute batch queries with concurrency."""
    product = registry.get_product(product_code)

    results = []
    errors = []

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_idx = {
            executor.submit(
                _query_single_sync,
                product_code,
                params,
                product,
                args.billing,
                args.region,
                args.duration,
                args.quantity
            ): idx
            for idx, params in enumerate(params_list)
        }

        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            try:
                result = future.result()
                results.append((idx, result))
            except Exception as e:
                errors.append((idx, str(e)))

    results.sort(key=lambda x: x[0])

    return formatters.format_batch_results(
        product["display_name"],
        results,
        errors,
        args.billing,
        args.duration,
        args.quantity,
        args.region,
    )


def cmd_price(args):
    """Query product price - supports batch query."""
    product_code = args.product

    # 1. Look up product definition
    product = registry.get_product(product_code)
    if not product:
        codes = registry.get_all_codes()
        print(f"错误: 未知产品 '{product_code}'。已注册产品: {', '.join(codes)}")
        return 1

    # 2. Parse --params JSON (supports single object or array)
    try:
        params_list = _parse_params(args.params)
    except ValueError as e:
        print(f"错误: --params JSON 解析失败: {e}")
        print(f"示例: --params '{{\"instance_type\":\"ecs.g7.xlarge\"}}'")
        return 1

    # 3. Add exclude_system_disk to each params if specified
    if getattr(args, "exclude_system_disk", False):
        for params in params_list:
            params["exclude_system_disk"] = True

    # 4. Single query - keep existing logic
    if len(params_list) == 1:
        params = params_list[0]

        # Fill defaults
        fill_defaults(product, params)

        # Type coercion
        coerce_types(product, params)

        # Validate
        errors = validate_params(product, params)
        if errors:
            print(format_error(ValidationError(errors)))
            return 1

        # Build modules
        try:
            modules = product["build_modules"](params)
        except Exception as e:
            print(f"错误: 参数构建失败: {e}")
            return 1

        # Check local calculation
        if _is_local_calculation_product(modules):
            try:
                from products.bailian import calculate_price
                result = calculate_price(params)
                print(_format_bailian_price(result))
                return 0
            except Exception as e:
                print(f"错误: 价格计算失败: {e}")
                return 1

        # Resolve ProductType
        product_type = resolve_product_type(product, params)

        # Get BSS API ProductCode
        bss_product_code = product.get("bss_product_code", product_code)

        # Create client and call BSS API
        try:
            client = bss_client.create_client()
        except bss_client.CredentialError as e:
            print(str(e))
            return 1

        try:
            billing = args.billing

            if billing == "subscription":
                price_data = bss_client.get_subscription_price(
                    client, bss_product_code, modules,
                    region=args.region,
                    duration=args.duration,
                    quantity=args.quantity,
                    product_type=product_type,
                )
            else:
                price_data = bss_client.get_pay_as_you_go_price(
                    client, bss_product_code, modules,
                    region=args.region,
                    product_type=product_type,
                )

            # Format output
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

    # 5. Batch query - concurrent execution
    else:
        # Validate all params first
        for idx, params in enumerate(params_list):
            fill_defaults(product, params)
            coerce_types(product, params)
            errors = validate_params(product, params)
            if errors:
                print(f"错误: 配置 {idx + 1} 参数验证失败:")
                print(format_error(ValidationError(errors)))
                return 1

        try:
            result = _query_batch(product_code, params_list, args)
            print(result)
            return 0
        except bss_client.CredentialError as e:
            print(str(e))
            return 1
        except Exception as e:
            print(f"错误: 批量询价失败: {e}")
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
                         help="产品参数 JSON，支持单对象或数组，如 '{\"instance_type\":\"ecs.g7.xlarge\"}' 或 '[{...}, {...}]'")
    p_price.add_argument("--region", default="cn-hangzhou", help="地域 ID (默认: cn-hangzhou)")
    p_price.add_argument("--billing", default="subscription",
                         choices=["subscription", "payAsYouGo"],
                         help="计费方式 (默认: subscription)")
    p_price.add_argument("--duration", type=int, default=1, help="包月时长/月 (默认: 1)")
    p_price.add_argument("--quantity", type=int, default=1, help="数量 (默认: 1)")
    p_price.add_argument("--exclude-system-disk", action="store_true",
                         help="排除系统盘价格（仅 ECS），SystemDisk 价格将设为 0")

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
