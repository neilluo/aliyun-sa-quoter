"""
Unified error handling for aliyun-quoter.

Provides a hierarchy of exception classes and friendly error message mapping
from BSS API error codes.
"""

import json
from pathlib import Path


class QuoterError(Exception):
    """Base exception for all quoter errors."""
    pass


class CredentialError(QuoterError):
    """Raised when AK/SK credentials are missing or invalid."""
    pass


class ProductNotFoundError(QuoterError):
    """Raised when the requested product code is not registered."""
    pass


class ValidationError(QuoterError):
    """Raised when parameter validation fails."""

    def __init__(self, errors):
        self.errors = errors if isinstance(errors, list) else [errors]
        msg = "; ".join(self.errors)
        super().__init__(msg)


class BssApiError(QuoterError):
    """Raised when BSS API returns an error.

    Attributes:
        code: Original API error code
        raw_message: Original error message from API
        friendly_message: User-friendly Chinese message
        suggestion: Actionable suggestion for the user
    """

    def __init__(self, message, code=None, raw_message=None,
                 friendly_message=None, suggestion=None):
        self.code = code
        self.raw_message = raw_message
        self.friendly_message = friendly_message
        self.suggestion = suggestion
        super().__init__(message)


class NetworkError(QuoterError):
    """Raised on network connectivity issues."""
    pass


# --- Error code mapping ---

_ERROR_CODES_FILE = Path(__file__).parent.parent / "meta" / "error_codes.json"
_ERROR_CODES = {}


def _load_error_codes():
    """Load error code mapping from JSON file (cached)."""
    global _ERROR_CODES
    if _ERROR_CODES:
        return _ERROR_CODES
    if _ERROR_CODES_FILE.exists():
        try:
            with open(_ERROR_CODES_FILE, "r", encoding="utf-8") as f:
                _ERROR_CODES = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return _ERROR_CODES


def get_friendly_error(api_code, default_message=""):
    """Look up a friendly error message for an API error code.

    Args:
        api_code: The error code from BSS API response
        default_message: Fallback message if code not found

    Returns:
        Tuple of (friendly_message, suggestion). Both may be empty strings.
    """
    codes = _load_error_codes()
    entry = codes.get(api_code, {})
    friendly = entry.get("message", default_message)
    suggestion = entry.get("suggestion", "")
    return friendly, suggestion


def format_error(error):
    """Format a QuoterError into a user-friendly string.

    Args:
        error: A QuoterError instance

    Returns:
        Formatted error string with message and optional suggestion.
    """
    if isinstance(error, ValidationError):
        lines = ["参数验证失败:"]
        for e in error.errors:
            lines.append(f"  - {e}")
        return "\n".join(lines)

    if isinstance(error, BssApiError):
        msg = error.friendly_message or str(error)
        lines = [f"错误: {msg}"]
        if error.code:
            lines.append(f"  错误码: {error.code}")
        if error.suggestion:
            lines.append(f"  建议: {error.suggestion}")
        return "\n".join(lines)

    if isinstance(error, ProductNotFoundError):
        return f"错误: {error}"

    if isinstance(error, CredentialError):
        return str(error)

    return f"错误: {error}"
