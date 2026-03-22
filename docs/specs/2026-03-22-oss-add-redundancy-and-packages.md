# OSS 产品添加冗余类型和资源包支持

## 背景

当前 OSS 产品存在以下问题：
1. 无法区分本地冗余(LRS)和同城冗余(ZRS)，两者价格不同
2. 不支持查询资源包价格（包年包月）
3. `StorageZRSXC` 模块配置可能有问题

## 目标

1. 添加 `redundancy_type` 参数支持 LRS/ZRS
2. 修复 ZRS 存储的 BSS API 查询
3. 添加 OSS 资源包固定价格表

## 技术方案

### 方案：增强 OSS 产品定义

修改 `products/oss.py`：
1. 添加 `redundancy_type` 参数
2. 根据冗余类型选择正确的 BSS 模块
3. 添加资源包价格表

## 实现计划

### Task 1: 添加冗余类型参数

**文件:** `skill/scripts/products/oss.py`

**变更:**
1. 添加 `redundancy_type` 参数（`LRS`/`ZRS`）
2. 修改 `build_modules` 函数，根据冗余类型选择模块
3. 添加资源包价格表

**关键代码:**
```python
# 存储类型和冗余类型映射到 BSS 模块
MODULE_MAP = {
    ("Standard", "LRS"): "Storage",  # 标准-本地冗余
    ("Standard", "ZRS"): "StorageZRSXC",  # 标准-同城冗余
    ("IA", "LRS"): "IaOrAchieveChargedStorage",  # 低频-本地冗余
    ("IA", "ZRS"): "ChargedDatasizeZRS",  # 低频-同城冗余
    ("Archive", "LRS"): "IaOrAchieveChargedStorage",  # 归档-本地冗余
    ("Archive", "ZRS"): "ChargedDataSizeArcZRS",  # 归档-同城冗余
}

# 资源包价格表（中国内地）
RESOURCE_PACKAGES = {
    "standard_lrs": {  # 标准-本地冗余
        "40GB": {"month": 4.98, "half_year": None, "year": 9},
        "100GB": {"month": 11, "half_year": 54.78, "year": 99},
        "500GB": {"month": 54, "half_year": 268.92, "year": 486},
        "1TB": {"month": 111, "half_year": 552.78, "year": 999},
        # ... 更多规格
    },
    "standard_zrs": {  # 标准-同城冗余
        "100GB": {"month": 14, "half_year": 69.72, "year": 126},
        "500GB": {"month": 68, "half_year": 338.64, "year": 612},
        # ... 更多规格
    },
    # ... 其他存储类型
}
```

### Task 2: 支持包年包月计费

**变更:**
- 当 `billing=subscription` 时，使用资源包价格表
- 当 `billing=payAsYouGo` 时，使用 BSS API

### Task 3: 测试验证

**测试用例:**
1. 标准-本地冗余 100GB 按量付费
2. 标准-同城冗余 100GB 按量付费
3. 标准-同城冗余 100GB 资源包（包月）
4. 低频-本地冗余 100GB 按量付费

## 接口变更

### 新增参数

```json
{
  "redundancy_type": {
    "type": "string",
    "choices": ["LRS", "ZRS"],
    "default": "LRS",
    "description": "LRS (本地冗余) / ZRS (同城冗余)"
  }
}
```

### 示例调用

```bash
# 标准-本地冗余 100GB 按量付费
quoter.py price oss --params '{"storage_class":"Standard","redundancy_type":"LRS","capacity":100}' --billing payAsYouGo

# 标准-同城冗余 100GB 按量付费
quoter.py price oss --params '{"storage_class":"Standard","redundancy_type":"ZRS","capacity":100}' --billing payAsYouGo

# 标准-同城冗余 100GB 资源包（包月）
quoter.py price oss --params '{"storage_class":"Standard","redundancy_type":"ZRS","capacity":100}' --billing subscription --duration 1
```

## 验证清单

- [ ] LRS 存储使用 `Storage` 模块，价格正确
- [ ] ZRS 存储使用 `StorageZRSXC` 模块，价格正确
- [ ] 资源包价格查询返回固定价格表
- [ ] 按量付费和包年包月切换正常
