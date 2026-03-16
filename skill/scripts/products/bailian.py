"""
Bailian (百炼大模型) product definition.

产品代码: bailian
计费方式: 按 Token 计费（输入 + 输出分开计费）
特点: 静态定价表，不走 BSS API，本地计算价格

价格数据最后更新: 2026-03-11
来源: https://help.aliyun.com/zh/model-studio/model-pricing
"""

# ============================================================================
# 定价表
# ============================================================================
# 价格数据最后更新: 2026-03-11
# 来源: https://help.aliyun.com/zh/model-studio/model-pricing

PRICING_TABLE = {
    "cn-beijing": {  # 中国内地
        "qwen3-max": {
            "input_tiers": [
                {"max_tokens": 32000, "price_per_million": 2.5},
                {"max_tokens": 128000, "price_per_million": 4.0},
                {"max_tokens": 252000, "price_per_million": 7.0},
            ],
            "output_price_per_million": 10.0,
            "thinking_output_price_per_million": 10.0,
            "supports_batch": True,
            "supports_context_cache": True,
        },
        "qwen-max": {
            "input_tiers": [
                {"max_tokens": 32000, "price_per_million": 2.4},
            ],
            "output_price_per_million": 9.6,
            "thinking_output_price_per_million": None,
            "supports_batch": True,
            "supports_context_cache": False,
        },
        "qwen3.5-plus": {
            "input_tiers": [
                {"max_tokens": 128000, "price_per_million": 0.8},
                {"max_tokens": 256000, "price_per_million": 2.0},
                {"max_tokens": 1000000, "price_per_million": 4.0},
            ],
            "output_price_per_million": 4.8,
            "thinking_output_price_per_million": 4.8,
            "supports_batch": True,
            "supports_context_cache": False,
        },
        "qwen-plus": {
            "input_tiers": [
                {"max_tokens": 128000, "price_per_million": 0.8},
                {"max_tokens": 256000, "price_per_million": 2.4},
                {"max_tokens": 1000000, "price_per_million": 4.8},
            ],
            "output_price_per_million": 2.0,
            "thinking_output_price_per_million": 8.0,
            "supports_batch": True,
            "supports_context_cache": True,
        },
        "qwen3.5-flash": {
            "input_tiers": [
                {"max_tokens": 128000, "price_per_million": 0.2},
                {"max_tokens": 256000, "price_per_million": 0.8},
                {"max_tokens": 1000000, "price_per_million": 1.2},
            ],
            "output_price_per_million": 2.0,
            "thinking_output_price_per_million": None,
            "supports_batch": True,
            "supports_context_cache": True,
        },
        "qwen-flash": {
            "input_tiers": [
                {"max_tokens": 128000, "price_per_million": 0.15},
                {"max_tokens": 256000, "price_per_million": 0.6},
                {"max_tokens": 1000000, "price_per_million": 1.2},
            ],
            "output_price_per_million": 1.5,
            "thinking_output_price_per_million": None,
            "supports_batch": True,
            "supports_context_cache": True,
        },
    },
    "global": {  # 全球
        "qwen3-max": {
            "input_tiers": [
                {"max_tokens": 32000, "price_per_million": 3.75},
                {"max_tokens": 128000, "price_per_million": 6.0},
                {"max_tokens": 252000, "price_per_million": 10.5},
            ],
            "output_price_per_million": 15.0,
            "thinking_output_price_per_million": 15.0,
            "supports_batch": True,
            "supports_context_cache": True,
        },
        "qwen-max": {
            "input_tiers": [
                {"max_tokens": 32000, "price_per_million": 3.6},
            ],
            "output_price_per_million": 14.4,
            "thinking_output_price_per_million": None,
            "supports_batch": True,
            "supports_context_cache": False,
        },
        "qwen3.5-plus": {
            "input_tiers": [
                {"max_tokens": 32000, "price_per_million": 1.8},
                {"max_tokens": 128000, "price_per_million": 3.6},
                {"max_tokens": 2000000, "price_per_million": 7.2},
            ],
            "output_price_per_million": 7.2,
            "thinking_output_price_per_million": 7.2,
            "supports_batch": True,
            "supports_context_cache": False,
        },
        "qwen-plus": {
            "input_tiers": [
                {"max_tokens": 32000, "price_per_million": 0.6},
                {"max_tokens": 128000, "price_per_million": 1.2},
                {"max_tokens": 2000000, "price_per_million": 3.0},
            ],
            "output_price_per_million": 3.0,
            "thinking_output_price_per_million": 12.0,
            "supports_batch": True,
            "supports_context_cache": True,
        },
        "qwen3.5-flash": {
            "input_tiers": [
                {"max_tokens": 32000, "price_per_million": 0.375},
                {"max_tokens": 128000, "price_per_million": 0.75},
                {"max_tokens": 2000000, "price_per_million": 1.5},
            ],
            "output_price_per_million": 3.0,
            "thinking_output_price_per_million": None,
            "supports_batch": True,
            "supports_context_cache": True,
        },
        "qwen-flash": {
            "input_tiers": [
                {"max_tokens": 32000, "price_per_million": 0.225},
                {"max_tokens": 128000, "price_per_million": 0.45},
                {"max_tokens": 2000000, "price_per_million": 0.9},
            ],
            "output_price_per_million": 2.25,
            "thinking_output_price_per_million": None,
            "supports_batch": True,
            "supports_context_cache": True,
        },
    },
    "international": {  # 国际
        "qwen3-max": {
            "input_tiers": [
                {"max_tokens": 32000, "price_per_million": 3.75},
                {"max_tokens": 128000, "price_per_million": 6.0},
                {"max_tokens": 252000, "price_per_million": 10.5},
            ],
            "output_price_per_million": 15.0,
            "thinking_output_price_per_million": 15.0,
            "supports_batch": True,
            "supports_context_cache": True,
        },
        "qwen-max": {
            "input_tiers": [
                {"max_tokens": 32000, "price_per_million": 3.6},
            ],
            "output_price_per_million": 14.4,
            "thinking_output_price_per_million": None,
            "supports_batch": True,
            "supports_context_cache": False,
        },
        "qwen3.5-plus": {
            "input_tiers": [
                {"max_tokens": 32000, "price_per_million": 1.8},
                {"max_tokens": 128000, "price_per_million": 3.6},
                {"max_tokens": 2000000, "price_per_million": 7.2},
            ],
            "output_price_per_million": 7.2,
            "thinking_output_price_per_million": 7.2,
            "supports_batch": True,
            "supports_context_cache": False,
        },
        "qwen-plus": {
            "input_tiers": [
                {"max_tokens": 32000, "price_per_million": 0.6},
                {"max_tokens": 128000, "price_per_million": 1.2},
                {"max_tokens": 2000000, "price_per_million": 3.0},
            ],
            "output_price_per_million": 3.0,
            "thinking_output_price_per_million": 12.0,
            "supports_batch": True,
            "supports_context_cache": True,
        },
        "qwen3.5-flash": {
            "input_tiers": [
                {"max_tokens": 32000, "price_per_million": 0.375},
                {"max_tokens": 128000, "price_per_million": 0.75},
                {"max_tokens": 2000000, "price_per_million": 1.5},
            ],
            "output_price_per_million": 3.0,
            "thinking_output_price_per_million": None,
            "supports_batch": True,
            "supports_context_cache": True,
        },
        "qwen-flash": {
            "input_tiers": [
                {"max_tokens": 32000, "price_per_million": 0.225},
                {"max_tokens": 128000, "price_per_million": 0.45},
                {"max_tokens": 2000000, "price_per_million": 0.9},
            ],
            "output_price_per_million": 2.25,
            "thinking_output_price_per_million": None,
            "supports_batch": True,
            "supports_context_cache": True,
        },
    },
    "us": {  # 美国
        "qwen3-max": {
            "input_tiers": [
                {"max_tokens": 32000, "price_per_million": 3.5},
                {"max_tokens": 128000, "price_per_million": 5.6},
                {"max_tokens": 252000, "price_per_million": 9.8},
            ],
            "output_price_per_million": 14.0,
            "thinking_output_price_per_million": 14.0,
            "supports_batch": True,
            "supports_context_cache": True,
        },
        "qwen-max": {
            "input_tiers": [
                {"max_tokens": 32000, "price_per_million": 3.36},
            ],
            "output_price_per_million": 13.44,
            "thinking_output_price_per_million": None,
            "supports_batch": True,
            "supports_context_cache": False,
        },
        "qwen3.5-plus": {
            "input_tiers": [
                {"max_tokens": 32000, "price_per_million": 1.68},
                {"max_tokens": 128000, "price_per_million": 3.36},
                {"max_tokens": 2000000, "price_per_million": 6.72},
            ],
            "output_price_per_million": 6.72,
            "thinking_output_price_per_million": 6.72,
            "supports_batch": True,
            "supports_context_cache": False,
        },
        "qwen-plus": {
            "input_tiers": [
                {"max_tokens": 32000, "price_per_million": 0.56},
                {"max_tokens": 128000, "price_per_million": 1.12},
                {"max_tokens": 2000000, "price_per_million": 2.8},
            ],
            "output_price_per_million": 2.8,
            "thinking_output_price_per_million": 11.2,
            "supports_batch": True,
            "supports_context_cache": True,
        },
        "qwen3.5-flash": {
            "input_tiers": [
                {"max_tokens": 32000, "price_per_million": 0.35},
                {"max_tokens": 128000, "price_per_million": 0.7},
                {"max_tokens": 2000000, "price_per_million": 1.4},
            ],
            "output_price_per_million": 2.8,
            "thinking_output_price_per_million": None,
            "supports_batch": True,
            "supports_context_cache": True,
        },
        "qwen-flash": {
            "input_tiers": [
                {"max_tokens": 32000, "price_per_million": 0.21},
                {"max_tokens": 128000, "price_per_million": 0.42},
                {"max_tokens": 2000000, "price_per_million": 0.84},
            ],
            "output_price_per_million": 2.1,
            "thinking_output_price_per_million": None,
            "supports_batch": True,
            "supports_context_cache": True,
        },
    },
}

# 地域显示名称映射
REGION_DISPLAY = {
    "cn-beijing": "中国内地",
    "global": "全球",
    "international": "国际",
    "us": "美国",
}

# 模型显示名称映射
MODEL_DISPLAY = {
    "qwen3-max": "通义千问3-Max",
    "qwen-max": "通义千问-Max",
    "qwen3.5-plus": "通义千问3.5-Plus",
    "qwen-plus": "通义千问-Plus",
    "qwen3.5-flash": "通义千问3.5-Flash",
    "qwen-flash": "通义千问-Flash",
}


# ============================================================================
# 价格计算逻辑
# ============================================================================

def _get_input_price_per_million(model_config, input_tokens):
    """根据输入 Token 数和阶梯定价规则计算输入单价（元/百万Token）。

    Args:
        model_config: 模型配置字典
        input_tokens: 输入 Token 数

    Returns:
        float: 输入单价（元/百万Token）
    """
    tiers = model_config["input_tiers"]
    for tier in tiers:
        if input_tokens <= tier["max_tokens"]:
            return tier["price_per_million"]
    # 如果超出最大阶梯，使用最后一档价格
    return tiers[-1]["price_per_million"]


def _get_output_price_per_million(model_config, thinking=False):
    """获取输出单价（元/百万Token）。

    Args:
        model_config: 模型配置字典
        thinking: 是否思考模式

    Returns:
        float: 输出单价（元/百万Token）
    """
    if thinking and model_config["thinking_output_price_per_million"] is not None:
        return model_config["thinking_output_price_per_million"]
    return model_config["output_price_per_million"]


def calculate_price(params):
    """计算百炼大模型调用价格。

    Args:
        params: 参数字典，包含 model, region, input_tokens, output_tokens,
                thinking, batch, context_cache

    Returns:
        dict: 价格计算结果，包含 input_price, output_price, total_price,
              input_unit_price, output_unit_price, discounts_applied 等
    """
    model = params["model"]
    region = params.get("region", "cn-beijing")
    input_tokens = params["input_tokens"]
    output_tokens = params["output_tokens"]
    thinking = params.get("thinking", False)
    batch = params.get("batch", False)
    context_cache = params.get("context_cache", False)

    # 获取定价配置
    region_config = PRICING_TABLE.get(region)
    if not region_config:
        raise ValueError(f"不支持的地域: {region}。支持的地域: {', '.join(PRICING_TABLE.keys())}")

    model_config = region_config.get(model)
    if not model_config:
        raise ValueError(f"不支持的模型: {model}。支持的模型: {', '.join(region_config.keys())}")

    # 计算单价
    input_unit_price = _get_input_price_per_million(model_config, input_tokens)
    output_unit_price = _get_output_price_per_million(model_config, thinking)

    # 计算基础价格
    input_price = input_tokens * input_unit_price / 1_000_000
    output_price = output_tokens * output_unit_price / 1_000_000

    # 应用折扣
    discounts_applied = []

    if batch:
        input_price *= 0.5
        output_price *= 0.5
        discounts_applied.append("Batch调用 50% 折扣")

    if context_cache:
        # 仅输入享有上下文缓存折扣
        input_price *= 0.5
        discounts_applied.append("上下文缓存 50% 折扣")

    total_price = input_price + output_price

    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "input_unit_price": input_unit_price,
        "output_unit_price": output_unit_price,
        "input_price": input_price,
        "output_price": output_price,
        "total_price": total_price,
        "discounts_applied": discounts_applied,
        "model": model,
        "region": region,
        "thinking": thinking,
        "batch": batch,
        "context_cache": context_cache,
    }


# ============================================================================
# 产品定义接口实现
# ============================================================================

def build_modules(params):
    """构建百炼定价模块列表。

    由于百炼不走 BSS API，这里返回空列表作为标记，
    实际价格计算在本地完成。

    Args:
        params: 用户参数字典

    Returns:
        list: 空列表（表示本地计算）
    """
    # 本地计算产品，返回特殊标记
    return [{"module_code": "__LOCAL_CALCULATION__", "config": "bailian", "price_type": "PerCall"}]


def format_summary(params):
    """构建人类可读的配置摘要。

    Args:
        params: 用户参数字典

    Returns:
        dict: 配置摘要字典
    """
    model = params["model"]
    region = params.get("region", "cn-beijing")
    input_tokens = params["input_tokens"]
    output_tokens = params["output_tokens"]
    thinking = params.get("thinking", False)
    batch = params.get("batch", False)
    context_cache = params.get("context_cache", False)

    summary = {
        "模型": MODEL_DISPLAY.get(model, model),
        "地域": f"{REGION_DISPLAY.get(region, region)}({region})",
        "输入 Token": f"{input_tokens:,}",
        "输出 Token": f"{output_tokens:,}",
        "思考模式": "是" if thinking else "否",
        "Batch 调用": "是" if batch else "否",
    }

    if context_cache:
        summary["上下文缓存"] = "是"

    return summary


def validate(params):
    """验证百炼参数。

    Args:
        params: 用户参数字典

    Returns:
        list: 错误字符串列表（空列表表示验证通过）
    """
    errors = []

    model = params.get("model")
    region = params.get("region", "cn-beijing")
    input_tokens = params.get("input_tokens")
    output_tokens = params.get("output_tokens")
    thinking = params.get("thinking", False)
    batch = params.get("batch", False)
    context_cache = params.get("context_cache", False)

    # 验证模型
    if model:
        region_config = PRICING_TABLE.get(region)
        if region_config and model not in region_config:
            errors.append(
                f"模型 '{model}' 在地域 '{region}' 不可用。"
                f"可用模型: {', '.join(region_config.keys())}"
            )

    # 验证 Token 数
    if input_tokens is not None:
        if input_tokens < 0:
            errors.append("输入 Token 数不能为负数")

    if output_tokens is not None:
        if output_tokens < 0:
            errors.append("输出 Token 数不能为负数")

    # 验证地域
    if region not in PRICING_TABLE:
        errors.append(
            f"不支持的地域: '{region}'。"
            f"支持的地域: {', '.join(PRICING_TABLE.keys())}"
        )

    # 验证思考模式是否被模型支持
    if thinking and model:
        region_config = PRICING_TABLE.get(region, {})
        model_config = region_config.get(model, {})
        if model_config.get("thinking_output_price_per_million") is None:
            errors.append(f"模型 '{model}' 不支持思考模式")

    # 验证上下文缓存是否被模型支持
    if context_cache and model:
        region_config = PRICING_TABLE.get(region, {})
        model_config = region_config.get(model, {})
        if not model_config.get("supports_context_cache", False):
            errors.append(f"模型 '{model}' 不支持上下文缓存")

    # 验证 Batch 调用是否被模型支持
    if batch and model:
        region_config = PRICING_TABLE.get(region, {})
        model_config = region_config.get(model, {})
        if not model_config.get("supports_batch", False):
            errors.append(f"模型 '{model}' 不支持 Batch 调用")

    return errors


# ============================================================================
# 产品定义
# ============================================================================

PRODUCT = {
    "code": "bailian",
    "name": "Bailian",
    "display_name": "百炼大模型",
    "product_type": None,  # 不走 BSS API
    "category": "ai",
    "params": [
        {
            "name": "model",
            "label": "模型",
            "type": "string",
            "required": True,
            "default": None,
            "choices": ["qwen3-max", "qwen-max", "qwen3.5-plus", "qwen-plus", "qwen3.5-flash", "qwen-flash"],
            "description": "百炼大模型名称",
            "examples": ["qwen3-max", "qwen-plus"],
        },
        {
            "name": "region",
            "label": "地域",
            "type": "string",
            "required": False,
            "default": "cn-beijing",
            "choices": ["cn-beijing", "global", "international", "us"],
            "description": "服务地域，影响定价",
            "examples": ["cn-beijing", "global"],
        },
        {
            "name": "input_tokens",
            "label": "输入 Token 数",
            "type": "int",
            "required": True,
            "default": None,
            "choices": None,
            "description": "输入 Token 数量（影响阶梯定价）",
            "examples": [1000, 100000, 1000000],
        },
        {
            "name": "output_tokens",
            "label": "输出 Token 数",
            "type": "int",
            "required": True,
            "default": None,
            "choices": None,
            "description": "输出 Token 数量",
            "examples": [500, 50000, 500000],
        },
        {
            "name": "thinking",
            "label": "思考模式",
            "type": "bool",
            "required": False,
            "default": False,
            "choices": None,
            "description": "是否启用思考模式（部分模型支持）",
            "examples": [False, True],
        },
        {
            "name": "batch",
            "label": "Batch 调用",
            "type": "bool",
            "required": False,
            "default": False,
            "choices": None,
            "description": "是否使用 Batch 调用（50% 折扣）",
            "examples": [False, True],
        },
        {
            "name": "context_cache",
            "label": "上下文缓存",
            "type": "bool",
            "required": False,
            "default": False,
            "choices": None,
            "description": "是否启用上下文缓存（输入 50% 折扣）",
            "examples": [False, True],
        },
    ],
    "build_modules": build_modules,
    "format_summary": format_summary,
    "validate": validate,
}
