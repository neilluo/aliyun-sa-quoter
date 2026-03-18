# AI 开发指南

欢迎来到 aliyun-sa-quoter 的 AI 友好开发指南！

## 快速开始

接入新产品只需 3 步：

```bash
# 第 1 步：复制模板
cp ai_friendly/TEMPLATE.py products/kafka.py

# 第 2 步：编辑 products/kafka.py，填写 CONFIG SECTION

# 第 3 步：验证
python -m ai_friendly.validate kafka
```

## 文件结构

```
ai_friendly/
├── TEMPLATE.py          # ⭐ 产品定义模板（从这里开始）
├── TEMPLATE_EXAMPLE.py  # ECS 完整示例（参考这个）
├── constants.py         # 所有常量定义
├── types.py             # 类型定义
├── validate.py          # 验证工具
└── README.md            # 本文件
```

## 开发流程

### 1. 复制模板

```bash
cp ai_friendly/TEMPLATE.py products/<product_code>.py
```

### 2. 填写配置

编辑产品文件，填写 CONFIG SECTION：

```python
# 基础信息
CODE = "alikafka"
NAME = "Kafka"
DISPLAY_NAME = "消息队列 Kafka"
CATEGORY = Category.MIDDLEWARE

# 参数定义
PARAMS = [
    {
        "name": "region",
        "label": "地域",
        "type": "string",
        "required": True,
        "default": Region.HANGZHOU,
        "choices": Region.ALL,
    },
    # ... 更多参数
]

# 模块定义
MODULES = [
    {
        "module_code": "PartitionNum",
        "config_template": "PartitionNum:{partition_num},...",
    },
    # ... 更多模块
]
```

### 3. 验证

```bash
python -m ai_friendly.validate <product_code>
```

## 常量引用

所有魔法字符串都定义在 `constants.py` 中：

```python
from ai_friendly.constants import Region, Category, DiskType, ProductType

# 地域
Region.HANGZHOU      # "cn-hangzhou"
Region.BEIJING       # "cn-beijing"
Region.ALL           # 所有地域列表

# 分类
Category.COMPUTE     # "compute"
Category.DATABASE    # "database"
Category.MIDDLEWARE  # "middleware"

# 磁盘类型
DiskType.ESSD        # "cloud_essd"
DiskType.SSD         # "cloud_ssd"

# ProductType
ProductType.KAFKA_PRE   # "alikafka_pre"
ProductType.KAFKA_POST  # "alikafka_post"
```

## 参数定义

参数定义使用 ParamDef 结构：

```python
{
    "name": "param_name",        # 参数名（英文）
    "label": "参数显示名",        # 参数显示名（中文）
    "type": "string",            # 类型: string/int/float/bool
    "required": True,            # 是否必填
    "default": "default_value",  # 默认值（可选）
    "choices": ["a", "b"],       # 可选值（可选）
    "description": "参数说明",    # 参数说明
    "examples": ["example"],     # 示例值
}
```

## 模块定义

模块定义使用 ModuleSpec 结构：

```python
# 基础模块
{
    "module_code": "ModuleCode",
    "config_template": "Region:{region},Type:{type}",
}

# 条件模块（根据条件添加）
{
    "module_code": "Disk",
    "config_template": "DiskSize:{disk_size}",
    "condition": lambda p: p.get("disk_size", 0) > 0,
}
```

## 验证规则

简单验证（choices）在 PARAMS 中定义：

```python
{
    "name": "spec_type",
    "choices": ["normal", "professional"],  # 自动验证
}
```

复杂验证在 VALIDATION_RULES 中定义：

```python
VALIDATION_RULES = [
    ValidationRule(
        name="disk_size",
        label="磁盘大小",
        min_val=20,
        max_val=32768,
    ),
]
```

## 完整示例

见 `TEMPLATE_EXAMPLE.py`（ECS 产品完整实现）。

## 常见问题

### Q: 如何定义 ProductType？

```python
# 不需要 ProductType
PRODUCT_TYPE = None

# 固定 ProductType
PRODUCT_TYPE = "alikafka_pre"

# 动态 ProductType
PRODUCT_TYPE = lambda p: "alikafka_pre" if p.get("billing") == "subscription" else "alikafka_post"
```

### Q: 如何添加条件模块？

```python
MODULES = [
    {
        "module_code": "DataDisk",
        "config_template": "DataDisk.Size:{data_disk_size}",
        "condition": lambda p: p.get("data_disk_size", 0) > 0,
    },
]
```

### Q: 验证失败怎么办？

运行验证工具会显示具体错误：

```bash
$ python -m ai_friendly.validate kafka
验证产品: kafka

❌ 验证失败:
  - 缺少必需常量: CATEGORY
  - PARAMS[0] 缺少 'type' 字段
```

根据错误提示修复即可。

## 约定

- 所有大写常量必须填写
- 所有列表必须至少有一个元素
- 使用 constants.py 中的常量，不要硬编码字符串
- 保持代码简洁，复杂逻辑放在 _prepare_params 中

## 测试

验证通过后，测试产品：

```bash
# 查看产品信息
python scripts/quoter.py info <product_code>

# 查询价格
python scripts/quoter.py price <product_code> \
  --params '{"region":"cn-hangzhou",...}' \
  --region cn-hangzhou \
  --billing subscription \
  --duration 1
```

---

Happy coding! 🚀
