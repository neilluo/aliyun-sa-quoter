"""
Alibaba Cloud Redis/Tair DescribePrice API client - zero-dependency implementation.

Uses only Python standard library to call Redis pricing APIs via Alibaba Cloud RPC signing.
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


# Redis API constants
_ENDPOINT = "https://r-kvstore.aliyuncs.com"
_API_VERSION = "2015-01-01"


class RedisApiError(Exception):
    """Raised when Redis API returns an error."""
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
    """Make a signed API call to Redis API."""
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

            raise RedisApiError(f"{action} 失败: HTTP {e.code} - {error_body[:500]}")

        except URLError as e:
            raise RedisApiError(f"{action} 网络错误: {e.reason}")

    return None


def _parse_price_response(body):
    """Parse Redis DescribePrice response into standard format."""
    if "Code" in body and body.get("Code") != "200" and body.get("Code") != "Success":
        code = body.get("Code", "?")
        msg = body.get("Message", "unknown")
        raise RedisApiError(f"DescribePrice 失败: {msg} (code: {code})")

    # Redis API returns price in "Order" object, not "PriceInfo"
    order = body.get("Order", {})
    
    result = {
        "original_price": float(order.get("OriginalAmount", 0)),
        "discount_price": float(order.get("DiscountAmount", 0)),
        "trade_price": float(order.get("TradeAmount", 0)),
        "currency": order.get("Currency", "CNY"),
        "details": {},
    }

    # Parse SubOrders to get component prices
    sub_orders = body.get("SubOrders", {}).get("SubOrder", [])
    for sub_order in sub_orders:
        module_instances = sub_order.get("ModuleInstance", {}).get("ModuleInstance", [])
        for module in module_instances:
            module_code = module.get("ModuleCode", "")
            original_price = float(module.get("StandPrice", 0))
            if original_price > 0:
                result["details"][module_code] = original_price

    return result


def get_redis_price(
    region: str,
    instance_class: str,
    architecture: str = "standard",
    capacity: int = 1024,
    pay_type: str = "Prepaid",
    period: int = 1,
    time_type: str = "Month"
):
    """
    Query Redis/Tair instance price via DescribePrice API.

    Args:
        region: Region ID, e.g., "cn-hangzhou"
        instance_class: Instance class, e.g., "redis.master.small.default"
        architecture: Architecture type ("standard" or "cluster")
        capacity: Capacity in MB
        pay_type: Payment type ("Prepaid" or "Postpaid")
        period: Subscription period
        time_type: Time type ("Month", "Year")

    Returns:
        dict with keys: original_price, discount_price, trade_price, currency, details
    """
    ak, sk = bss_client.check_credentials()

    params = {
        "RegionId": region,
        "InstanceClass": instance_class,
        "Capacity": str(capacity),
        "PayType": pay_type,
        "OrderType": "BUY",  # BUY, UPGRADE, RENEW
        "Quantity": "1",
    }
    
    if pay_type == "Prepaid":
        params["TimeType"] = time_type
        params["Period"] = str(period)

    body = _call_api("DescribePrice", params, ak, sk)
    return _parse_price_response(body)
