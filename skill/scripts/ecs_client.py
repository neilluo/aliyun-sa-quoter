"""
Alibaba Cloud ECS DescribePrice API client - zero-dependency implementation.

Uses only Python standard library to call ECS pricing APIs via Alibaba Cloud RPC signing.
"""

import base64
import hashlib
import hmac
import json
import uuid
from datetime import datetime, timezone
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

import bss_client


# ECS API constants
_ENDPOINT = "https://ecs.aliyuncs.com"
_API_VERSION = "2014-05-26"


class EcsApiError(Exception):
    """Raised when ECS API returns an error."""
    pass


def _percent_encode(s):
    """RFC 3986 percent-encoding."""
    return quote(str(s), safe="~")


def _build_signature(params, ak_secret, http_method="GET"):
    """Build Alibaba Cloud RPC API signature (HMAC-SHA1, SignatureVersion 1.0)."""
    # 1. Sort parameters by key name
    sorted_params = sorted(params.items(), key=lambda x: x[0])

    # 2. Build canonicalized query string with percent-encoding
    canonicalized = "&".join(
        f"{_percent_encode(k)}={_percent_encode(v)}"
        for k, v in sorted_params
    )

    # 3. Build string to sign
    string_to_sign = (
        f"{http_method}"
        f"&{_percent_encode('/')}"
        f"&{_percent_encode(canonicalized)}"
    )

    # 4. HMAC-SHA1 with key = AccessKeySecret + "&"
    signing_key = (ak_secret + "&").encode("utf-8")
    digest = hmac.new(signing_key, string_to_sign.encode("utf-8"), hashlib.sha1).digest()

    return base64.b64encode(digest).decode("utf-8")


def _build_common_params(action, ak):
    """Build common parameters for every API request."""
    return {
        "Action": action,
        "Version": _API_VERSION,
        "Format": "JSON",
        "AccessKeyId": ak,
        "SignatureMethod": "HMAC-SHA1",
        "SignatureVersion": "1.0",
        "SignatureNonce": str(uuid.uuid4()),
        "Timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def _call_api(action, params, ak, sk, max_retries=3):
    """Make a signed API call to ECS API."""
    import time
    import sys

    for attempt in range(max_retries):
        # Merge common params with action-specific params
        all_params = _build_common_params(action, ak)
        all_params.update(params)

        # Compute signature
        signature = _build_signature(all_params, sk)
        all_params["Signature"] = signature

        # Build URL
        query_string = urlencode(all_params, quote_via=quote)
        url = f"{_ENDPOINT}/?{query_string}"

        try:
            req = Request(url, method="GET")
            req.add_header("Accept", "application/json")
            req.add_header("User-Agent", "aliyun-quoter/1.0")

            with urlopen(req, timeout=30) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                return body

        except HTTPError as e:
            error_body = ""
            try:
                error_body = e.read().decode("utf-8")
            except Exception:
                pass

            # Retry on throttling (HTTP 429 or throttling error in body)
            if e.code == 429 or "Throttling" in error_body:
                if attempt < max_retries - 1:
                    wait = 2 ** attempt
                    print(f"API 限流，{wait} 秒后重试...", file=sys.stderr)
                    time.sleep(wait)
                    continue

            raise EcsApiError(f"{action} 失败: HTTP {e.code} - {error_body[:500]}")

        except URLError as e:
            raise EcsApiError(f"{action} 网络错误: {e.reason}")

    return None


def _format_platform(platform):
    """Format platform for ECS API (linux/windows)."""
    p = platform.lower()
    if p in ("linux", "centos", "ubuntu", "debian", "alibaba"):
        return "linux"
    elif p in ("windows", "win"):
        return "windows"
    return "linux"


def _parse_price_response(body):
    """Parse ECS DescribePrice response into standard format."""
    if "Code" in body and body.get("Code") != "200" and body.get("Code") != "Success":
        code = body.get("Code", "?")
        msg = body.get("Message", "unknown")
        raise EcsApiError(f"DescribePrice 失败: {msg} (code: {code})")

    price_info = body.get("PriceInfo", {})
    price = price_info.get("Price", {})

    result = {
        "original_price": float(price.get("OriginalPrice", 0)),
        "discount_price": float(price.get("DiscountPrice", 0)),
        "trade_price": float(price.get("TradePrice", 0)),
        "currency": price_info.get("Currency", "CNY"),
        "details": {},
    }

    # Parse DetailInfos to get component prices
    detail_infos = price.get("DetailInfos", {}).get("DetailInfo", [])
    for detail in detail_infos:
        resource = detail.get("Resource", "")
        original_price = float(detail.get("OriginalPrice", 0))
        if resource:
            # Map resource names to module codes
            if resource == "instanceType":
                result["details"]["instanceType"] = original_price
            elif resource == "systemDisk":
                result["details"]["SystemDisk"] = original_price
            elif resource == "dataDisk":
                result["details"]["DataDisk"] = original_price
            elif resource == "bandwidth":
                result["details"]["InternetMaxBandwidthOut"] = original_price

    return result


def get_instance_price(region, instance_type, platform="linux",
                        system_disk_category=None,
                        system_disk_size=40, period=1, price_unit="Month",
                        data_disk_category=None, data_disk_size=0,
                        internet_max_bandwidth_out=0):
    """
    Query ECS instance price via ECS DescribePrice API.

    Args:
        region: Region ID, e.g., "cn-hangzhou"
        instance_type: Instance type, e.g., "ecs.g7.xlarge"
        platform: Operating system ("linux" or "windows")
        system_disk_category: System disk category ("cloud_essd", "cloud_ssd", "cloud_efficiency"), None to use default
        system_disk_size: System disk size in GB
        period: Subscription period
        price_unit: Price unit ("Month", "Year", "Week")
        data_disk_category: Data disk category (optional)
        data_disk_size: Data disk size in GB (optional)
        internet_max_bandwidth_out: Internet max bandwidth out in Mbps (optional)

    Returns:
        dict with keys: original_price, discount_price, trade_price, currency, details
    """
    ak, sk = bss_client.check_credentials()

    params = {
        "RegionId": region,
        "InstanceType": instance_type,
        "Platform": _format_platform(platform),
        "Period": str(period),
        "PriceUnit": price_unit,
    }

    # Add system disk params if provided, otherwise let API use default
    # Note: ECS API uses dot notation: SystemDisk.Category, SystemDisk.Size
    if system_disk_category:
        params["SystemDisk.Category"] = system_disk_category
    if system_disk_size:
        params["SystemDisk.Size"] = str(system_disk_size)

    # Add optional parameters
    # Note: ECS API uses dot notation: DataDisk.1.Category, DataDisk.1.Size
    if data_disk_category and data_disk_size and int(data_disk_size) > 0:
        params["DataDisk.1.Category"] = data_disk_category
        params["DataDisk.1.Size"] = str(data_disk_size)

    if internet_max_bandwidth_out and int(internet_max_bandwidth_out) > 0:
        params["InternetMaxBandwidthOut"] = str(internet_max_bandwidth_out)

    body = _call_api("DescribePrice", params, ak, sk)
    return _parse_price_response(body)
