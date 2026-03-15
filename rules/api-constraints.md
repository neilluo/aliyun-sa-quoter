---
trigger: always_on
---
# API 数据源与安全约束

## 数据源原则

- 所有产品 API 参数（ProductCode / ProductType / ModuleCode / Config / 有效值）**必须来自 https://api.aliyun.com/ 官方文档**
- **禁止猜测或凭经验编造任何参数值**
- 每个产品接入前，必须先运行 `quoter.py modules <product>` 实际发现 ModuleCode/Config
- 参数有效值变更时（阿里云调整 API），以官方文档为准，及时更新产品文件

## 产品接入标准流程

```
1. 到 https://api.aliyun.com/ 查阅该产品的 BSS 询价文档
   - 确认 ProductCode、ProductType
   - 查看 GetSubscriptionPrice / GetPayAsYouGoPrice 的调用示例
2. 运行 quoter.py modules <product_code> --type Subscription 发现包年包月模块
3. 运行 quoter.py modules <product_code> --type PayAsYouGo 发现按量付费模块
4. 基于真实数据编写 products/<product>.py
5. 编写测试 tests/test_products/test_<product>.py
6. 运行测试通过
7. 更新 product-reference.md
```

## 安全

- **禁止**在日志、输出、错误消息、代码注释中暴露 AK/SK 凭证
- 凭证仅通过环境变量读取：
  - `ALIBABA_CLOUD_ACCESS_KEY_ID`
  - `ALIBABA_CLOUD_ACCESS_KEY_SECRET`
- 错误消息中不得包含签名字符串或完整请求 URL

## 限流保护

- API 调用遇到 429 / Throttling 自动指数退避重试（最多 3 次）
- 单次会话内控制调用频率，避免触发阿里云 API 限流
- 重试间隔：1s → 2s → 4s（指数退避）
