---
name: aliyun-sa-quoter
description: >
  Query Alibaba Cloud product pricing via BSS OpenAPI. Supports ECS, RDS, SLB,
  OSS, CDN, and EIP. Use when the user wants to query, estimate, or compare
  Alibaba Cloud (aliyun) product prices, cost estimation, server quotes, or
  cloud resource budgeting.
---

# Alibaba Cloud Quoter

Query real-time Alibaba Cloud product prices via BSS OpenAPI. Supports 8 products: ECS, RDS, SLB, EIP, OSS, CDN, WAF, Bailian (百炼大模型).

## Products

### BSS API Products (实时价格)
- **ECS** - 云服务器
- **RDS** - 云数据库
- **SLB** - 负载均衡
- **EIP** - 弹性公网IP
- **OSS** - 对象存储
- **CDN** - 内容分发网络
- **WAF** - Web应用防火墙

### Local Calculation Products (静态定价表)
- **Bailian** - 百炼大模型（通义千问系列）

## Prerequisites

This skill uses only Python standard library -- no pip install or venv needed. Just requires Python 3.6+.

Verify credentials before first use:
```bash
python3 scripts/quoter.py check
```

If credentials are missing, instruct the user to set environment variables:

```bash
export ALIBABA_CLOUD_ACCESS_KEY_ID=your_access_key_id
export ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_access_key_secret
```

Access keys can be obtained from: Alibaba Cloud Console -> AccessKey Management
(https://ram.console.aliyun.com/manage/ak)

## Workflow

When a user asks about Alibaba Cloud pricing, follow these steps:

```
Task Progress:
- [ ] Step 1: Check credentials
- [ ] Step 2: Map user request to product parameters
- [ ] Step 3: Execute pricing query
- [ ] Step 4: Present results to user
```

**Step 1: Check credentials**

Run from this file's directory:
```bash
python3 scripts/quoter.py check
```
If this fails, show the user the credential setup instructions above.

**Step 2: Map user request to product parameters**

Identify: product type, region, instance spec, billing method, duration.
See "Parameter Mapping" section below for common mappings.

**Step 3: Execute pricing query**

Run the appropriate price command (see "Script Reference" below).

**Step 4: Present results**

The script outputs Markdown-formatted pricing. Present it directly to the user.

## Script Reference

All commands run from this file's directory using `python3`.

### Check credentials
```bash
python3 scripts/quoter.py check
```

### List products
```bash
python3 scripts/quoter.py products
```

### Discover pricing modules
```bash
python3 scripts/quoter.py modules ecs --type Subscription
python3 scripts/quoter.py modules rds --type PayAsYouGo
```

### Query ECS price
```bash
python3 scripts/quoter.py price ecs \
  --params '{"instance_type":"ecs.g7.xlarge","image_os":"linux","system_disk_category":"cloud_essd","system_disk_size":40,"data_disk_size":100,"internet_bandwidth":5}' \
  --region cn-hangzhou \
  --billing subscription \
  --duration 1 \
  --quantity 2
```

### Query RDS price
```bash
python3 scripts/quoter.py price rds \
  --params '{"engine":"mysql","engine_version":"8.0","series":"HighAvailability","instance_class":"mysql.n2.medium.2c","storage_type":"local_ssd","storage_size":100}' \
  --region cn-hangzhou \
  --billing subscription \
  --duration 1
```

### Query SLB price
```bash
python3 scripts/quoter.py price slb \
  --params '{"spec":"slb.s3.large","internet_charge_type":1}' \
  --region cn-hangzhou \
  --billing subscription \
  --duration 1
```

### Query EIP price
```bash
python3 scripts/quoter.py price eip \
  --params '{"bandwidth":5,"internet_charge_type":"PayByTraffic"}' \
  --region cn-hangzhou \
  --billing subscription \
  --duration 1
```

### Query OSS price
```bash
python3 scripts/quoter.py price oss \
  --params '{"storage_class":"Standard","capacity":500}' \
  --region cn-hangzhou \
  --billing subscription \
  --duration 1
```

### Query CDN price
```bash
python3 scripts/quoter.py price cdn \
  --params '{"traffic_package":1000}' \
  --region cn-hangzhou \
  --billing subscription \
  --duration 1
```

### Query WAF price
```bash
# 包年包月 - 基础企业版
python3 scripts/quoter.py price waf \
  --params '{"billing_mode":"subscription","package_code":"version_4","region":"cn-hangzhou"}' \
  --billing subscription \
  --duration 1

# 包年包月 - 带扩展功能
python3 scripts/quoter.py price waf \
  --params '{"billing_mode":"subscription","package_code":"version_4","region":"cn-hangzhou","qps_package":10,"bot_web":1,"apisec":1}' \
  --billing subscription \
  --duration 1

# 按量付费
python3 scripts/quoter.py price waf \
  --params '{"billing_mode":"payasyougo","secu":100,"region":"cn-hangzhou"}' \
  --billing payAsYouGo
```

### Query Bailian (百炼大模型) price
```bash
# 基础查询
python3 scripts/quoter.py price bailian \
  --params '{"model":"qwen3-max","input_tokens":100000,"output_tokens":50000}'

# 指定地域
python3 scripts/quoter.py price bailian \
  --params '{"model":"qwen3-max","region":"global","input_tokens":100000,"output_tokens":50000}'

# Batch 调用（50% 折扣）
python3 scripts/quoter.py price bailian \
  --params '{"model":"qwen3-max","input_tokens":100000,"output_tokens":50000,"batch":true}'

# 思考模式（部分模型支持）
python3 scripts/quoter.py price bailian \
  --params '{"model":"qwen3.5-plus","input_tokens":100000,"output_tokens":50000,"thinking":true}'
```

## Parameter Mapping

Map natural language to `--params` JSON keys:

| User says | Product | Key params JSON |
|-----------|---------|----------------|
| "4核8G服务器" | ecs | `{"instance_type":"ecs.c7.xlarge"}` (4C8G) |
| "4核16G服务器" | ecs | `{"instance_type":"ecs.g7.xlarge"}` (4C16G) |
| "2核4G" | ecs | `{"instance_type":"ecs.c7.large"}` (2C4G) |
| "8核32G" | ecs | `{"instance_type":"ecs.g7.2xlarge"}` (8C32G) |
| "MySQL数据库" | rds | `{"engine":"mysql"}` |
| "PostgreSQL" | rds | `{"engine":"postgresql"}` |
| "负载均衡" | slb | product=slb |
| "弹性IP/公网IP" | eip | product=eip |
| "对象存储" | oss | product=oss |
| "CDN加速" | cdn | product=cdn |
| "WAF防火墙" | waf | product=waf |
| "百炼大模型" | bailian | product=bailian |
| "通义千问" | bailian | `{"model":"qwen3-max"}` |
| "杭州/华东1" | any | `--region cn-hangzhou` |
| "北京/华北2" | any | `--region cn-beijing` |
| "上海/华东2" | any | `--region cn-shanghai` |
| "深圳/华南1" | any | `--region cn-shenzhen` |
| "包月/包年包月" | any | `--billing subscription` |
| "按量/按量付费" | any | `--billing payAsYouGo` |
| "1年" | any | `--duration 12` |
| "3年" | any | `--duration 36` |

### ECS Instance Type Reference

| vCPU | Memory | Compute (c7) | General (g7) | Memory (r7) |
|------|--------|-------------|-------------|-------------|
| 2 | 4G/8G/16G | ecs.c7.large | ecs.g7.large | ecs.r7.large |
| 4 | 8G/16G/32G | ecs.c7.xlarge | ecs.g7.xlarge | ecs.r7.xlarge |
| 8 | 16G/32G/64G | ecs.c7.2xlarge | ecs.g7.2xlarge | ecs.r7.2xlarge |
| 16 | 32G/64G/128G | ecs.c7.4xlarge | ecs.g7.4xlarge | ecs.r7.4xlarge |

- **c7** (计算型): CPU:Memory = 1:2
- **g7** (通用型): CPU:Memory = 1:4
- **r7** (内存型): CPU:Memory = 1:8

## Error Handling

- **Credentials missing**: Script prints setup instructions with the AccessKey management URL. Guide the user to configure environment variables.
- **API errors**: Script returns friendly Chinese error messages. If a product query fails, suggest using `quoter.py modules <product>` to discover valid parameters.
- **Unknown instance type**: Suggest the user check Alibaba Cloud documentation or use the ECS Instance Type Reference table above.

## Detailed Reference

For complete ModuleCode, Config format, and parameter values for each product, see [product-reference.md](product-reference.md).
