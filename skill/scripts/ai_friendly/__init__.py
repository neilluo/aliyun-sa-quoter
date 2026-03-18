"""AI Friendly - AI 友好的产品定义框架。

提供标准化的产品定义模板、常量、类型和验证工具，
让 AI 在 5 分钟内理解项目，10 分钟内完成新产品接入。

【快速开始】
1. 复制 TEMPLATE.py 到 products/<product_code>.py
2. 填写 CONFIG SECTION 中的常量
3. 定义 PARAMS 和 MODULES
4. 运行验证: python -m ai_friendly.validate <product_code>

【模块说明】
- constants.py: 所有常量定义（地域、分类、磁盘类型等）
- types.py: TypedDict 类型定义（ParamDef, ModuleSpec 等）
- TEMPLATE.py: 产品定义模板（填空即可）
- validate.py: 验证工具（检查产品定义正确性）
"""

from .constants import (
    Region,
    Category,
    BillingType,
    DiskType,
    ProductType,
    PriceType,
)
from .types import (
    ParamDef,
    ModuleSpec,
    ModuleConfig,
    ProductDef,
)

__version__ = "1.0.0"
__all__ = [
    "Region",
    "Category",
    "BillingType",
    "DiskType",
    "ProductType",
    "PriceType",
    "ParamDef",
    "ModuleSpec",
    "ModuleConfig",
    "ProductDef",
]
