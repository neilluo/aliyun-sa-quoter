"""
Output formatters for BSS pricing results.

Converts raw API response dicts into human-readable Markdown text.
"""

import json
from pathlib import Path

# Load region name mapping
_REGIONS_FILE = Path(__file__).parent.parent / "meta" / "regions.json"
_REGIONS = {}

if _REGIONS_FILE.exists():
    with open(_REGIONS_FILE, "r", encoding="utf-8") as f:
        _REGIONS = json.load(f)


def get_region_name(region_id):
    """Get human-readable region name from region id."""
    return _REGIONS.get(region_id, region_id)


def format_price_result(product_name, config_summary, price_data, billing_method,
                        duration=None, quantity=1, region=None):
    """Format a price query result as Markdown.

    Args:
        product_name: e.g. "ECS 云服务器"
        config_summary: dict of {label: value} for configuration display
        price_data: dict from bss_client (original_amount, trade_amount, module_details, etc.)
        billing_method: "subscription" or "payAsYouGo"
        duration: months (for subscription)
        quantity: number of instances
        region: region id

    Returns Markdown string.
    """
    lines = [f"## {product_name}报价", ""]

    # Configuration table
    lines.append("| 项目 | 配置 |")
    lines.append("|------|------|")
    if region:
        lines.append(f"| 地域 | {get_region_name(region)} ({region}) |")
    for label, value in config_summary.items():
        lines.append(f"| {label} | {value} |")

    billing_text = "包年包月" if billing_method == "subscription" else "按量付费"
    if billing_method == "subscription" and duration:
        if duration >= 12 and duration % 12 == 0:
            billing_text += f" / {duration // 12}年"
        else:
            billing_text += f" / {duration}个月"
    lines.append(f"| 计费方式 | {billing_text} |")
    if quantity > 1:
        lines.append(f"| 数量 | {quantity} |")
    lines.append("")

    # Price breakdown table
    if price_data.get("module_details"):
        lines.append("| 计费项 | 金额 (元) |")
        lines.append("|--------|----------|")
        for md in price_data["module_details"]:
            cost = md.get("cost_after_discount") or md.get("original_cost") or 0
            if cost and float(cost) > 0:
                lines.append(f"| {md['module_code']} | {float(cost):.2f} |")

    # Total - calculate from module_details if top-level fields are null
    # BSS API may return null for OriginalAmount/TradeAmount for some products (e.g., ECS)
    # In such cases, we aggregate from module_details
    original = price_data.get("original_amount")
    trade = price_data.get("trade_amount")
    discount = price_data.get("discount_amount") or 0

    # If top-level amounts are null, calculate from module_details
    if original is None and price_data.get("module_details"):
        original = sum(
            (md.get("original_cost") or 0) for md in price_data["module_details"]
        )
    if trade is None and price_data.get("module_details"):
        trade = sum(
            (md.get("cost_after_discount") or md.get("original_cost") or 0)
            for md in price_data["module_details"]
        )

    # Fallback to 0 if still None
    original = original or 0
    trade = trade or 0
    discount = discount or 0

    lines.append("")
    if float(discount) > 0:
        lines.append(f"| 原价 | {float(original):.2f} |")
        lines.append(f"| 优惠 | -{float(discount):.2f} |")
    lines.append(f"| **应付金额** | **{float(trade):.2f}** |")

    if quantity > 1:
        total = float(trade) * quantity
        lines.append(f"| **总计 (x{quantity})** | **{total:.2f}** |")

    lines.append("")
    currency = price_data.get("currency", "CNY")
    lines.append(f"货币: {currency}")

    return "\n".join(lines)


def format_product_list(products):
    """Format product list as Markdown table."""
    lines = ["## 可询价产品列表", ""]
    lines.append("| 产品代码 | 产品名称 | 产品类型 |")
    lines.append("|---------|---------|---------|")
    for p in products:
        lines.append(
            f"| {p['product_code']} | {p['product_name']} | {p.get('product_type', '-')} |"
        )
    lines.append("")
    lines.append(f"共 {len(products)} 个产品")
    return "\n".join(lines)


def format_pricing_modules(product_code, modules):
    """Format pricing module info as Markdown."""
    lines = [f"## {product_code} 计价模块", ""]

    if not modules:
        lines.append("未找到计价模块信息。")
        return "\n".join(lines)

    for m in modules:
        lines.append(f"### {m['module_code']}")
        if m.get("module_name"):
            lines.append(f"名称: {m['module_name']}")
        lines.append("")
        if m.get("config_list"):
            lines.append("可用配置项:")
            lines.append("")
            for c in m["config_list"]:
                lines.append(f"- `{c}`")
            lines.append("")

    return "\n".join(lines)


def format_registered_products(products):
    """Format locally registered product list as Markdown table.

    Args:
        products: list of PRODUCT dicts from registry.

    Returns Markdown string.
    """
    _CATEGORY_NAMES = {
        "compute": "计算",
        "database": "数据库",
        "network": "网络",
        "storage": "存储",
        "cdn_security": "CDN 与安全",
        "middleware": "中间件",
    }

    lines = ["## 已注册产品", ""]
    lines.append("| 产品代码 | 产品名称 | 分类 | 必填参数 |")
    lines.append("|---------|---------|------|---------|")

    for p in sorted(products, key=lambda x: (x.get("category", ""), x.get("code", ""))):
        cat = _CATEGORY_NAMES.get(p.get("category", ""), p.get("category", "-"))
        required_params = [
            pp["name"] for pp in p.get("params", []) if pp.get("required")
        ]
        req_str = ", ".join(required_params) if required_params else "-"
        lines.append(f"| {p['code']} | {p['display_name']} | {cat} | {req_str} |")

    lines.append("")
    lines.append(f"共 {len(products)} 个产品。使用 `quoter.py info <产品代码>` 查看详细参数。")
    return "\n".join(lines)


def format_product_info(product):
    """Format product parameter definitions as Markdown.

    Args:
        product: PRODUCT dict from registry.

    Returns Markdown string.
    """
    lines = [f"## {product['display_name']} ({product['code']})", ""]

    # Basic info
    pt = product.get("product_type")
    if pt is None:
        pt_display = "无"
    elif callable(pt):
        pt_display = "动态 (根据参数自动推断)"
    else:
        pt_display = pt
    lines.append(f"- **ProductCode**: `{product['code']}`")
    lines.append(f"- **ProductType**: {pt_display}")
    lines.append(f"- **分类**: {product.get('category', '-')}")
    lines.append("")

    # Parameters table
    params = product.get("params", [])
    if params:
        lines.append("### 参数定义")
        lines.append("")
        lines.append("| 参数名 | 说明 | 类型 | 必填 | 默认值 | 可选值 |")
        lines.append("|-------|------|------|------|-------|-------|")
        for p in params:
            name = p["name"]
            label = p.get("label", name)
            ptype = p.get("type", "string")
            required = "是" if p.get("required") else "否"
            default = p.get("default")
            default_str = str(default) if default is not None else "-"
            choices = p.get("choices")
            choices_str = ", ".join(str(c) for c in choices) if choices else "-"
            lines.append(f"| `{name}` | {label} | {ptype} | {required} | {default_str} | {choices_str} |")
        lines.append("")

    # Examples
    has_examples = any(p.get("examples") for p in params)
    if has_examples:
        lines.append("### 示例")
        lines.append("")
        # Build a minimal example JSON
        example = {}
        for p in params:
            if p.get("required") and p.get("examples"):
                example[p["name"]] = p["examples"][0]
            elif p.get("required"):
                example[p["name"]] = f"<{p['label']}>"
        example_json = json.dumps(example, ensure_ascii=False)
        lines.append(f"```bash")
        lines.append(f"quoter.py price {product['code']} --params '{example_json}'")
        lines.append(f"```")
        lines.append("")

    return "\n".join(lines)


def format_credential_check(success, message=""):
    """Format credential check result."""
    if success:
        return "凭证检查通过。AK/SK 已配置且 API 可连通。"
    else:
        return f"凭证检查失败: {message}"


def format_batch_results(product_name, results, errors, billing_method,
                         duration=None, quantity=1, region=None):
    """Format batch query results as Markdown table.

    Args:
        product_name: e.g. "ECS 云服务器"
        results: list of (idx, result_dict) tuples
        errors: list of (idx, error_msg) tuples
        billing_method: "subscription" or "payAsYouGo"
        duration: months (for subscription)
        quantity: number of instances
        region: region id

    Returns Markdown string.
    """
    lines = [f"## {product_name}批量报价结果", ""]

    # Billing info
    billing_text = "包年包月" if billing_method == "subscription" else "按量付费"
    if billing_method == "subscription" and duration:
        if duration >= 12 and duration % 12 == 0:
            billing_text += f" / {duration // 12}年"
        else:
            billing_text += f" / {duration}个月"
    lines.append(f"**计费方式**: {billing_text}")
    if region:
        lines.append(f"**地域**: {get_region_name(region)} ({region})")
    if quantity > 1:
        lines.append(f"**数量**: {quantity}")
    lines.append("")

    # Summary table
    lines.append("| 序号 | 配置 | 实例价格 | 数据盘 | 总计 |")
    lines.append("|------|------|---------|--------|------|")

    total_monthly = 0
    for idx, result in results:
        # Extract prices from result
        instance_price = result.get("instance_price", 0)
        disk_price = result.get("disk_price", 0)
        subtotal = result.get("total", 0)
        config_summary = result.get("config_summary", {})

        # Get instance type from config summary
        instance_type = config_summary.get("实例规格", "-")

        lines.append(f"| {idx + 1} | {instance_type} | ¥{float(instance_price):.2f} | ¥{float(disk_price):.2f} | ¥{float(subtotal):.2f} |")
        total_monthly += float(subtotal)

    lines.append("")

    # Apply quantity multiplier
    total_all = total_monthly * quantity
    lines.append(f"**总计**: ¥{total_all:.2f}/月")

    # Error summary
    if errors:
        lines.append("")
        lines.append("## 错误")
        for idx, error in errors:
            lines.append(f"- 配置 {idx + 1}: {error}")

    return "\n".join(lines)
