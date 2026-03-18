# Spec: 清理 aliyun-sa-quoter 冗余代码

**任务 ID**: 2026-03-18-cleanup-redundant-imports  
**创建时间**: 2026-03-18 16:00  
**方案**: 方案 A (完整清理)

---

## 1. 任务目标

清理 aliyun-sa-quoter 项目中 12 个产品文件的冗余 import，并为 5 个文件添加统一的 `__main__` 验证块。

---

## 2. 文件修改清单

### 2.1 需要清理冗余 import 的文件 (12个)

| 文件 | 冗余 typing | 冗余 types | 冗余 constants |
|------|------------|-----------|---------------|
| alikafka.py | Any, Callable | ParamDef, ModuleSpec | - |
| bailian.py | Any | ParamDef | - |
| cdn.py | Any, Optional, Union | ParamDef, ModuleSpec | Region, DiskType |
| ecs.py | Any, Optional, Union | ParamDef, ModuleSpec | Region |
| eip.py | Any, Optional, Union | ParamDef, ModuleSpec | Region, DiskType |
| elasticsearch.py | Any, Callable | ParamDef, ModuleSpec | - |
| nas.py | Any, Callable | ParamDef, ModuleSpec | ProductType |
| oss.py | Any, Optional, Union | ParamDef, ModuleSpec | Region, DiskType |
| polardb.py | Any, Callable, Optional, Union | ParamDef, ModuleSpec | BillingType |
| rds.py | Any, Callable | ParamDef, ModuleSpec | - |
| slb.py | Any, Optional, Union | ParamDef, ModuleSpec | Region, DiskType |
| waf.py | Any, Callable | ParamDef, ModuleSpec | - |

### 2.2 需要添加 __main__ 块的文件 (5个)

- cdn.py
- ecs.py
- eip.py
- oss.py
- slb.py

---

## 3. 具体修改内容

### 3.1 Import 清理规则

对于每个文件，需要:

1. **typing import**: 只保留实际使用的类型
   - 检查函数签名中的类型注解
   - 保留: `Dict`, `List` (如果用于 `Dict[str, Any]`, `List[Dict[str, str]]`)
   - 删除: `Any`, `Callable`, `Optional`, `Union` (如果未使用)

2. **ai_friendly.types import**: 
   - 当前所有产品都未使用 `ParamDef` 和 `ModuleSpec`
   - 删除整行: `from ai_friendly.types import ParamDef, ModuleSpec`

3. **ai_friendly.constants import**:
   - 删除未使用的常量
   - 保留实际使用的: `Category`, `DiskType` (如果用于默认值), `BillingType` (如果使用), 等

### 3.2 __main__ 块模板

为 5 个文件添加的标准 `__main__` 块:

```python
if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    # Add project root to path
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
```

---

## 4. 验证步骤

### 4.1 单文件验证

每个文件修改后，运行:
```bash
cd ~/Desktop/aliyun-sa-quoter/skill/scripts
python products/<filename>.py
```

期望输出: `✅ 验证通过`

### 4.2 整体验证

```bash
cd ~/Desktop/aliyun-sa-quoter
python -m pytest tests/ -v
```

期望: 所有测试通过

### 4.3 Registry 验证

```bash
cd ~/Desktop/aliyun-sa-quoter/skill/scripts
python -c "from framework import registry; registry.discover_products(); print('产品数:', len(registry.get_all_codes())); print('产品:', registry.get_all_codes())"
```

期望: 15 个产品全部注册成功

---

## 5. 回滚方案

如果出现问题，使用 git 回滚:

```bash
cd ~/Desktop/aliyun-sa-quoter
git checkout -- skill/scripts/products/
```

---

## 6. 提交信息

```
refactor: 清理冗余 import 并统一 __main__ 验证块

- 删除 12 个产品文件中未使用的 import
  - typing: Any, Callable, Optional, Union
  - ai_friendly.types: ParamDef, ModuleSpec
  - ai_friendly.constants: Region, DiskType, ProductType, BillingType

- 为 5 个产品文件添加 __main__ 验证块
  - cdn.py, ecs.py, eip.py, oss.py, slb.py

- 保持所有 15 个产品功能正常
```

---

## 7. 注意事项

1. 修改前确保 git 工作区干净
2. 逐个文件修改并验证
3. 保留文件中的注释和文档字符串
4. 不要修改文件的其他逻辑
5. 确保 import 删除后不会破坏代码功能
