---
name: aliyun-sa-quoter
description: >
  Query Alibaba Cloud product pricing via BSS OpenAPI and product-specific DescribePrice APIs. 
  Supports 12 products including ECS, RDS, MongoDB, Redis, SLB, EIP, OSS, NAS, CDN, WAF, 
  RocketMQ, and Bailian LLM. Use when the user wants to query, estimate, or compare 
  Alibaba Cloud (aliyun) product prices, cost estimation, server quotes, or cloud resource budgeting.
---

# Alibaba Cloud Quoter

Query real-time Alibaba Cloud product prices via **BSS OpenAPI** and **product-specific DescribePrice APIs**. Supports **12 products** across compute, database, network, storage, security, middleware, and AI.

## API Implementation Status

| Product | API Used | Accuracy |
|---------|----------|----------|
| **ECS** | ECS DescribePrice API | ✅ High |
| **RDS** | RDS DescribePrice API | ✅ High |
| **Redis** | Redis DescribePrice API | ✅ High |
| MongoDB | BSS OpenAPI | ⚠️ Medium |
| SLB | BSS OpenAPI | ⚠️ Medium |
| EIP | BSS OpenAPI | ⚠️ Medium |
| OSS | BSS OpenAPI | ⚠️ Medium |
| NAS | BSS OpenAPI | ⚠️ Medium |
| CDN | BSS OpenAPI | ⚠️ Medium |
| WAF | BSS OpenAPI | ⚠️ Medium |
| RocketMQ | BSS OpenAPI | ⚠️ Medium |
| Bailian | Local Calculation | ✅ High |

**Note**: Products using DescribePrice API (ECS, RDS, Redis) provide more accurate pricing and real-time availability checking.

## Products Overview

### Compute (计算)
| Product | Code | Description | Billing |
|---------|------|-------------|---------|
| **ECS** | `ecs` | 云服务器 | Subscription/PayAsYouGo |

### Database (数据库)
| Product | Code | Description | Billing |
|---------|------|-------------|---------|
| **RDS** | `rds` | 关系型数据库 (MySQL, PostgreSQL, SQL Server) | Subscription/PayAsYouGo |
| **MongoDB** | `mongodb` | 云数据库 MongoDB 版 | Subscription/PayAsYouGo |
| **Redis** | `redis` | 云数据库 Redis 版 | Subscription/PayAsYouGo |

### Network (网络)
| Product | Code | Description | Billing |
|---------|------|-------------|---------|
| **SLB** | `slb` | 负载均衡 | Subscription |
| **EIP** | `eip` | 弹性公网IP | Subscription |

### Storage (存储)
| Product | Code | Description | Billing |
|---------|------|-------------|---------|
| **OSS** | `oss` | 对象存储 | PayAsYouGo |
| **NAS** | `nas` | 文件存储 NAS | PayAsYouGo |

### CDN & Security (CDN与安全)
| Product | Code | Description | Billing |
|---------|------|-------------|---------|
| **CDN** | `cdn` | 内容分发网络 | PayAsYouGo |
| **WAF** | `waf` | Web应用防火墙 | Subscription/PayAsYouGo |

### Middleware (中间件)
| Product | Code | Description | Billing |
|---------|------|-------------|---------|
| **RocketMQ** | `rocketmq` | 消息队列 RocketMQ 版 | Subscription/PayAsYouGo |

### AI (人工智能)
| Product | Code | Description | Billing |
|---------|------|-------------|---------|
| **Bailian** | `bailian` | 百炼大模型（通义千问系列） | Local Calculation |

---

## Prerequisites

### Environment Configuration

The skill requires Alibaba Cloud AccessKey credentials. Check these locations for existing configuration:

- `~/.profile`
- `~/.zshrc`
- `~/.bashrc`

Look for:
```bash
export ALIBABA_CLOUD_ACCESS_KEY_ID=your_access_key_id
export ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_access_key_secret
```

### Credential Verification

Verify credentials before first use:
```bash
python3 scripts/quoter.py check
```

If credentials are missing, set environment variables:
```bash
export ALIBABA_CLOUD_ACCESS_KEY_ID=your_access_key_id
export ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_access_key_secret
```

Access keys: https://ram.console.aliyun.com/manage/ak

---

## Core Features

### 1. Batch Query (批量查询)

Query multiple configurations in parallel:

```bash
python3 quoter.py price ecs \
  --params '[
    {"instance_type":"ecs.c6.4xlarge","data_disk_size":100},
    {"instance_type":"ecs.r9i.2xlarge","data_disk_size":200}
  ]' \
  --region cn-beijing
```

**Output**: Markdown table with all results and total price.

### 2. Exclude System Disk (排除系统盘)

Get instance-only pricing (useful when comparing instance types):

```bash
python3 quoter.py price ecs \
  --params '{"instance_type":"ecs.c6.4xlarge"}' \
  --exclude-system-disk
```

---

## Quick Reference

### Common Commands

```bash
# Check credentials
python3 quoter.py check

# List all products
python3 quoter.py products

# Get product info
python3 quoter.py info ecs

# Discover pricing modules
python3 quoter.py modules ecs --type Subscription
```

### ECS (云服务器)

```bash
# Basic query
python3 quoter.py price ecs \
  --params '{"instance_type":"ecs.g7.xlarge","system_disk_size":40}'

# With data disk and bandwidth
python3 quoter.py price ecs \
  --params '{
    "instance_type":"ecs.g7.xlarge",
    "system_disk_size":40,
    "data_disk_size":100,
    "internet_bandwidth":5
  }'

# Exclude system disk (instance-only price)
python3 quoter.py price ecs \
  --params '{"instance_type":"ecs.g7.xlarge"}' \
  --exclude-system-disk

# Batch query
python3 quoter.py price ecs \
  --params '[
    {"instance_type":"ecs.c6.4xlarge"},
    {"instance_type":"ecs.r9i.2xlarge"},
    {"instance_type":"ecs.r9i.4xlarge"}
  ]'
```

### RDS (云数据库)

```bash
# MySQL
python3 quoter.py price rds \
  --params '{
    "engine":"mysql",
    "engine_version":"8.0",
    "series":"HighAvailability",
    "instance_class":"mysql.n2.medium.2c",
    "storage_type":"local_ssd",
    "storage_size":100
  }'

# PostgreSQL
python3 quoter.py price rds \
  --params '{
    "engine":"postgresql",
    "engine_version":"14.0",
    "series":"HighAvailability",
    "instance_class":"pg.n2.medium.2c",
    "storage_size":100
  }'
```

### MongoDB

```bash
python3 quoter.py price mongodb \
  --params '{
    "region":"cn-hangzhou",
    "instance_class":"mdb.shard.2x.large.d",
    "storage_size":100
  }'
```

### Redis

```bash
python3 quoter.py price redis \
  --params '{
    "region":"cn-hangzhou",
    "instance_class":"redis.master.small.default",
    "architecture":"standard"
  }'
```

### SLB (负载均衡)

```bash
python3 quoter.py price slb \
  --params '{"spec":"slb.s3.large","internet_charge_type":1}'
```

### EIP (弹性公网IP)

```bash
python3 quoter.py price eip \
  --params '{"bandwidth":5,"internet_charge_type":"PayByTraffic"}'
```

### OSS (对象存储)

```bash
python3 quoter.py price oss \
  --params '{"storage_class":"Standard","capacity":500}' \
  --billing payAsYouGo
```

### NAS (文件存储)

```bash
python3 quoter.py price nas \
  --params '{
    "region":"cn-hangzhou",
    "file_system_type":"standard",
    "storage_type":"Performance",
    "capacity":1000
  }' \
  --billing payAsYouGo
```

### CDN

```bash
python3 quoter.py price cdn \
  --params '{"traffic_package":1000}' \
  --billing payAsYouGo
```

### WAF (Web应用防火墙)

```bash
# Subscription
python3 quoter.py price waf \
  --params '{
    "billing_mode":"subscription",
    "package_code":"version_4",
    "region":"cn-hangzhou"
  }'

# PayAsYouGo
python3 quoter.py price waf \
  --params '{
    "billing_mode":"payasyougo",
    "secu":100,
    "region":"cn-hangzhou"
  }' \
  --billing payAsYouGo
```

### RocketMQ

```bash
python3 quoter.py price rocketmq \
  --params '{
    "region":"cn-hangzhou",
    "instance_class":"rocketmq.n1.micro"
  }'
```

### Bailian (百炼大模型)

```bash
# Basic
python3 quoter.py price bailian \
  --params '{
    "model":"qwen3-max",
    "input_tokens":100000,
    "output_tokens":50000
  }'

# Batch mode (50% discount)
python3 quoter.py price bailian \
  --params '{
    "model":"qwen3-max",
    "input_tokens":100000,
    "output_tokens":50000,
    "batch":true
  }'

# Thinking mode
python3 quoter.py price bailian \
  --params '{
    "model":"qwen3.5-plus",
    "input_tokens":100000,
    "output_tokens":50000,
    "thinking":true
  }'
```

---

## Parameter Mapping

### Natural Language to Parameters

| User Request | Product | Parameters |
|-------------|---------|------------|
| "4核8G服务器" | ecs | `{"instance_type":"ecs.c7.xlarge"}` |
| "4核16G服务器" | ecs | `{"instance_type":"ecs.g7.xlarge"}` |
| "8核64G内存型" | ecs | `{"instance_type":"ecs.r7.2xlarge"}` |
| "MySQL数据库" | rds | `{"engine":"mysql"}` |
| "PostgreSQL" | rds | `{"engine":"postgresql"}` |
| "MongoDB" | mongodb | `{}` |
| "Redis缓存" | redis | `{}` |
| "负载均衡" | slb | `{}` |
| "公网IP" | eip | `{}` |
| "对象存储" | oss | `{}` |
| "文件存储" | nas | `{}` |
| "CDN" | cdn | `{}` |
| "WAF防火墙" | waf | `{}` |
| "RocketMQ" | rocketmq | `{}` |
| "百炼/通义千问" | bailian | `{"model":"qwen3-max"}` |
| "杭州/华东1" | any | `--region cn-hangzhou` |
| "北京/华北2" | any | `--region cn-beijing` |
| "上海/华东2" | any | `--region cn-shanghai` |
| "深圳/华南1" | any | `--region cn-shenzhen` |
| "包年包月" | any | `--billing subscription` |
| "按量付费" | any | `--billing payAsYouGo` |
| "1年" | any | `--duration 12` |
| "3年" | any | `--duration 36` |

### ECS Instance Type Reference

| vCPU | Memory | Compute (c7) | General (g7) | Memory (r7) |
|------|--------|-------------|-------------|-------------|
| 2 | 4G/8G/16G | ecs.c7.large | ecs.g7.large | ecs.r7.large |
| 4 | 8G/16G/32G | ecs.c7.xlarge | ecs.g7.xlarge | ecs.r7.xlarge |
| 8 | 16G/32G/64G | ecs.c7.2xlarge | ecs.g7.2xlarge | ecs.r7.2xlarge |
| 16 | 32G/64G/128G | ecs.c7.4xlarge | ecs.g7.4xlarge | ecs.r7.4xlarge |
| 32 | 64G/128G/256G | ecs.c7.8xlarge | ecs.g7.8xlarge | ecs.r7.8xlarge |

- **c7** (计算型): CPU:Memory = 1:2
- **g7** (通用型): CPU:Memory = 1:4
- **r7** (内存型): CPU:Memory = 1:8

---

## Multi-Instance Price Comparison

When user specifies requirements like "16核64G", query multiple instance types:

```bash
python3 quoter.py price ecs \
  --params '[
    {"instance_type":"ecs.g7.4xlarge"},
    {"instance_type":"ecs.g8y.4xlarge"},
    {"instance_type":"ecs.g8a.4xlarge"}
  ]' \
  --region cn-beijing
```

**Output comparison table**:
| 实例类型 | 系列 | 价格/月 | 推荐度 |
|----------|------|---------|--------|
| ecs.g8y.4xlarge | ARM | ¥1,576 | ⭐ 最优 |
| ecs.g8a.4xlarge | AMD | ¥1,999 | 较好 |
| ecs.g7.4xlarge | Intel | ¥2,049 | 标准 |

---

## Error Handling

| Error | Solution |
|-------|----------|
| Credentials missing | Set `ALIBABA_CLOUD_ACCESS_KEY_ID` and `ALIBABA_CLOUD_ACCESS_KEY_SECRET` |
| API errors | Check `quoter.py modules <product>` for valid parameters |
| Invalid instance type | Use ECS Instance Type Reference table |

---

## Known Limitations

### Billing Mode Limitations

| Product | Subscription | PayAsYouGo |
|---------|-----------|------------|
| ECS | ✅ | ✅ |
| RDS | ✅ | ✅ |
| MongoDB | ✅ | ✅ |
| Redis | ✅ | ✅ |
| SLB | ✅ | ❌ |
| EIP | ✅ | ❌ |
| OSS | ❌ | ✅ |
| NAS | ❌ | ✅ |
| CDN | ❌ | ✅ |
| WAF | ✅ | ✅ |
| RocketMQ | ✅ | ✅ |
| Bailian | N/A | N/A (Local) |

### Product Code Mappings

Some products use different codes in BSS API:

| Display Name | BSS API Code |
|-------------|--------------|
| polardb | drds (PolarDB-X 1.0) |

---

## Detailed Reference

For complete ModuleCode, Config format, and parameter values, see [product-reference.md](product-reference.md).