"""类型定义 - 使用 TypedDict 提供 IDE 友好的类型提示。

该模块包含产品中使用的所有数据结构类型定义，
帮助 AI 理解数据结构，提供代码补全和类型检查。

【使用示例】
    from ai_friendly.types import ParamDef, ModuleSpec, ProductDef

    # 定义参数
    param: ParamDef = {
        "name": "region",
        "label": "地域",
        "type": "string",
        "required": True,
        "default": "cn-hangzhou",
        "choices": ["cn-hangzhou", "cn-beijing"],
        "description": "阿里云地域ID",
        "examples": ["cn-hangzhou"],
    }

    # 定义模块
    module: ModuleSpec = {
        "module_code": "Instance",
        "config_template": "Region:{region}",
        "price_type": "Hour",
        "condition": None,
    }
"""

from typing import Any, Callable, Dict, List, Optional, TypedDict, Union


class ParamDef(TypedDict, total=False):
    """参数定义类型。

    用于定义产品的可配置参数，每个参数包含元数据、
    验证规则和 UI 展示信息。

    【必需字段】
    - name: 参数名称（JSON key）
    - label: 中文标签
    - type: 数据类型
    - required: 是否必填

    【可选字段】
    - default: 默认值
    - choices: 可选值列表
    - description: 参数描述（用于 AI）
    - examples: 示例值列表

    【使用示例】
        {
            "name": "instance_type",
            "label": "实例规格",
            "type": "string",
            "required": True,
            "default": None,
            "choices": None,
            "description": "ECS 实例规格",
            "examples": ["ecs.g7.xlarge"],
        }
    """

    name: str
    label: str
    type: str
    required: bool
    default: Any
    choices: Optional[List[Any]]
    description: str
    examples: List[Any]


class ModuleSpec(TypedDict, total=False):
    """BSS 模块定义类型。

    用于定义 BSS API 调用时的模块配置。

    【必需字段】
    - module_code: BSS 模块代码
    - config_template: 配置模板字符串

    【可选字段】
    - price_type: 价格类型（覆盖默认值）
    - condition: 条件函数（条件模块）

    【使用示例】
        # 固定模块
        {
            "module_code": "Instance",
            "config_template": "InstanceType:{instance_type}",
        }

        # 条件模块
        {
            "module_code": "DataDisk",
            "config_template": "DiskSize:{data_disk_size}",
            "condition": lambda p: p.get("data_disk_size", 0) > 0,
        }
    """

    module_code: str
    config_template: str
    price_type: Optional[str]
    condition: Optional[Callable[[Dict[str, Any]], bool]]


class ModuleConfig(TypedDict):
    """构建后的 BSS 模块配置类型。

    这是 build_modules 函数返回的模块列表项类型，
    可直接用于 BSS API 请求。

    【字段说明】
    - module_code: BSS 模块代码
    - config: 格式化后的配置字符串
    - price_type: 价格类型

    【使用示例】
        {
            "module_code": "Instance",
            "config": "InstanceType:ecs.g7.xlarge",
            "price_type": "Hour",
        }
    """

    module_code: str
    config: str
    price_type: str


class ProductDef(TypedDict, total=False):
    """产品定义类型。

    这是每个产品文件必须导出的 PRODUCT dict 的完整类型定义。

    【元数据字段】
    - code: BSS ProductCode（如 "ecs"）
    - name: 英文名称（如 "ECS"）
    - display_name: 中文显示名称
    - product_type: ProductType 字符串或函数
    - category: 产品分类

    【参数字段】
    - params: 参数定义列表

    【函数字段】
    - build_modules: 构建 BSS 模块列表
    - format_summary: 格式化配置摘要
    - validate: 验证参数

    【使用示例】
        PRODUCT: ProductDef = {
            "code": "ecs",
            "name": "ECS",
            "display_name": "ECS 云服务器",
            "product_type": None,
            "category": "compute",
            "params": [...],
            "build_modules": build_modules,
            "format_summary": format_summary,
            "validate": validate,
        }
    """

    code: str
    name: str
    display_name: str
    product_type: Union[str, None, Callable[[Dict[str, Any]], Optional[str]]]
    category: str
    params: List[ParamDef]
    build_modules: Callable[[Dict[str, Any]], List[ModuleConfig]]
    format_summary: Callable[[Dict[str, Any]], Dict[str, str]]
    validate: Optional[Callable[[Dict[str, Any]], List[str]]]


class ValidationError(TypedDict):
    """验证错误类型。

    【字段说明】
    - field: 错误字段名称
    - message: 错误消息
    - code: 错误代码（可选）
    """

    field: str
    message: str
    code: Optional[str]


class PriceResult(TypedDict, total=False):
    """价格查询结果类型。

    【字段说明】
    - product_code: 产品代码
    - module_code: 模块代码
    - price: 价格数值
    - currency: 货币单位（如 "CNY"）
    - price_type: 价格类型
    """

    product_code: str
    module_code: str
    price: float
    currency: str
    price_type: str


# Type aliases for convenience
ParamsDict = Dict[str, Any]
ModulesList = List[ModuleConfig]
ErrorsList = List[str]
SummaryDict = Dict[str, str]
ValidateFn = Callable[[ParamsDict], ErrorsList]
BuildModulesFn = Callable[[ParamsDict], ModulesList]
FormatSummaryFn = Callable[[ParamsDict], SummaryDict]
