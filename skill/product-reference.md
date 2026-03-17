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

## WAF (ProductCode: `waf`)

### ProductType

- **Subscription (包年包月)**: `waf_v3prepaid_public_cn`
- **PayAsYouGo (按量付费)**: `waf_v2_public_cn`

### Modules

#### 包年包月 (Subscription)

| ModuleCode | Config Format | Required |
|------------|--------------|----------|
| PackageCode | `Region:{region},PackageCode:{package_code}` | Yes |
| QPSPackage | `botWeb:{0/1},apisec:{0/1},botApp:{0/1},Region:{region},QPSPackage:{qps_package}` | No |
| ExtDomainPackage | `ExtDomainPackage:{ext_domain_package},Region:{region},PackageCode:{package_code}` | No |
| botWeb | `botWeb:1,Region:{region},bot_version:1,PackageCode:{package_code}` | No |
| botApp | `botApp:1,Region:{region},bot_version:1` | No |
| apisec | `apisec:1,Region:{region},PackageCode:{package_code}` | No |
| domainVip | `Region:{region},domainVip:{domain_vip}` | No |
| LogStorage | `Region:{region},LogStorage:{log_storage}` | No |
| WafGslb | `Region:{region},WafGslb:1` | No |
| HybridCloudNode | `Region:{region},PackageCode:{package_code},HybridCloudNode:{hybrid_cloud_node}` | No |
| BlueTeaming | `BlueTeaming:1,Region:{region},PackageCode:{package_code}` | No |
| spikeThrottle | `Region:{region},spikeThrottle:{spike_throttle}` | No |
| ElasticQps | `botWeb:{0/1},apisec:{0/1},botApp:{0/1},Region:{region},ElasticQps:{elastic_qps}` | No |

#### 按量付费 (PayAsYouGo)

| ModuleCode | Config Format | Required |
|------------|--------------|----------|
| SeCU | `SeCU:{secu},Region:{region}` | Yes |

### Key Parameter Values

**billing_mode (计费模式)**: `subscription` (包年包月), `payasyougo` (按量付费)

**package_code (版本，包年包月必填)**:
- `version_3` - 高级版
- `version_4` - 企业版
- `version_5` - 旗舰版

**secu (SeCU数量，按量付费必填)**: ≥1

**扩展参数 (包年包月可选)**:
- `qps_package` - QPS扩展包数量 (≥0)
- `ext_domain_package` - 域名扩展包数量 (≥0)
- `domain_vip` - 独享IP数量 (≥0)
- `log_storage` - 日志存储容量GB (≥0)
- `hybrid_cloud_node` - 混合云扩展节点数 (≥0)
- `spike_throttle` - 洪峰限流配置 (≥0)
- `elastic_qps` - 弹性后付费QPS (≥0)

**安全功能开关 (包年包月可选)**:
- `bot_web` - Bot Web防护 (true/false)
- `bot_app` - Bot APP防护 (true/false)
- `apisec` - API安全防护 (true/false)
- `waf_gslb` - 智能负载均衡 (true/false)
- `blue_teaming` - 重保场景 (true/false)

### Example Usage

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

---

## Kafka (ProductCode: `alikafka`)

### Modules

#### 包年包月 (Subscription, ProductType: `alikafka_pre`)

| ModuleCode | Config Format | Required |
|------------|--------------|----------|
| PartitionNum | `PartitionNum:{partition_num},SpecType:{spec_type},RegionId:{region}` | Yes |
| TopicQuota | `PartitionNum:{partition_num},TopicQuota:{topic_quota},RegionId:{region}` | Yes |
| IoMaxSpec | `SpecType:{spec_type},IoMaxSpec:{io_max_spec},RegionId:{region}` | Yes |
| DiskSize | `DiskType:{disk_type},DiskSize:{disk_size},RegionId:{region}` | Yes |
| EipMax | `EipMax:{eip_max},RegionId:{region}` | No |

#### 按量付费 (PayAsYouGo, ProductType: `alikafka_post`)

| ModuleCode | Config Format | Required |
|------------|--------------|----------|
| PartitionNum | `PartitionNum:{partition_num},SpecType:{spec_type},RegionId:{region}` | Yes |
| TopicQuota | `PartitionNum:{partition_num},TopicQuota:{topic_quota},RegionId:{region}` | Yes |
| IoMaxSpec | `SpecType:{spec_type},IoMaxSpec:{io_max_spec},RegionId:{region}` | Yes |
| DiskSize | `DiskType:{disk_type},DiskSize:{disk_size},RegionId:{region}` | Yes |
| EipMax | `EipMax:{eip_max},RegionId:{region}` | No |

### Key Parameter Values

**spec_type (规格类型)**:
- `normal` - 标准版（高写）
- `professional` - 专业版（高写）
- `professionalForHighRead` - 专业版（高读）

**disk_type (磁盘类型)**:
- `0` - 高效云盘
- `1` - SSD
- `5` - ESSD_PL0
- `6` - ESSD_PL1

**io_max_spec (流量规格)**:
- 高写版 (normal/professional): `alikafka.hw.2xlarge`, `alikafka.hw.3xlarge`, `alikafka.hw.6xlarge`, `alikafka.hw.9xlarge`, `alikafka.hw.12xlarge`
- 高读版 (professionalForHighRead): `alikafka.hr.2xlarge`, `alikafka.hr.3xlarge`, `alikafka.hr.6xlarge`, `alikafka.hr.9xlarge`, `alikafka.hr.12xlarge`

**参数范围**:
- `partition_num`: 0-40000
- `topic_quota`: 1-9999
- `disk_size`: ≥100 (GB)
- `eip_max`: 0-2500 (MB/s), 0表示不开通

### Example Usage

```bash
# 包年包月 - 标准版基础配置
python3 scripts/quoter.py price alikafka \
  --params '{"spec_type":"normal","partition_num":100,"topic_quota":50,"disk_type":"1","disk_size":500,"region":"cn-hangzhou"}' \
  --billing subscription \
  --duration 1

# 包年包月 - 专业版高读版带公网
python3 scripts/quoter.py price alikafka \
  --params '{"spec_type":"professionalForHighRead","partition_num":500,"topic_quota":100,"disk_type":"6","disk_size":1000,"eip_max":100,"region":"cn-hangzhou"}' \
  --billing subscription \
  --duration 1

# 按量付费
python3 scripts/quoter.py price alikafka \
  --params '{"spec_type":"professional","partition_num":1000,"topic_quota":200,"disk_type":"6","disk_size":2000,"region":"cn-hangzhou"}' \
  --billing payAsYouGo
```

---

## RocketMQ 5.0 (ProductCode: `ons`)

### Modules

#### 包年包月 (Subscription, ProductType: `ons_rmqsub_public_cn`)

| ModuleCode | Config Format | Required |
|------------|--------------|----------|
| msg_process_spec | `chip_type:{chip_type},region:{region},msg_process_spec:{spec}` | Yes |
| msg_store_spec | `msg_store_spec:{spec},region:{region}` | Yes |
| flow_out_bandwidth | `flow_out_bandwidth:{bandwidth},flow_out_type:{type},region:{region}` | No |
| topic_paid | `region:{region},series_type:{series}` | No |

#### 按量付费 (PayAsYouGo, ProductType: `ons_rmqpost_public_cn`)

| ModuleCode | Config Format | Required |
|------------|--------------|----------|
| msg_process_spec | `chip_type:{chip_type},region:{region},msg_process_spec:{spec}` | Yes |
| msg_store_spec | `msg_store_spec:{spec},region:{region}` | Yes |
| flow_out_bandwidth | `flow_out_bandwidth:{bandwidth},flow_out_type:{type},region:{region}` | No |
| topic_paid | `region:{region},series_type:{series}` | No |

### Key Parameter Values

**chip_type (架构类型)**: `x86`, `arm`

**msg_process_spec (消息收发计算规格)**:
- x86: `rmq.su.2xlarge` (8C16G), `rmq.su.4xlarge` (16C32G), `rmq.su.6xlarge` (24C48G), `rmq.su.8xlarge` (32C64G)
- arm: `rmq.su.2xlarge` (8C16G), `rmq.su.4xlarge` (16C32G), `rmq.su.6xlarge` (24C48G)

**msg_store_spec (消息存储规格)**: `rmq.ssu.2xlarge`, `rmq.ssu.4xlarge`, `rmq.ssu.6xlarge`, `rmq.ssu.8xlarge`

**series_type (系列类型)**: `standard` (标准版), `professional` (专业版)

**flow_out_type (公网计费类型)**: `payByTraffic` (按流量), `fixedBandwidth` (固定带宽)

**参数范围**:
- `flow_out_bandwidth`: 0-600 (MB/s), 0表示不开通
- `topic_paid`: ≥0

### Example Usage

```bash
# 包年包月 - x86标准版基础配置
python3 scripts/quoter.py price ons \
  --params '{"chip_type":"x86","msg_process_spec":"rmq.su.2xlarge","msg_store_spec":"rmq.ssu.2xlarge","series_type":"standard","region":"cn-hangzhou"}' \
  --billing subscription \
  --duration 1

# 包年包月 - arm专业版带公网和付费Topic
python3 scripts/quoter.py price ons \
  --params '{"chip_type":"arm","msg_process_spec":"rmq.su.4xlarge","msg_store_spec":"rmq.ssu.4xlarge","series_type":"professional","flow_out_bandwidth":100,"flow_out_type":"payByTraffic","topic_paid":10,"region":"cn-hangzhou"}' \
  --billing subscription \
  --duration 1

# 按量付费
python3 scripts/quoter.py price ons \
  --params '{"chip_type":"x86","msg_process_spec":"rmq.su.6xlarge","msg_store_spec":"rmq.ssu.6xlarge","series_type":"professional","region":"cn-hangzhou"}' \
  --billing payAsYouGo
```

---

## Discovering Module Parameters

For any product, use the `modules` command to discover available pricing modules and their config options:

```bash
python scripts/quoter.py modules ecs --type Subscription
python scripts/quoter.py modules rds --type PayAsYouGo
```

This calls `DescribePricingModule` API and returns all available ModuleCodes with their config keys.
