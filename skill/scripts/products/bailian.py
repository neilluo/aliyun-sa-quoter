"""Bailian (百炼大模型) product definition - ai_friendly format.

ProductCode: bailian
计费方式: 按 Token 计费（输入 + 输出分开计费）
特点: 静态定价表，不走 BSS API，本地计算价格

价格数据最后更新: 2026-03-20
来源: https://help.aliyun.com/zh/model-studio/model-pricing
"""

from typing import Any, Dict, List

from framework.validators import ValidationRule, Validator
from ai_friendly.constants import Category
from ai_friendly.types import ParamDef


# =============================================================================
# CONFIG SECTION
# =============================================================================

CODE: str = "bailian"
NAME: str = "Bailian"
DISPLAY_NAME: str = "百炼大模型"
CATEGORY: str = Category.AI
PRODUCT_TYPE = None  # 不走 BSS API


# =============================================================================
# 定价表
# =============================================================================

PRICING_TABLE = {
    "cn-beijing": {
        "qwen3-max": {
            "input_tiers": [
                {"max_tokens": 32000, "price_per_million": 2.5},
                {"max_tokens": 128000, "price_per_million": 4.0},
                {"max_tokens": 252000, "price_per_million": 7.0},
            ],
            "output_tiers": [
                {"max_tokens": 32000, "price_per_million": 10.0},
            ],
            "thinking_output_tiers": [
                {"max_tokens": 32000, "price_per_million": 10.0},
                {"max_tokens": 128000, "price_per_million": 16.0},
                {"max_tokens": 252000, "price_per_million": 28.0},
            ],
            "supports_thinking": True,
        },
        "qwen-max": {
            "input_tiers": [{"max_tokens": 32000, "price_per_million": 2.4}],
            "output_tiers": [
                {"max_tokens": 32000, "price_per_million": 9.6},
            ],
            "thinking_output_tiers": None,
            "supports_thinking": False,
        },
        "qwen3.5-plus": {
            "input_tiers": [
                {"max_tokens": 128000, "price_per_million": 0.8},
                {"max_tokens": 256000, "price_per_million": 2.0},
                {"max_tokens": 1000000, "price_per_million": 4.0},
            ],
            "output_tiers": [
                {"max_tokens": 128000, "price_per_million": 4.8},
                {"max_tokens": 256000, "price_per_million": 12.0},
                {"max_tokens": 1000000, "price_per_million": 24.0},
            ],
            "thinking_output_tiers": [
                {"max_tokens": 128000, "price_per_million": 4.8},
                {"max_tokens": 256000, "price_per_million": 12.0},
                {"max_tokens": 1000000, "price_per_million": 24.0},
            ],
            "supports_thinking": True,
        },
        "qwen-plus": {
            "input_tiers": [
                {"max_tokens": 128000, "price_per_million": 0.8},
                {"max_tokens": 256000, "price_per_million": 2.4},
                {"max_tokens": 1000000, "price_per_million": 4.8},
            ],
            "output_tiers": [
                {"max_tokens": 128000, "price_per_million": 2.0},
                {"max_tokens": 256000, "price_per_million": 20.0},
                {"max_tokens": 1000000, "price_per_million": 48.0},
            ],
            "thinking_output_tiers": [
                {"max_tokens": 128000, "price_per_million": 8.0},
                {"max_tokens": 256000, "price_per_million": 24.0},
                {"max_tokens": 1000000, "price_per_million": 64.0},
            ],
            "supports_thinking": True,
        },
        "qwen3.5-flash": {
            "input_tiers": [
                {"max_tokens": 128000, "price_per_million": 0.2},
                {"max_tokens": 256000, "price_per_million": 0.8},
                {"max_tokens": 1000000, "price_per_million": 1.2},
            ],
            "output_tiers": [
                {"max_tokens": 128000, "price_per_million": 2.0},
                {"max_tokens": 256000, "price_per_million": 8.0},
                {"max_tokens": 1000000, "price_per_million": 12.0},
            ],
            "thinking_output_tiers": [
                {"max_tokens": 128000, "price_per_million": 2.0},
                {"max_tokens": 256000, "price_per_million": 8.0},
                {"max_tokens": 1000000, "price_per_million": 12.0},
            ],
            "supports_thinking": True,
        },
        "qwen-flash": {
            "input_tiers": [
                {"max_tokens": 128000, "price_per_million": 0.15},
                {"max_tokens": 256000, "price_per_million": 0.6},
                {"max_tokens": 1000000, "price_per_million": 1.2},
            ],
            "output_tiers": [
                {"max_tokens": 128000, "price_per_million": 1.5},
                {"max_tokens": 256000, "price_per_million": 6.0},
                {"max_tokens": 1000000, "price_per_million": 12.0},
            ],
            "thinking_output_tiers": [
                {"max_tokens": 128000, "price_per_million": 1.5},
                {"max_tokens": 256000, "price_per_million": 6.0},
                {"max_tokens": 1000000, "price_per_million": 12.0},
            ],
            "supports_thinking": True,
        },
        "qwen-turbo": {
            "input_tiers": [{"max_tokens": 1000000, "price_per_million": 0.3}],
            "output_tiers": [
                {"max_tokens": 1000000, "price_per_million": 0.6},
            ],
            "thinking_output_tiers": [
                {"max_tokens": 1000000, "price_per_million": 3.0},
            ],
            "supports_thinking": True,
        },
        "qwq-plus": {
            "input_tiers": [{"max_tokens": 1000000, "price_per_million": 1.6}],
            "output_tiers": [
                {"max_tokens": 1000000, "price_per_million": 4.0},
            ],
            "thinking_output_tiers": [
                {"max_tokens": 1000000, "price_per_million": 4.0},
            ],
            "supports_thinking": True,
            "thinking_only": True,
        },
        "qwen-long": {
            "input_tiers": [{"max_tokens": 10000000, "price_per_million": 0.5}],
            "output_tiers": [
                {"max_tokens": 10000000, "price_per_million": 2.0},
            ],
            "thinking_output_tiers": None,
            "supports_thinking": False,
        },
    },
}

REGION_DISPLAY = {
    "cn-beijing": "中国内地",
}

MODEL_DISPLAY = {
    "qwen3-max": "通义千问3-Max",
    "qwen-max": "通义千问-Max",
    "qwen3.5-plus": "通义千问3.5-Plus",
    "qwen-plus": "通义千问-Plus",
    "qwen3.5-flash": "通义千问3.5-Flash",
    "qwen-flash": "通义千问-Flash",
    "qwen-turbo": "通义千问-Turbo",
    "qwq-plus": "QwQ-Plus",
    "qwen-long": "通义千问-Long",
}


# =============================================================================
# PARAMS SECTION
# =============================================================================

PARAMS: List[ParamDef] = [
    {
        "name": "model",
        "label": "模型",
        "type": "string",
        "required": True,
        "default": None,
        "choices": [
            "qwen3-max",
            "qwen-max",
            "qwen3.5-plus",
            "qwen-plus",
            "qwen3.5-flash",
            "qwen-flash",
            "qwen-turbo",
            "qwq-plus",
            "qwen-long",
        ],
        "description": "百炼大模型名称",
        "examples": ["qwen3-max", "qwen-plus"],
    },
    {
        "name": "region",
        "label": "地域",
        "type": "string",
        "required": False,
        "default": "cn-beijing",
        "choices": ["cn-beijing"],
        "description": "服务地域",
        "examples": ["cn-beijing"],
    },
    {
        "name": "input_tokens",
        "label": "输入 Token 数",
        "type": "int",
        "required": True,
        "default": None,
        "choices": None,
        "description": "输入 Token 数量",
        "examples": [1000, 100000],
    },
    {
        "name": "output_tokens",
        "label": "输出 Token 数",
        "type": "int",
        "required": True,
        "default": None,
        "choices": None,
        "description": "输出 Token 数量",
        "examples": [500, 50000],
    },
    {
        "name": "thinking",
        "label": "思考模式",
        "type": "bool",
        "required": False,
        "default": False,
        "choices": None,
        "description": "是否启用思考模式",
        "examples": [False, True],
    },
]


# =============================================================================
# MODULES SECTION - 本地计算产品，返回特殊标记
# =============================================================================

MODULES: List[Dict[str, Any]] = []

DEFAULT_PRICE_TYPE: str = "PerCall"


# =============================================================================
# IMPLEMENTATION SECTION
# =============================================================================

def _get_input_price_per_million(model_config, input_tokens):
    """根据输入 Token 数和阶梯定价规则计算输入单价。"""
    tiers = model_config["input_tiers"]
    for tier in tiers:
        if input_tokens <= tier["max_tokens"]:
            return tier["price_per_million"]
    return tiers[-1]["price_per_million"]


def _get_output_price_per_million(model_config, output_tokens, thinking=False):
    """根据输出 Token 数和阶梯定价规则计算输出单价。"""
    if thinking and model_config.get("thinking_output_tiers") is not None:
        tiers = model_config["thinking_output_tiers"]
    else:
        tiers = model_config["output_tiers"]
    
    for tier in tiers:
        if output_tokens <= tier["max_tokens"]:
            return tier["price_per_million"]
    return tiers[-1]["price_per_million"]


def calculate_price(params):
    """计算百炼大模型调用价格。"""
    model = params["model"]
    region = params.get("region", "cn-beijing")
    input_tokens = params["input_tokens"]
    output_tokens = params["output_tokens"]
    thinking = params.get("thinking", False)

    region_config = PRICING_TABLE.get(region)
    if not region_config:
        raise ValueError(f"不支持的地域: {region}")

    model_config = region_config.get(model)
    if not model_config:
        raise ValueError(f"不支持的模型: {model}")

    input_unit_price = _get_input_price_per_million(model_config, input_tokens)
    output_unit_price = _get_output_price_per_million(model_config, output_tokens, thinking)

    input_price = input_tokens * input_unit_price / 1_000_000
    output_price = output_tokens * output_unit_price / 1_000_000

    total_price = input_price + output_price

    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "input_unit_price": input_unit_price,
        "output_unit_price": output_unit_price,
        "input_price": input_price,
        "output_price": output_price,
        "total_price": total_price,
        "model": model,
        "region": region,
        "thinking": thinking,
    }


def build_modules(params):
    """构建百炼定价模块列表 - 本地计算，返回特殊标记。"""
    return [{"module_code": "__LOCAL_CALCULATION__", "config": "bailian", "price_type": "PerCall"}]


def format_summary(params):
    """构建人类可读的配置摘要。"""
    model = params["model"]
    region = params.get("region", "cn-beijing")
    input_tokens = params["input_tokens"]
    output_tokens = params["output_tokens"]
    thinking = params.get("thinking", False)

    return {
        "模型": MODEL_DISPLAY.get(model, model),
        "地域": f"{REGION_DISPLAY.get(region, region)}({region})",
        "输入 Token": f"{input_tokens:,}",
        "输出 Token": f"{output_tokens:,}",
        "思考模式": "是" if thinking else "否",
    }


# =============================================================================
# VALIDATION SECTION
# =============================================================================

VALIDATION_RULES: List[ValidationRule] = [
    ValidationRule(name="model", label="模型", required=True),
    ValidationRule(name="input_tokens", label="输入 Token 数", required=True, min_val=1),
    ValidationRule(name="output_tokens", label="输出 Token 数", required=True, min_val=1),
]


def validate(params):
    """验证百炼参数。"""
    validator = Validator(VALIDATION_RULES)
    errors = validator.validate(params)

    model = params.get("model")
    region = params.get("region", "cn-beijing")
    thinking = params.get("thinking", False)

    if region not in PRICING_TABLE:
        errors.append(f"不支持的地域: '{region}'")
    elif model:
        region_config = PRICING_TABLE.get(region, {})
        if model not in region_config:
            errors.append(f"模型 '{model}' 在地域 '{region}' 不可用")
        else:
            model_config = region_config.get(model, {})
            if thinking and not model_config.get("supports_thinking", False):
                errors.append(f"模型 '{model}' 不支持思考模式")
            if not thinking and model_config.get("thinking_only", False):
                errors.append(f"模型 '{model}' 仅支持思考模式")

    return errors


# =============================================================================
# EXPORT SECTION
# =============================================================================

PRODUCT = {
    "code": CODE,
    "name": NAME,
    "display_name": DISPLAY_NAME,
    "product_type": PRODUCT_TYPE,
    "category": CATEGORY,
    "params": PARAMS,
    "build_modules": build_modules,
    "format_summary": format_summary,
    "validate": validate,
}


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from ai_friendly.validate import validate_product_file
    
    print(f"验证产品定义: {CODE}")
    errors = validate_product_file(__file__)
    
    if errors:
        print("❌ 验证失败:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("✅ 验证通过")
        sys.exit(0)
