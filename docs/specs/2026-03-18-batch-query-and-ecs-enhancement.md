# Spec: 批量查询与 ECS 价格逻辑增强

**日期**: 2026-03-18
**任务**: aliyun-sa-quoter 技能增强
**作者**: Holly

---

## 1. 背景与目标

### 1.1 当前问题
1. ECS 查询返回 `InstanceType + SystemDisk + DataDisk`，无法单独查看实例价格
2. 不支持批量查询，多个实例需要多次调用

### 1.2 目标
1. 支持排除 SystemDisk 价格，单独查看实例价格
2. 支持批量并发查询，提高查询效率

---

## 2. 需求规格

### 2.1 功能需求

| ID | 需求 | 优先级 |
|----|------|--------|
| F1 | 添加 `--exclude-system-disk` 参数，SystemDisk 价格设为 0 | P0 |
| F2 | `--params` 支持 JSON 数组输入 | P0 |
| F3 | 数组长度 > 1 时自动并发查询（5 workers） | P0 |
| F4 | 批量查询结果输出汇总表格 | P1 |
| F5 | 向后兼容：单对象 JSON 保持现有行为 | P0 |

### 2.2 接口规格

#### 改造前
```bash
python3 quoter.py price ecs \
  --params '{"instance_type":"ecs.c6.4xlarge","system_disk_size":40}'
```

#### 改造后
```bash
# 单查询，排除系统盘
python3 quoter.py price ecs \
  --params '{"instance_type":"ecs.c6.4xlarge","data_disk_size":100}' \
  --exclude-system-disk

# 批量查询
python3 quoter.py price ecs \
  --params '[
    {"instance_type":"ecs.c6.4xlarge","data_disk_size":100},
    {"instance_type":"ecs.r9i.2xlarge","data_disk_size":200}
  ]'
```

---

## 3. 技术设计

### 3.1 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                         cmd_price                           │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
        单对象 JSON      数组 JSON        解析错误
              │               │
              ▼               ▼
    ┌─────────────────┐ ┌─────────────────┐
    │   现有逻辑      │ │  ThreadPool     │
    │   (同步)        │ │  Executor(5)    │
    └─────────────────┘ └─────────────────┘
              │               │
              │         ┌─────┴─────┐
              │         │  Worker 1 │
              │         │  Worker 2 │
              │         │  Worker 3 │
              │         │  Worker 4 │
              │         │  Worker 5 │
              │         └─────┬─────┘
              │               │
              └───────┬───────┘
                      ▼
            ┌─────────────────┐
            │   结果聚合       │
            │   format_batch  │
            └─────────────────┘
```

### 3.2 核心模块改造

#### 3.2.1 quoter.py - cmd_price

```python
def cmd_price(args):
    """Query product price - supports batch query."""
    product_code = args.product
    
    # 1. 解析 params（支持单对象或数组）
    params_list = _parse_params(args.params)
    
    # 2. 单查询 - 保持现有逻辑
    if len(params_list) == 1:
        return _query_single(product_code, params_list[0], args)
    
    # 3. 批量查询 - 并发执行
    return _query_batch(product_code, params_list, args)


def _parse_params(params_str):
    """Parse params JSON - supports single object or array."""
    try:
        data = json.loads(params_str)
        if isinstance(data, list):
            return data
        return [data]
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")


def _query_batch(product_code, params_list, args):
    """Execute batch queries with concurrency."""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    results = []
    errors = []
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        # 提交所有任务
        future_to_idx = {
            executor.submit(_query_single_sync, product_code, params, args): idx
            for idx, params in enumerate(params_list)
        }
        
        # 收集结果
        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            try:
                result = future.result()
                results.append((idx, result))
            except Exception as e:
                errors.append((idx, str(e)))
    
    # 按原始顺序排序
    results.sort(key=lambda x: x[0])
    
    # 格式化输出
    return _format_batch_results(results, errors)
```

#### 3.2.2 products/ecs.py - build_modules

```python
def build_modules(params: Dict[str, Any]) -> List[Dict[str, str]]:
    """Build ECS pricing module list."""
    # ... existing code ...
    
    # Check if we should exclude system disk
    exclude_system_disk = params.get("exclude_system_disk", False)
    
    modules = [
        {
            "module_code": "InstanceType",
            "config": f"InstanceType:{instance_type},...",
            "price_type": "Hour",
        },
    ]
    
    # SystemDisk - use size 0 if excluded
    if exclude_system_disk:
        modules.append({
            "module_code": "SystemDisk",
            "config": "SystemDisk.Category:cloud_essd,SystemDisk.Size:0",
            "price_type": "Hour",
        })
    else:
        modules.append({
            "module_code": "SystemDisk",
            "config": f"SystemDisk.Category:{system_disk_category},SystemDisk.Size:{system_disk_size}",
            "price_type": "Hour",
        })
    
    # DataDisk - always include if specified
    if data_disk_size and int(data_disk_size) > 0:
        # ... existing code ...
    
    return modules
```

#### 3.2.3 formatters.py - format_batch_results

```python
def format_batch_results(results, errors):
    """Format batch query results as Markdown table."""
    lines = ["## 批量报价结果", ""]
    
    # Summary table
    lines.append("| 序号 | 配置 | 实例价格 | 数据盘 | 总计 |")
    lines.append("|------|------|---------|--------|------|")
    
    total = 0
    for idx, result in results:
        # Extract prices from result
        instance_price = result.get("instance_price", 0)
        disk_price = result.get("disk_price", 0)
        subtotal = result.get("total", 0)
        config = result.get("config_summary", {})
        
        lines.append(f"| {idx+1} | {config.get('实例规格', '-')} | ¥{instance_price:.2f} | ¥{disk_price:.2f} | ¥{subtotal:.2f} |")
        total += subtotal
    
    lines.append("")
    lines.append(f"**总计**: ¥{total:.2f}/月")
    
    # Error summary
    if errors:
        lines.append("")
        lines.append("## 错误")
        for idx, error in errors:
            lines.append(f"- 配置 {idx+1}: {error}")
    
    return "\n".join(lines)
```

---

## 4. 测试用例

### 4.1 单查询 - 排除系统盘
```bash
python3 quoter.py price ecs \
  --params '{"instance_type":"ecs.c6.4xlarge","data_disk_size":100}' \
  --exclude-system-disk

# 期望输出：
# InstanceType: ¥1496
# SystemDisk: ¥0 (mocked)
# DataDisk: ¥100
# Total: ¥1596
```

### 4.2 批量查询
```bash
python3 quoter.py price ecs \
  --params '[
    {"instance_type":"ecs.c6.4xlarge","data_disk_size":100},
    {"instance_type":"ecs.r9i.2xlarge","data_disk_size":200}
  ]'

# 期望输出：
# | 序号 | 配置 | 实例价格 | 数据盘 | 总计 |
# | 1 | ecs.c6.4xlarge | ¥1496 | ¥100 | ¥1636 |
# | 2 | ecs.r9i.2xlarge | ¥1269.91 | ¥200 | ¥1509.91 |
# **总计**: ¥3145.91/月
```

### 4.3 向后兼容
```bash
python3 quoter.py price ecs \
  --params '{"instance_type":"ecs.c6.4xlarge","system_disk_size":40}'

# 期望输出：保持现有格式不变
```

---

## 5. 实施计划

| Phase | 任务 | 预计时间 |
|-------|------|---------|
| Phase 3 | 修改 quoter.py - 支持批量查询 | 30 min |
| Phase 3 | 修改 products/ecs.py - 支持 exclude_system_disk | 15 min |
| Phase 3 | 修改 formatters.py - 批量结果格式化 | 20 min |
| Phase 4 | Code Review | 15 min |
| Phase 5 | 修复问题 | 15 min |
| Phase 6 | Push & Merge | 10 min |

**总计**: 约 1.5 小时

---

## 6. 风险与注意事项

1. **并发限制**: BSS API 可能有 QPS 限制，需要添加 rate limiter
2. **错误处理**: 单个查询失败不应影响其他查询
3. **向后兼容**: 确保单对象 JSON 行为不变

---

## 7. 验收标准

- [ ] `--params` 支持 JSON 数组
- [ ] 数组长度 > 1 时并发执行
- [ ] 添加 `--exclude-system-disk` 参数
- [ ] SystemDisk 价格 mock 为 0
- [ ] 批量查询输出汇总表格
- [ ] 单对象 JSON 向后兼容
- [ ] 所有测试用例通过
