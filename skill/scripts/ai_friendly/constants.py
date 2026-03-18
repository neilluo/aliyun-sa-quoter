"""所有常量定义 - AI 直接引用，不要硬编码。

该模块包含产品中使用的所有魔法字符串常量，
消灭硬编码字符串，提高代码可读性和可维护性。

【使用示例】
    from ai_friendly.constants import Region, Category, DiskType

    # 使用地域常量
    region = Region.HANGZHOU  # "cn-hangzhou"

    # 使用分类常量
    category = Category.COMPUTE  # "compute"

    # 使用所有地域列表
    all_regions = Region.ALL
"""

from typing import List


class Region:
    """阿里云地域常量。

    【使用示例】
        Region.HANGZHOU  # "cn-hangzhou"
        Region.ALL  # 所有地域列表
    """

    # 华北地域
    QINGDAO = "cn-qingdao"
    BEIJING = "cn-beijing"
    ZHANGJIAKOU = "cn-zhangjiakou"
    HUHEHAOTE = "cn-huhehaote"
    WULANCHABU = "cn-wulanchabu"

    # 华东地域
    HANGZHOU = "cn-hangzhou"
    SHANGHAI = "cn-shanghai"
    NANJING = "cn-nanjing"
    FUZHOU = "cn-fuzhou"

    # 华南地域
    SHENZHEN = "cn-shenzhen"
    HEYUAN = "cn-heyuan"
    GUANGZHOU = "cn-guangzhou"

    # 西南地域
    CHENGDU = "cn-chengdu"

    # 中国地域
    HONGKONG = "cn-hongkong"

    # 海外地域
    SINGAPORE = "ap-southeast-1"
    SYDNEY = "ap-southeast-2"
    KUALA_LUMPUR = "ap-southeast-3"
    JAKARTA = "ap-southeast-5"
    MANILA = "ap-southeast-6"
    BANGKOK = "ap-southeast-7"
    TOKYO = "ap-northeast-1"
    SEOUL = "ap-northeast-2"
    MUMBAI = "ap-south-1"
    SILICON_VALLEY = "us-west-1"
    VIRGINIA = "us-east-1"
    FRANKFURT = "eu-central-1"
    LONDON = "eu-west-1"
    DUBAI = "me-east-1"
    RIYADH = "me-central-1"

    # 常用地域列表
    MAINLAND: List[str] = [
        BEIJING, SHANGHAI, HANGZHOU, SHENZHEN,
        QINGDAO, ZHANGJIAKOU, HUHEHAOTE, WULANCHABU,
        NANJING, FUZHOU, HEYUAN, GUANGZHOU, CHENGDU,
    ]

    OVERSEAS: List[str] = [
        HONGKONG, SINGAPORE, SYDNEY, KUALA_LUMPUR,
        JAKARTA, MANILA, BANGKOK, TOKYO, SEOUL,
        MUMBAI, SILICON_VALLEY, VIRGINIA, FRANKFURT,
        LONDON, DUBAI, RIYADH,
    ]

    ALL: List[str] = MAINLAND + OVERSEAS


class Category:
    """产品分类常量。

    【使用示例】
        Category.COMPUTE  # "compute"
        Category.ALL  # 所有分类列表
    """

    COMPUTE = "compute"
    DATABASE = "database"
    NETWORK = "network"
    STORAGE = "storage"
    CDN_SECURITY = "cdn_security"
    MIDDLEWARE = "middleware"
    AI = "ai"

    ALL: List[str] = [
        COMPUTE,
        DATABASE,
        NETWORK,
        STORAGE,
        CDN_SECURITY,
        MIDDLEWARE,
        AI,
    ]

    # 中文名称映射
    DISPLAY_NAMES = {
        COMPUTE: "计算",
        DATABASE: "数据库",
        NETWORK: "网络",
        STORAGE: "存储",
        CDN_SECURITY: "CDN与安全",
        MIDDLEWARE: "中间件",
        AI: "人工智能",
    }


class BillingType:
    """计费类型常量。

    【使用示例】
        BillingType.SUBSCRIPTION  # "Subscription"
        BillingType.PAY_AS_YOU_GO  # "PayAsYouGo"
    """

    SUBSCRIPTION = "Subscription"
    PAY_AS_YOU_GO = "PayAsYouGo"

    ALL: List[str] = [SUBSCRIPTION, PAY_AS_YOU_GO]

    # 中文名称映射
    DISPLAY_NAMES = {
        SUBSCRIPTION: "包年包月",
        PAY_AS_YOU_GO: "按量付费",
    }


class DiskType:
    """磁盘类型常量（ECS/RDS 等）。

    【使用示例】
        DiskType.ESSD  # "cloud_essd"
        DiskType.ALL  # 所有磁盘类型列表
    """

    # 云盘类型
    EFFICIENCY = "cloud_efficiency"  # 高效云盘
    SSD = "cloud_ssd"  # SSD 云盘
    ESSD = "cloud_essd"  # ESSD 云盘

    # ESSD 性能级别
    ESSD_PL0 = "cloud_essd_pl0"
    ESSD_PL1 = "cloud_essd_pl1"
    ESSD_PL2 = "cloud_essd_pl2"
    ESSD_PL3 = "cloud_essd_pl3"

    # RDS 专用
    LOCAL_SSD = "local_ssd"

    ALL: List[str] = [
        EFFICIENCY,
        SSD,
        ESSD,
        ESSD_PL0,
        ESSD_PL1,
        ESSD_PL2,
        ESSD_PL3,
        LOCAL_SSD,
    ]

    # ECS 支持的类型
    ECS_TYPES: List[str] = [EFFICIENCY, SSD, ESSD, ESSD_PL0, ESSD_PL1]

    # RDS 支持的类型
    RDS_TYPES: List[str] = [LOCAL_SSD, SSD, ESSD]


class ProductType:
    """ProductType 常量（需要 ProductType 的产品）。

    【使用示例】
        ProductType.KAFKA_PRE  # "alikafka_pre"
        ProductType.WAF_V2  # "waf_v2_public_cn"
    """

    # Kafka
    KAFKA_PRE = "alikafka_pre"
    KAFKA_POST = "alikafka_post"

    # Elasticsearch
    ES_PRE = "elasticsearch_pre"
    ES_POST = "elasticsearch_post"

    # WAF
    WAF_V2 = "waf_v2_public_cn"
    WAF_V3_PREPAID = "waf_v3prepaid_public_cn"

    # RocketMQ
    ROCKETMQ_SUB = "mq_sub"
    ROCKETMQ_POST = "mq_post"

    # RDS 系列
    RDS_STANDARD = "rds"
    RDS_BASIC = "bards"
    RDS_READONLY = "rords"

    ALL: List[str] = [
        KAFKA_PRE,
        KAFKA_POST,
        ES_PRE,
        ES_POST,
        WAF_V2,
        WAF_V3_PREPAID,
        ROCKETMQ_SUB,
        ROCKETMQ_POST,
        RDS_STANDARD,
        RDS_BASIC,
        RDS_READONLY,
    ]


class PriceType:
    """价格类型常量（BSS API）。

    【使用示例】
        PriceType.HOUR  # "Hour"
        PriceType.MONTH  # "Month"
    """

    HOUR = "Hour"
    MONTH = "Month"
    YEAR = "Year"

    ALL: List[str] = [HOUR, MONTH, YEAR]


class ImageOS:
    """操作系统类型常量（ECS）。

    【使用示例】
        ImageOS.LINUX  # "linux"
        ImageOS.WINDOWS  # "windows"
    """

    LINUX = "linux"
    WINDOWS = "windows"

    ALL: List[str] = [LINUX, WINDOWS]


class Engine:
    """数据库引擎常量（RDS）。

    【使用示例】
        Engine.MYSQL  # "mysql"
        Engine.POSTGRESQL  # "postgresql"
    """

    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    MSSQL = "mssql"
    MARIADB = "mariadb"

    ALL: List[str] = [MYSQL, POSTGRESQL, MSSQL, MARIADB]


class NetworkType:
    """网络类型常量。

    【使用示例】
        NetworkType.VPC  # 1
        NetworkType.CLASSIC  # 0
    """

    VPC = 1
    CLASSIC = 0

    ALL: List[int] = [VPC, CLASSIC]


class Architecture:
    """架构类型常量（Redis 等）。

    【使用示例】
        Architecture.STANDARD  # "standard"
        Architecture.CLUSTER  # "cluster"
    """

    STANDARD = "standard"
    CLUSTER = "cluster"
    RWSPLIT = "rwsplit"

    ALL: List[str] = [STANDARD, CLUSTER, RWSPLIT]


class Edition:
    """版本类型常量（Redis 等）。

    【使用示例】
        Edition.COMMUNITY  # "community"
        Edition.ENTERPRISE  # "enterprise"
    """

    COMMUNITY = "community"
    ENTERPRISE = "enterprise"

    ALL: List[str] = [COMMUNITY, ENTERPRISE]
