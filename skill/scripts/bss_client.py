"""
Alibaba Cloud BSS OpenAPI client - zero-dependency implementation.

Uses only Python standard library (urllib, hmac, hashlib, json, uuid, datetime)
to call BSS pricing APIs via Alibaba Cloud RPC signing (HMAC-SHA1, SignatureVersion 1.0).

Provides unified access to BSS pricing APIs:
- QueryProductList
- DescribePricingModule
- GetSubscriptionPrice / GetPayAsYouGoPrice
"""

import base64
import hashlib
import hmac
import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from errors import get_friendly_error


# BSS OpenAPI constants
_ENDPOINT = "https://business.aliyuncs.com"
_API_VERSION = "2017-12-14"


class CredentialError(Exception):
    """Raised when AK/SK credentials are missing or invalid."""
    pass


class BssApiError(Exception):
    """Raised when BSS API returns an error."""
    pass


def check_credentials():
    """Check if AK/SK environment variables are set. Returns (ak, sk) or raises CredentialError."""
    ak = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_ID", "").strip()
    sk = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_SECRET", "").strip()

    if not ak or not sk:
        missing = []
        if not ak:
            missing.append("ALIBABA_CLOUD_ACCESS_KEY_ID")
        if not sk:
            missing.append("ALIBABA_CLOUD_ACCESS_KEY_SECRET")

        raise CredentialError(
            f"未检测到阿里云 AK/SK 凭证。缺少环境变量: {', '.join(missing)}\n"
            "\n"
            "请设置以下环境变量:\n"
            "  export ALIBABA_CLOUD_ACCESS_KEY_ID=your_access_key_id\n"
            "  export ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_access_key_secret\n"
            "\n"
            "获取方式: 登录阿里云控制台 -> AccessKey 管理\n"
            "  https://ram.console.aliyun.com/manage/ak"
        )

    return ak, sk


def _percent_encode(s):
    """RFC 3986 percent-encoding.

    Encodes all characters except unreserved characters: A-Z a-z 0-9 - _ . ~
    Space -> %20 (not +), * -> %2A.
    """
    return quote(str(s), safe="~")


def _build_signature(params, ak_secret, http_method="GET"):
    """Build Alibaba Cloud RPC API signature (HMAC-SHA1, SignatureVersion 1.0).

    Args:
        params: dict of all request parameters (excluding Signature)
        ak_secret: AccessKeySecret
        http_method: HTTP method (GET or POST)

    Returns:
        Base64-encoded HMAC-SHA1 signature string.
    """
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
    """Make a signed API call to BSS OpenAPI.

    Args:
        action: API action name (e.g. "QueryProductList")
        params: dict of action-specific parameters
        ak: AccessKeyId
        sk: AccessKeySecret
        max_retries: number of retries on throttling

    Returns:
        Parsed JSON response body as dict.

    Raises:
        BssApiError: on API-level errors
    """
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

            # Try to parse error response for a better message
            try:
                err_json = json.loads(error_body)
                msg = err_json.get("Message", error_body)
                code = err_json.get("Code", str(e.code))
                friendly, suggestion = get_friendly_error(code, msg)
                error_text = f"{action} 失败: {friendly}"
                if suggestion:
                    error_text += f"\n  建议: {suggestion}"
                raise BssApiError(error_text)
            except (json.JSONDecodeError, BssApiError):
                if isinstance(sys.exc_info()[1], BssApiError):
                    raise
                raise BssApiError(f"{action} 失败: HTTP {e.code} - {error_body[:500]}")

        except URLError as e:
            raise BssApiError(f"{action} 网络错误: {e.reason}")

    return None


def create_client():
    """Create a lightweight client (ak, sk tuple). Compatible interface for quoter.py."""
    ak, sk = check_credentials()
    return (ak, sk)


def query_product_list(client, page_num=1, page_size=50):
    """Query available product list from BSS API.

    Args:
        client: (ak, sk) tuple
        page_num: Page number for pagination (default: 1)
        page_size: Number of products per page (default: 50)

    Returns list of dicts with keys: product_code, product_name, product_type.
    """
    ak, sk = client

    params = {
        "PageNum": str(page_num),
        "PageSize": str(page_size),
    }

    try:
        body = _call_api("QueryProductList", params, ak, sk)
    except BssApiError:
        raise
    except Exception as e:
        raise BssApiError(f"查询产品列表失败: {e}")

    if not body.get("Success"):
        raise BssApiError(
            f"查询产品列表失败: {body.get('Message', 'unknown')} (code: {body.get('Code', '?')})"
        )

    products = []
    product_list = body.get("Data", {}).get("ProductList", {}).get("Product", [])
    for p in product_list:
        products.append({
            "product_code": p.get("ProductCode", ""),
            "product_name": p.get("ProductName", ""),
            "product_type": p.get("ProductType", ""),
        })

    return products


def describe_pricing_modules(client, product_code, subscription_type="Subscription"):
    """Describe pricing modules for a product.

    Args:
        client: (ak, sk) tuple
        product_code: e.g. "ecs", "rds", "slb"
        subscription_type: "Subscription" or "PayAsYouGo"

    Returns list of dicts with keys: module_code, module_name, config_list.
    """
    ak, sk = client

    params = {
        "ProductCode": product_code,
        "SubscriptionType": subscription_type,
    }

    try:
        body = _call_api("DescribePricingModule", params, ak, sk)
    except BssApiError:
        raise
    except Exception as e:
        raise BssApiError(f"查询计价模块失败 ({product_code}): {e}")

    if not body.get("Success"):
        raise BssApiError(
            f"查询计价模块失败: {body.get('Message', 'unknown')} (code: {body.get('Code', '?')})"
        )

    modules = []
    module_list = body.get("Data", {}).get("ModuleList", {}).get("Module", [])
    for m in module_list:
        config_list = []
        raw_configs = m.get("ConfigList", {}).get("ConfigList", [])
        if isinstance(raw_configs, list):
            config_list = raw_configs
        modules.append({
            "module_code": m.get("ModuleCode", ""),
            "module_name": m.get("ModuleName", ""),
            "config_list": config_list,
        })

    return modules


def _flatten_module_list(module_list, prefix="ModuleList"):
    """Flatten module list into indexed parameters for RPC API.

    Input: [{"module_code": "X", "config": "Y", "price_type": "Z"}, ...]
    Output: {"ModuleList.1.ModuleCode": "X", "ModuleList.1.Config": "Y", "ModuleList.1.PriceType": "Z", ...}
    """
    params = {}
    for i, m in enumerate(module_list, start=1):
        params[f"{prefix}.{i}.ModuleCode"] = m["module_code"]
        params[f"{prefix}.{i}.Config"] = m["config"]
        params[f"{prefix}.{i}.PriceType"] = m.get("price_type", "Hour")
    return params


def _parse_price_response(body, action_label):
    """Parse price response body into standard result dict.

    Returns dict with keys: original_amount, discount_amount, trade_amount, currency, module_details.
    """
    if not body.get("Success"):
        api_code = body.get("Code", "?")
        raw_msg = body.get("Message", "unknown")
        friendly, suggestion = get_friendly_error(api_code, raw_msg)
        error_text = f"{action_label}: {friendly}"
        if suggestion:
            error_text += f"\n  建议: {suggestion}"
        raise BssApiError(error_text)

    data = body.get("Data", {})
    result = {
        "original_amount": data.get("OriginalAmount"),
        "discount_amount": data.get("DiscountAmount"),
        "trade_amount": data.get("TradeAmount"),
        "currency": data.get("Currency", "CNY"),
        "module_details": [],
    }

    module_details = data.get("ModuleDetails", {}).get("ModuleDetail", [])
    for md in module_details:
        result["module_details"].append({
            "module_code": md.get("ModuleCode", ""),
            "original_cost": md.get("OriginalCost"),
            "discount_cost": md.get("DiscountCost"),
            "invest_total_cost": md.get("InvestTotalCost"),
            "cost_after_discount": md.get("CostAfterDiscount"),
        })

    return result


def get_subscription_price(client, product_code, module_list, region, duration=1,
                           quantity=1, product_type=None):
    """Get subscription (prepaid) price.

    Args:
        client: (ak, sk) tuple
        product_code: e.g. "ecs"
        module_list: list of dicts with keys: module_code, config, price_type
        region: region id, e.g. "cn-hangzhou"
        duration: months (1-12 or 12/24/36)
        quantity: number of instances
        product_type: optional product type override

    Returns dict with keys: original_amount, discount_amount, trade_amount, currency, module_details.
    """
    ak, sk = client

    params = {
        "ProductCode": product_code,
        "OrderType": "NewOrder",
        "SubscriptionType": "Subscription",
        "Region": region,
        "ServicePeriodQuantity": str(duration),
        "ServicePeriodUnit": "Month",
        "Quantity": str(quantity),
    }

    if product_type:
        params["ProductType"] = product_type

    # Flatten module list into indexed params
    params.update(_flatten_module_list(module_list))

    try:
        body = _call_api("GetSubscriptionPrice", params, ak, sk)
    except BssApiError:
        raise
    except Exception as e:
        raise BssApiError(f"包年包月询价失败 ({product_code}): {e}")

    return _parse_price_response(body, f"包年包月询价失败 ({product_code})")


def get_pay_as_you_go_price(client, product_code, module_list, region,
                            product_type=None):
    """Get pay-as-you-go (postpaid) price.

    Args:
        client: (ak, sk) tuple
        product_code: e.g. "ecs"
        module_list: list of dicts with keys: module_code, config, price_type
        region: region id, e.g. "cn-hangzhou"
        product_type: optional product type override

    Returns dict with keys: original_amount, discount_amount, trade_amount, currency, module_details.
    """
    ak, sk = client

    params = {
        "ProductCode": product_code,
        "OrderType": "NewOrder",
        "SubscriptionType": "PayAsYouGo",
        "Region": region,
    }

    if product_type:
        params["ProductType"] = product_type

    # Flatten module list into indexed params
    params.update(_flatten_module_list(module_list))

    try:
        body = _call_api("GetPayAsYouGoPrice", params, ak, sk)
    except BssApiError:
        raise
    except Exception as e:
        raise BssApiError(f"按量付费询价失败 ({product_code}): {e}")

    return _parse_price_response(body, f"按量付费询价失败 ({product_code})")
