"""
Alibaba Cloud RDS DescribePrice API client - zero-dependency implementation.

Uses only Python standard library to call RDS pricing APIs via Alibaba Cloud RPC signing.
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


# RDS API constants
_ENDPOINT = "https://rds.aliyuncs.com"
_API_VERSION = "2014-08-15"


class RdsApiError(Exception):
    """Raised when RDS API returns an error."""
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
    """Make a signed API call to RDS API."""
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

            raise RdsApiError(f"{action} 失败: HTTP {e.code} - {error_body[:500]}")

        except URLError as e:
            raise RdsApiError(f"{action} 网络错误: {e.reason}")

    return None


def _parse_price_response(body):
    """Parse RDS DescribePrice response into standard format."""
    if "Code" in body and body.get("Code") != "200" and body.get("Code") != "Success":
        code = body.get("Code", "?")
        msg = body.get("Message", "unknown")
        raise RdsApiError(f"DescribePrice 失败: {msg} (code: {code})")

    price_info = body.get("PriceInfo", {})
    
    # RDS API returns price directly in PriceInfo, not nested in Price
    result = {
        "original_price": float(price_info.get("OriginalPrice", 0)),
        "discount_price": float(price_info.get("DiscountPrice", 0)),
        "trade_price": float(price_info.get("TradePrice", 0)),
        "currency": price_info.get("Currency", "CNY"),
        "details": {},
    }

    # Parse OrderLines to get component prices
    order_lines = price_info.get("OrderLines", {})
    if isinstance(order_lines, dict):
        # OrderLines is a dict with numeric keys like "0", "1", etc.
        for key, line in order_lines.items():
            if isinstance(line, dict):
                # Extract price components from order line
                commodity_code = line.get("commodityCode", "")
                price = float(line.get("price", 0))
                if price > 0:
                    result["details"][commodity_code] = price

    return result


def get_rds_price(
    region: str,
    engine: str,
    engine_version: str,
    instance_class: str,
    storage_size: int = 100,
    pay_type: str = "Prepaid",
    period: int = 1,
    time_type: str = "Month"
):
    """
    Query RDS instance price via DescribePrice API.

    Args:
        region: Region ID, e.g., "cn-hangzhou"
        engine: Database engine, e.g., "mysql", "postgresql", "sqlserver"
        engine_version: Engine version, e.g., "8.0", "14.0"
        instance_class: Instance class, e.g., "mysql.x2.large.2"
        storage_size: Storage size in GB
        pay_type: Payment type ("Prepaid" or "Postpaid")
        period: Subscription period
        time_type: Time type ("Month", "Year")

    Returns:
        dict with keys: original_price, discount_price, trade_price, currency, details
    """
    ak, sk = bss_client.check_credentials()

    params = {
        "RegionId": region,
        "Engine": engine,
        "EngineVersion": engine_version,
        "DBInstanceClass": instance_class,
        "DBInstanceStorage": str(storage_size),
        "PayType": pay_type,
        "Quantity": "1",
    }
    
    if pay_type == "Prepaid":
        params["TimeType"] = time_type
        params["UsedTime"] = str(period)

    body = _call_api("DescribePrice", params, ak, sk)
    return _parse_price_response(body)
