# Product Reference - BSS OpenAPI Parameters

Detailed ModuleCode and Config format for each product. Refer to this when the agent needs to understand parameter structure or troubleshoot pricing queries.

## ECS (ProductCode: `ecs`)

### Modules

| ModuleCode | Config Format | Required |
|------------|--------------|----------|
| InstanceType | `InstanceType:{spec},IoOptimized:IoOptimized,ImageOs:{os},InstanceTypeFamily:{family}` | Yes |
| SystemDisk | `SystemDisk.Category:{category},SystemDisk.Size:{size}` | Yes |
| DataDisk | `DataDisk.Category:{category},DataDisk.Size:{size}` | No |
| InternetMaxBandwidthOut | `InternetMaxBandwidthOut:{mbps},InternetMaxBandwidthOut.IsFlowType:{type},NetworkType:1` | No |

### Key Parameter Values

**Instance Type examples**: `ecs.c7.large` (2C4G), `ecs.g7.xlarge` (4C16G), `ecs.r7.2xlarge` (8C64G)

**Instance Family prefix**: extract first two parts, e.g. `ecs.g7.xlarge` -> `ecs.g7`

**ImageOs**: `linux`, `windows`

**Disk Category**: `cloud_essd` (ESSD), `cloud_ssd` (SSD), `cloud_efficiency` (高效云盘)

**InternetMaxBandwidthOut.IsFlowType**: `5` = fixed bandwidth, `1` = by traffic

---

## RDS (ProductCode: `rds`)

### Modules

| ModuleCode | Config Format | Required |
|------------|--------------|----------|
| Engine | `Engine:{engine}` | Yes |
| EngineVersion | `EngineVersion:{version}` | Yes |
| Series | `Series:{series}` | Yes |
| DBInstanceStorageType | `DBInstanceStorageType:{type}` | Yes |
| DBInstanceStorage | `DBInstanceStorage:{size}` | Yes |
| DBInstanceClass | `DBInstanceClass:{class}` | Yes |
| DBNetworkType | `DBNetworkType:{type}` | Yes |

### Key Parameter Values

**Engine**: `mysql`, `postgresql`, `mssql`, `MariaDB`

**EngineVersion**: MySQL: `5.7`, `8.0`; PostgreSQL: `13.0`, `14.0`, `15.0`; MSSQL: `2019_ent`, `2019_std`

**Series**: `Basic` (基础版), `HighAvailability` (高可用版), `AlwaysOn` (集群版)

**DBInstanceStorageType**: `local_ssd`, `cloud_essd`, `cloud_ssd`

**DBInstanceClass examples**: `mysql.n2.medium.2c` (2C4G), `mysql.n4.medium.2c` (2C8G), `mysql.n2.large.2c` (4C8G)

**DBNetworkType**: `0` = classic network, `1` = VPC

**Pay-as-you-go notes**: Use `ProductType=bards` for Basic edition, `ProductType=rords` for read-only instances.

---

## SLB (ProductCode: `slb`)

### Modules

| ModuleCode | Config Format | Required |
|------------|--------------|----------|
| LoadBalancerSpec | `LoadBalancerSpec:{spec}` | Yes |
| InternetTrafficOut | `InternetTrafficOut:{type}` | Yes |
| InstanceRent | `InstanceRent:1` | Yes |
| Bandwidth | `Bandwidth:{kbps}` | Conditional |

### Key Parameter Values

**LoadBalancerSpec**: `slb.s0.share` (共享型), `slb.s1.small` (简约型I), `slb.s2.small` (标准型I), `slb.s2.medium` (标准型II), `slb.s3.small` (高阶型I), `slb.s3.medium` (高阶型II), `slb.s3.large` (超强型I)

**InternetTrafficOut**: `1` = by traffic, `0` = by bandwidth

**Bandwidth**: in Kbps, required when InternetTrafficOut=0

---

## EIP (ProductCode: `eip`)

### Modules

| ModuleCode | Config Format | Required |
|------------|--------------|----------|
| Bindwidth | `Bindwidth:{mbps}` | Yes |
| InternetChargeType | `InternetChargeType:{type}` | Yes |

### Key Parameter Values

**Bindwidth**: bandwidth in Mbps (note: Alibaba Cloud API uses "Bindwidth" spelling)

**InternetChargeType**: `PayByTraffic` (按流量), `PayByBandwidth` (按带宽)

---

## OSS (ProductCode: `oss`)

OSS pricing modules should be discovered dynamically via `quoter.py modules oss`.

### Common Parameters

**StorageClass**: `Standard` (标准存储), `IA` (低频访问), `Archive` (归档存储)

**Capacity**: storage capacity in GB

---

## CDN (ProductCode: `cdn`)

CDN pricing modules should be discovered dynamically via `quoter.py modules cdn`.

### Common Parameters

**TrafficPackage**: traffic package size in GB

---

## Elasticsearch (ProductCode: `elasticsearch`)

### ProductType

- **Subscription (包年包月)**: `elasticsearchpre`
- **PayAsYouGo (按量付费)**: `elasticsearch`

### Modules (MVP Version)

| ModuleCode | Config Format | Required |
|------------|--------------|----------|
| NodeSpec | `NodeSpec:{spec},Region:{region},NodeAmount:{amount}` | Yes |
| Disk | `DataDiskType:{type},PerformanceLevel:{level},Region:{region},NodeAmount:{amount},Disk:{size}` | Yes |

### Key Parameter Values

**NodeSpec (数据节点规格)**:
- `elasticsearch.g7.xlarge` - 4核16G (通用型)
- `elasticsearch.g7.2xlarge` - 8核32G (通用型)
- `elasticsearch.g7.4xlarge` - 16核64G (通用型)
- `elasticsearch.r7.xlarge` - 4核32G (内存型)
- `elasticsearch.r7.2xlarge` - 8核64G (内存型)
- `elasticsearch.c7.xlarge` - 4核8G (计算型)

**DataDiskType (存储类型)**: `cloud_ssd` (SSD云盘), `cloud_essd` (ESSD云盘), `cloud_efficiency` (高效云盘)

**PerformanceLevel (ESSD性能级别)**: `PL0`, `PL1`, `PL2`, `PL3` (仅在使用 cloud_essd 时有效)

**NodeAmount (节点数量)**: 2-50，建议至少3个保证高可用

**Disk (单节点存储)**: 20-20480 GB

### Example Usage

```bash
# 包年包月询价
python scripts/quoter.py price elasticsearch \
  --region cn-hangzhou \
  --node-spec elasticsearch.g7.xlarge \
  --node-amount 3 \
  --disk-type cloud_ssd \
  --disk-size 100 \
  --subscription-type Subscription

# 按量付费询价
python scripts/quoter.py price elasticsearch \
  --region cn-hangzhou \
  --node-spec elasticsearch.r7.2xlarge \
  --node-amount 5 \
  --disk-type cloud_essd \
  --disk-size 500 \
  --performance-level PL2 \
  --subscription-type PayAsYouGo
```

---

## Discovering Module Parameters

For any product, use the `modules` command to discover available pricing modules and their config options:

```bash
python scripts/quoter.py modules ecs --type Subscription
python scripts/quoter.py modules rds --type PayAsYouGo
```

This calls `DescribePricingModule` API and returns all available ModuleCodes with their config keys.
