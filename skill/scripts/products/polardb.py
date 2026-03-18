"""PolarDB (云原生关系型数据库) product definition - ai_friendly format.

ProductCode: polardb
ProductType: "online" (必需)
API docs: https://api.aliyun.com/document/BssOpenApi/2017-12-14/GetSubscriptionPrice
"""

from typing import Any, Dict, List

from framework.builders import ModuleBuilder
from framework.validators import ValidationRule, Validator
from ai_friendly.constants import Region, Category
from ai_friendly.types import ParamDef, ModuleSpec


# =============================================================================
# CONFIG SECTION
# =============================================================================

CODE: str = "polardb"
NAME: str = "PolarDB"
DISPLAY_NAME: str = "PolarDB 云原生数据库"
CATEGORY: str = Category.DATABASE

# 固定 ProductType
PRODUCT_TYPE: str = "online"


# =============================================================================
# PARAMS SECTION
# =============================================================================

PARAMS: List[ParamDef] = [
    {
        "name": "region",
        "label": "地域",
        "type": "string",
        "required": True,
        "default": Region.HANGZHOU,
        "choices": Region.ALL,
        "description": "阿里云地域ID",
        "examples": [Region.HANGZHOU, Region.BEIJING, Region.SHANGHAI],
    },
    {
        "name": "db_type",
        "label": "数据库类型",
        "type": "string",
        "required": False,
        "default": "MySQL",
        "choices": ["MySQL", "PostgreSQL", "Oracle"],
        "description": "数据库引擎类型",
        "examples": ["MySQL", "PostgreSQL"],
    },
    {
        "name": "db_version",
        "label": "数据库版本",
        "type": "string",
        "required": False,
        "default": "8.0",
        "choices": None,
        "description": "数据库版本。MySQL: 5.6/5.7/8.0; PostgreSQL: 11/12/13/14/15",
        "examples": ["8.0", "5.7", "14"],
    },
    {
        "name": "pay_type",
        "label": "计费方式",
        "type": "string",
        "required": False,
        "default": "Serverless",
        "choices": ["Serverless", "PrePaid", "PostPaid"],
        "description": "Serverless (Serverless版), PrePaid (包年包月), PostPaid (按量付费)",
        "examples": ["Serverless", "PrePaid"],
    },
    {
        "name": "db_node_class",
        "label": "节点规格",
        "type": "string",
        "required": False,
        "default": "polar.mysql.xlarge",
        "choices": None,
        "description": "计算节点规格，如 polar.mysql.xlarge (4C8G)",
        "examples": [
            "polar.mysql.xlarge",
            "polar.mysql.2xlarge",
            "polar.mysql.4xlarge",
        ],
    },
    {
        "name": "db_node_count",
        "label": "节点数量",
        "type": "int",
        "required": False,
        "default": 2,
        "choices": None,
        "description": "计算节点数量（至少 2 个：1 主 1 只读）",
        "examples": [2, 3, 4],
    },
    {
        "name": "storage_size",
        "label": "存储大小",
        "type": "int",
        "required": False,
        "default": 100,
        "choices": None,
        "description": "存储大小 (GB)，最小 20GB",
        "examples": [100, 500, 1000],
    },
]


# =============================================================================
# MODULES SECTION
# =============================================================================

# Serverless 版的基础模块（所有计费方式都需要）
MODULES: List[ModuleSpec] = [
    {
        "module_code": "DBType",
        "config_template": "DBType:{db_type}",
    },
    {
        "module_code": "DBVersion",
        "config_template": "DBVersion:{db_version}",
    },
    {
        "module_code": "PayType",
        "config_template": "PayType:{pay_type}",
    },
    # 以下模块仅在非 Serverless 时添加
    {
        "module_code": "DBNodeClass",
        "config_template": "DBNodeClass:{db_node_class}",
        "condition": lambda p: p.get("pay_type", "Serverless") != "Serverless",
    },
    {
        "module_code": "DBNodeCount",
        "config_template": "DBNodeCount:{db_node_count}",
        "condition": lambda p: p.get("pay_type", "Serverless") != "Serverless",
    },
    {
        "module_code": "Storage",
        "config_template": "Storage:{storage_size}",
        "condition": lambda p: p.get("pay_type", "Serverless") != "Serverless",
    },
]

DEFAULT_PRICE_TYPE: str = "Hour"


# =============================================================================
# VALIDATION SECTION
# =============================================================================

VALIDATION_RULES: List[ValidationRule] = [
    ValidationRule(
        name="db_node_count",
        label="节点数量",
        required=False,
        min_val=2,
        max_val=16,
        error_formatter=lambda r, v, t: (
            "PolarDB 至少需要 2 个节点（1 主 1 只读）" if t == 'min_val'
            else "PolarDB 节点数量不能超过 16 个" if t == 'max_val'
            else f"参数 {r.label} ({r.name}) 验证失败"
        ),
    ),
    ValidationRule(
        name="storage_size",
        label="存储大小",
        required=False,
        min_val=20,
        max_val=100000,
        error_formatter=lambda r, v, t: (
            "存储大小不能小于 20GB" if t == 'min_val'
            else "存储大小不能超过 100000GB" if t == 'max_val'
            else f"参数 {r.label} ({r.name}) 验证失败"
        ),
    ),
]


# =============================================================================
# IMPLEMENTATION SECTION
# =============================================================================

def _prepare_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """Preprocess parameters before building modules."""
    result = dict(params)
    # 设置默认值
    if "db_type" not in result:
        result["db_type"] = "MySQL"
    if "db_version" not in result:
        result["db_version"] = "8.0"
    if "pay_type" not in result:
        result["pay_type"] = "Serverless"
    if "db_node_class" not in result:
        result["db_node_class"] = "polar.mysql.xlarge"
    if "db_node_count" not in result:
        result["db_node_count"] = 2
    if "storage_size" not in result:
        result["storage_size"] = 100
    return result


def build_modules(params: Dict[str, Any]) -> List[Dict[str, str]]:
    """Build BSS module list."""
    p = _prepare_params(params)
    builder = ModuleBuilder(default_price_type=DEFAULT_PRICE_TYPE)
    
    for spec in MODULES:
        condition = spec.get("condition")
        price_type = spec.get("price_type")
        
        if condition is not None:
            builder.add_conditional(
                spec["module_code"],
                spec["config_template"],
                condition,
                price_type,
            )
        else:
            builder.add(
                spec["module_code"],
                spec["config_template"],
                price_type,
            )
    
    return builder.build(p)


def format_summary(params: Dict[str, Any]) -> Dict[str, str]:
    """Build human-readable config summary."""
    pay_type = params.get("pay_type", "Serverless")
    region = params.get("region", Region.HANGZHOU)
    
    pay_type_map = {
        "Serverless": "Serverless 版",
        "PrePaid": "包年包月",
        "PostPaid": "按量付费",
    }
    
    summary = {
        "产品": "PolarDB 云原生数据库",
        "地域": region,
        "数据库": f"{params.get('db_type', 'MySQL')} {params.get('db_version', '8.0')}",
        "计费方式": pay_type_map.get(pay_type, pay_type),
    }
    
    if pay_type != "Serverless":
        summary["节点规格"] = params.get("db_node_class", "polar.mysql.xlarge")
        summary["节点数量"] = str(params.get("db_node_count", 2))
        summary["存储"] = f"{params.get('storage_size', 100)} GB"
    
    return summary


def validate(params: Dict[str, Any]) -> List[str]:
    """Validate parameters."""
    errors = []
    
    # 自动验证 PARAMS 中的 choices 和必填
    for param in PARAMS:
        name = param["name"]
        value = params.get(name)
        
        if param.get("required") and value is None:
            errors.append(f"缺少必填参数: {param['label']} ({name})")
            continue
        
        if value is None:
            continue
        
        choices = param.get("choices")
        if choices and value not in choices:
            errors.append(
                f"参数 {param['label']} ({name}) 的值 '{value}' 无效，"
                f"可选值: {', '.join(str(c) for c in choices)}"
            )
    
    # 验证规则检查（仅对非 Serverless）
    pay_type = params.get("pay_type", "Serverless")
    if pay_type != "Serverless" and VALIDATION_RULES:
        validator = Validator(VALIDATION_RULES)
        errors.extend(validator.validate(params))
    
    # 版本与数据库类型匹配验证
    db_type = params.get("db_type", "MySQL")
    db_version = params.get("db_version", "8.0")
    
    if db_type == "MySQL":
        valid_versions = ["5.6", "5.7", "8.0"]
        if db_version not in valid_versions:
            errors.append(f"MySQL 版本必须是: {', '.join(valid_versions)}")
    elif db_type == "PostgreSQL":
        valid_versions = ["11", "12", "13", "14", "15"]
        if db_version not in valid_versions:
            errors.append(f"PostgreSQL 版本必须是: {', '.join(valid_versions)}")
    
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


# =============================================================================
# AI 验证命令（运行此文件时执行自检）
# =============================================================================
if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    # 添加项目根目录到路径
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
