"""
Build BSS ModuleList parameters for each product.

Each function takes CLI arguments and returns a list of module dicts
compatible with bss_client.get_subscription_price / get_pay_as_you_go_price.

Module dict format: {"module_code": str, "config": str, "price_type": str}
"""


def _extract_instance_family(instance_type):
    """Extract instance family from instance type, e.g. 'ecs.g7.xlarge' -> 'ecs.g7'."""
    parts = instance_type.split(".")
    if len(parts) >= 2:
        return ".".join(parts[:2])
    return instance_type


def build_ecs_modules(instance_type, image_os="linux",
                      system_disk_category="cloud_essd", system_disk_size=40,
                      data_disk_category=None, data_disk_size=0,
                      internet_bandwidth=0):
    """Build ECS pricing module list.

    Args:
        instance_type: e.g. "ecs.g7.xlarge"
        image_os: "linux" or "windows"
        system_disk_category: "cloud_essd", "cloud_ssd", "cloud_efficiency"
        system_disk_size: GB (20-500)
        data_disk_category: optional, same values as system disk
        data_disk_size: GB, 0 means no data disk
        internet_bandwidth: Mbps, 0 means no public bandwidth

    Returns list of module dicts.
    """
    family = _extract_instance_family(instance_type)

    modules = [
        {
            "module_code": "InstanceType",
            "config": (
                f"InstanceType:{instance_type},"
                f"IoOptimized:IoOptimized,"
                f"ImageOs:{image_os},"
                f"InstanceTypeFamily:{family}"
            ),
            "price_type": "Hour",
        },
        {
            "module_code": "SystemDisk",
            "config": (
                f"SystemDisk.Category:{system_disk_category},"
                f"SystemDisk.Size:{system_disk_size}"
            ),
            "price_type": "Hour",
        },
    ]

    if data_disk_size > 0:
        category = data_disk_category or system_disk_category
        modules.append({
            "module_code": "DataDisk",
            "config": (
                f"DataDisk.Category:{category},"
                f"DataDisk.Size:{data_disk_size}"
            ),
            "price_type": "Hour",
        })

    if internet_bandwidth > 0:
        modules.append({
            "module_code": "InternetMaxBandwidthOut",
            "config": (
                f"InternetMaxBandwidthOut:{internet_bandwidth},"
                f"InternetMaxBandwidthOut.IsFlowType:5,"
                f"NetworkType:1"
            ),
            "price_type": "Hour",
        })

    return modules


def build_rds_modules(engine="mysql", engine_version="8.0",
                      series="HighAvailability", instance_class="mysql.n2.medium.2c",
                      storage_type="local_ssd", storage_size=100,
                      network_type=1):
    """Build RDS pricing module list.

    Args:
        engine: "mysql", "postgresql", "mssql", "MariaDB"
        engine_version: e.g. "8.0", "5.7"
        series: "Basic", "HighAvailability", "AlwaysOn"
        instance_class: e.g. "mysql.n2.medium.2c"
        storage_type: "local_ssd", "cloud_essd", "cloud_ssd"
        storage_size: GB (must be multiple of 5)
        network_type: 0=classic, 1=VPC

    Returns list of module dicts.
    """
    modules = [
        {
            "module_code": "Engine",
            "config": f"Engine:{engine}",
            "price_type": "Hour",
        },
        {
            "module_code": "EngineVersion",
            "config": f"EngineVersion:{engine_version}",
            "price_type": "Hour",
        },
        {
            "module_code": "Series",
            "config": f"Series:{series}",
            "price_type": "Hour",
        },
        {
            "module_code": "DBInstanceStorageType",
            "config": f"DBInstanceStorageType:{storage_type}",
            "price_type": "Hour",
        },
        {
            "module_code": "DBInstanceStorage",
            "config": f"DBInstanceStorage:{storage_size}",
            "price_type": "Hour",
        },
        {
            "module_code": "DBInstanceClass",
            "config": f"DBInstanceClass:{instance_class}",
            "price_type": "Hour",
        },
        {
            "module_code": "DBNetworkType",
            "config": f"DBNetworkType:{network_type}",
            "price_type": "Hour",
        },
    ]

    return modules


def build_slb_modules(spec="slb.s3.large", internet_charge_type=1,
                      bandwidth=0):
    """Build SLB pricing module list.

    Args:
        spec: e.g. "slb.s0.share", "slb.s1.small", "slb.s2.medium", "slb.s3.large"
        internet_charge_type: 1=by traffic, 0=by bandwidth
        bandwidth: Kbps, required when internet_charge_type=0

    Returns list of module dicts.
    """
    modules = [
        {
            "module_code": "LoadBalancerSpec",
            "config": f"LoadBalancerSpec:{spec}",
            "price_type": "Hour",
        },
        {
            "module_code": "InternetTrafficOut",
            "config": f"InternetTrafficOut:{internet_charge_type}",
            "price_type": "Hour",
        },
        {
            "module_code": "InstanceRent",
            "config": "InstanceRent:1",
            "price_type": "Hour",
        },
    ]

    if internet_charge_type == 0 and bandwidth > 0:
        modules.append({
            "module_code": "Bandwidth",
            "config": f"Bandwidth:{bandwidth}",
            "price_type": "Hour",
        })

    return modules


def build_eip_modules(bandwidth=5, internet_charge_type="PayByTraffic"):
    """Build EIP pricing module list.

    Args:
        bandwidth: Mbps
        internet_charge_type: "PayByTraffic" or "PayByBandwidth"

    Returns list of module dicts.
    """
    modules = [
        {
            "module_code": "Bindwidth",
            "config": f"Bindwidth:{bandwidth}",
            "price_type": "Hour",
        },
        {
            "module_code": "InternetChargeType",
            "config": f"InternetChargeType:{internet_charge_type}",
            "price_type": "Hour",
        },
    ]

    return modules


def build_oss_modules(storage_class="Standard", capacity=100):
    """Build OSS pricing module list.

    Note: OSS module codes should be discovered via DescribePricingModule.
    This provides a basic structure; actual config keys may vary.

    Args:
        storage_class: "Standard", "IA" (Infrequent Access), "Archive"
        capacity: storage capacity in GB

    Returns list of module dicts.
    """
    modules = [
        {
            "module_code": "Capacity",
            "config": f"Capacity:{capacity},StorageClass:{storage_class}",
            "price_type": "Hour",
        },
    ]

    return modules


def build_cdn_modules(traffic_package=100):
    """Build CDN pricing module list.

    Note: CDN module codes should be discovered via DescribePricingModule.
    This provides a basic structure; actual config keys may vary.

    Args:
        traffic_package: traffic package size in GB

    Returns list of module dicts.
    """
    modules = [
        {
            "module_code": "TrafficPackage",
            "config": f"TrafficPackage:{traffic_package}",
            "price_type": "Hour",
        },
    ]

    return modules


# Product code to builder mapping
PRODUCT_BUILDERS = {
    "ecs": build_ecs_modules,
    "rds": build_rds_modules,
    "slb": build_slb_modules,
    "eip": build_eip_modules,
    "oss": build_oss_modules,
    "cdn": build_cdn_modules,
}

SUPPORTED_PRODUCTS = list(PRODUCT_BUILDERS.keys())
