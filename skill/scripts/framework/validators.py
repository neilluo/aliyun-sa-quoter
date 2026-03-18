"""
声明式验证框架 - 用于产品参数验证。

提供 ValidationRule 数据类和 Validator 类，支持声明式定义验证规则，
自动格式化中文错误信息。
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Union


@dataclass
class ValidationRule:
    """单个字段的验证规则定义。

    Attributes:
        name: 字段名称
        label: 字段显示名称（中文，用于错误信息）
        required: 是否必填
        choices: 可选值列表（None 表示不限制）
        min_val: 数值最小值（None 表示不限制）
        max_val: 数值最大值（None 表示不限制）
        custom_validator: 自定义验证函数 fn(value, field_name, field_label) -> str|None
        error_formatter: 自定义错误格式化函数 fn(rule, value, error_type) -> str
    """
    name: str
    label: str = ""
    required: bool = False
    choices: Optional[List[Any]] = None
    min_val: Optional[Union[int, float]] = None
    max_val: Optional[Union[int, float]] = None
    custom_validator: Optional[Callable[[Any, str, str], Optional[str]]] = None
    error_formatter: Optional[Callable[[Any, Any, str], str]] = None

    def __post_init__(self):
        if not self.label:
            self.label = self.name

    def format_error(self, value: Any, error_type: str) -> str:
        """格式化错误信息。"""
        if self.error_formatter:
            return self.error_formatter(self, value, error_type)

        formatters = {
            'required': f"缺少必填参数: {self.label} ({self.name})",
            'choices': (
                f"参数 {self.label} ({self.name}) 的值 '{value}' 无效，"
                f"可选值: {', '.join(str(c) for c in (self.choices or []))}"
            ),
            'min_val': (
                f"参数 {self.label} ({self.name}) 的值 {value} 过小，"
                f"最小值为 {self.min_val}"
            ),
            'max_val': (
                f"参数 {self.label} ({self.name}) 的值 {value} 过大，"
                f"最大值为 {self.max_val}"
            ),
            'type': (
                f"参数 {self.label} ({self.name}) 的值 '{value}' 类型不正确"
            ),
            'custom': f"参数 {self.label} ({self.name}) 验证失败",
        }
        return formatters.get(error_type, f"参数 {self.name} 验证失败")


class Validator:
    """批量验证器，支持多个字段的声明式验证。

    Example:
        rules = [
            ValidationRule(name="region", label="地域", required=True),
            ValidationRule(name="cpu", label="CPU核数", required=True, min_val=1, max_val=256),
            ValidationRule(name="disk_type", label="磁盘类型", choices=["cloud_ssd", "cloud_essd"]),
        ]
        validator = Validator(rules)
        errors = validator.validate(params)
    """

    def __init__(self, rules: Optional[List[ValidationRule]] = None):
        self.rules: Dict[str, ValidationRule] = {}
        if rules:
            for rule in rules:
                self.add_rule(rule)

    def add_rule(self, rule: ValidationRule) -> 'Validator':
        """添加验证规则，支持链式调用。"""
        self.rules[rule.name] = rule
        return self

    def remove_rule(self, name: str) -> 'Validator':
        """移除验证规则，支持链式调用。"""
        self.rules.pop(name, None)
        return self

    def validate(self, params: Dict[str, Any]) -> List[str]:
        """验证参数字典，返回错误列表（空列表表示验证通过）。

        Args:
            params: 待验证的参数名值对

        Returns:
            错误信息列表（中文）
        """
        errors = []

        for name, rule in self.rules.items():
            value = params.get(name)
            field_errors = self._validate_field(rule, value)
            errors.extend(field_errors)

        return errors

    def validate_field(self, name: str, value: Any) -> List[str]:
        """验证单个字段。

        Args:
            name: 字段名称
            value: 字段值

        Returns:
            错误信息列表
        """
        rule = self.rules.get(name)
        if not rule:
            return []
        return self._validate_field(rule, value)

    def _validate_field(self, rule: ValidationRule, value: Any) -> List[str]:
        """执行单个字段的所有验证规则。"""
        errors = []

        # 1. 必填验证
        if rule.required and (value is None or value == ""):
            errors.append(rule.format_error(value, 'required'))
            return errors  # 必填为空时，跳过其他验证

        # 值为空且非必填，跳过其他验证
        if value is None or value == "":
            return errors

        # 2. 可选值验证
        if rule.choices is not None and value not in rule.choices:
            errors.append(rule.format_error(value, 'choices'))

        # 3. 数值范围验证
        if rule.min_val is not None:
            try:
                if float(value) < rule.min_val:
                    errors.append(rule.format_error(value, 'min_val'))
            except (ValueError, TypeError):
                errors.append(rule.format_error(value, 'type'))

        if rule.max_val is not None:
            try:
                if float(value) > rule.max_val:
                    errors.append(rule.format_error(value, 'max_val'))
            except (ValueError, TypeError):
                if rule.min_val is None:  # 避免重复添加类型错误
                    errors.append(rule.format_error(value, 'type'))

        # 4. 自定义验证器
        if rule.custom_validator:
            try:
                error = rule.custom_validator(value, rule.name, rule.label)
                if error:
                    if isinstance(error, str):
                        errors.append(error)
                    else:
                        errors.append(rule.format_error(value, 'custom'))
            except Exception as e:
                errors.append(f"参数 {rule.label} ({rule.name}) 自定义验证出错: {str(e)}")

        return errors

    def is_valid(self, params: Dict[str, Any]) -> bool:
        """快速检查参数是否有效。

        Args:
            params: 待验证的参数名值对

        Returns:
            True 表示验证通过，False 表示有错误
        """
        return len(self.validate(params)) == 0


# ==================== 验证器工厂函数 ====================

def create_range_validator(
    min_val: Optional[Union[int, float]] = None,
    max_val: Optional[Union[int, float]] = None,
    error_message: Optional[str] = None
) -> ValidationRule:
    """创建数值范围验证规则。

    Args:
        min_val: 最小值
        max_val: 最大值
        error_message: 自定义错误信息模板，可用 name, label, value, min, max

    Returns:
        ValidationRule 实例
    """
    def formatter(rule, value, error_type):
        if error_message:
            return error_message.format(
                name=rule.name,
                label=rule.label,
                value=value,
                min=rule.min_val,
                max=rule.max_val
            )
        if error_type == 'min_val':
            return f"{rule.label} 不能小于 {rule.min_val}"
        if error_type == 'max_val':
            return f"{rule.label} 不能大于 {rule.max_val}"
        return f"{rule.label} 必须在 {rule.min_val} 到 {rule.max_val} 之间"

    return ValidationRule(
        name="__range__",
        min_val=min_val,
        max_val=max_val,
        error_formatter=formatter
    )


def create_choices_validator(
    choices: List[Any],
    error_message: Optional[str] = None
) -> ValidationRule:
    """创建可选值验证规则。

    Args:
        choices: 允许的值列表
        error_message: 自定义错误信息模板，可用 name, label, value, choices

    Returns:
        ValidationRule 实例
    """
    def formatter(rule, value, error_type):
        if error_message:
            return error_message.format(
                name=rule.name,
                label=rule.label,
                value=value,
                choices=", ".join(str(c) for c in rule.choices)
            )
        return (
            f"{rule.label} 的值 '{value}' 无效，"
            f"可选值: {', '.join(str(c) for c in rule.choices)}"
        )

    return ValidationRule(
        name="__choices__",
        choices=choices,
        error_formatter=formatter
    )


def create_regex_validator(
    pattern: str,
    error_message: Optional[str] = None
) -> Callable[[Any, str, str], Optional[str]]:
    """创建正则表达式验证器（返回 custom_validator 函数）。

    Args:
        pattern: 正则表达式模式
        error_message: 自定义错误信息，可用 name, label, value, pattern

    Returns:
        可用于 ValidationRule.custom_validator 的函数
    """
    import re
    compiled = re.compile(pattern)

    def validator(value, name, label):
        if not compiled.match(str(value)):
            if error_message:
                return error_message.format(name=name, label=label, value=value, pattern=pattern)
            return f"{label} ({name}) 格式不正确，应匹配模式: {pattern}"
        return None

    return validator


def create_length_validator(
    min_len: Optional[int] = None,
    max_len: Optional[int] = None
) -> Callable[[Any, str, str], Optional[str]]:
    """创建字符串长度验证器（返回 custom_validator 函数）。

    Args:
        min_len: 最小长度
        max_len: 最大长度

    Returns:
        可用于 ValidationRule.custom_validator 的函数
    """
    def validator(value, name, label):
        str_value = str(value)
        if min_len is not None and len(str_value) < min_len:
            return f"{label} ({name}) 长度不能小于 {min_len} 个字符"
        if max_len is not None and len(str_value) > max_len:
            return f"{label} ({name}) 长度不能大于 {max_len} 个字符"
        return None

    return validator


def create_type_validator(
    expected_type: type,
    error_message: Optional[str] = None
) -> Callable[[Any, str, str], Optional[str]]:
    """创建类型验证器（返回 custom_validator 函数）。

    Args:
        expected_type: 期望的类型（int, float, str, bool 等）
        error_message: 自定义错误信息，可用 name, label, value, expected_type

    Returns:
        可用于 ValidationRule.custom_validator 的函数
    """
    def validator(value, name, label):
        if not isinstance(value, expected_type):
            if error_message:
                return error_message.format(
                    name=name, label=label, value=value,
                    expected_type=expected_type.__name__
                )
            return f"{label} ({name}) 必须是 {expected_type.__name__} 类型"
        return None

    return validator


def create_email_validator(
    error_message: Optional[str] = None
) -> Callable[[Any, str, str], Optional[str]]:
    """创建邮箱格式验证器（返回 custom_validator 函数）。

    Args:
        error_message: 自定义错误信息，可用 name, label, value

    Returns:
        可用于 ValidationRule.custom_validator 的函数
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    compiled = re.compile(pattern)

    def validator(value, name, label):
        if not compiled.match(str(value)):
            if error_message:
                return error_message.format(name=name, label=label, value=value)
            return f"{label} ({name}) 邮箱格式不正确"
        return None

    return validator


def create_url_validator(
    schemes: Optional[List[str]] = None,
    error_message: Optional[str] = None
) -> Callable[[Any, str, str], Optional[str]]:
    """创建 URL 格式验证器（返回 custom_validator 函数）。

    Args:
        schemes: 允许的协议列表，如 ["http", "https"]
        error_message: 自定义错误信息，可用 name, label, value

    Returns:
        可用于 ValidationRule.custom_validator 的函数
    """
    import re
    pattern = r'^([a-zA-Z][a-zA-Z0-9+.-]*)://([^/]+)(/.*)?$'
    compiled = re.compile(pattern)

    def validator(value, name, label):
        match = compiled.match(str(value))
        if not match:
            if error_message:
                return error_message.format(name=name, label=label, value=value)
            return f"{label} ({name}) URL 格式不正确"

        if schemes:
            scheme = match.group(1).lower()
            if scheme not in [s.lower() for s in schemes]:
                return f"{label} ({name}) URL 协议必须是 {', '.join(schemes)}"
        return None

    return validator


# ==================== 快捷使用函数 ====================

def validate_required(name: str, label: str, value: Any) -> Optional[str]:
    """快捷必填验证。"""
    if value is None or value == "":
        return f"缺少必填参数: {label} ({name})"
    return None


def validate_choices(name: str, label: str, value: Any, choices: List[Any]) -> Optional[str]:
    """快捷可选值验证。"""
    if value not in choices:
        return (
            f"参数 {label} ({name}) 的值 '{value}' 无效，"
            f"可选值: {', '.join(str(c) for c in choices)}"
        )
    return None


def validate_range(
    name: str, label: str, value: Any,
    min_val: Optional[Union[int, float]] = None,
    max_val: Optional[Union[int, float]] = None
) -> Optional[str]:
    """快捷数值范围验证。"""
    try:
        num_value = float(value)
        if min_val is not None and num_value < min_val:
            return f"参数 {label} ({name}) 的值 {value} 过小，最小值为 {min_val}"
        if max_val is not None and num_value > max_val:
            return f"参数 {label} ({name}) 的值 {value} 过大，最大值为 {max_val}"
    except (ValueError, TypeError):
        return f"参数 {label} ({name}) 的值 '{value}' 必须是数值"
    return None


def validate_port(name: str, label: str, value: Any) -> Optional[str]:
    """快捷端口号验证（1-65535）。"""
    return validate_range(name, label, value, min_val=1, max_val=65535)


def validate_positive_int(name: str, label: str, value: Any) -> Optional[str]:
    """快捷正整数验证。"""
    try:
        int_value = int(value)
        if int_value <= 0:
            return f"参数 {label} ({name}) 必须是正整数"
    except (ValueError, TypeError):
        return f"参数 {label} ({name}) 的值 '{value}' 必须是整数"
    return None


def validate_non_negative(name: str, label: str, value: Any) -> Optional[str]:
    """快捷非负数验证。"""
    try:
        num_value = float(value)
        if num_value < 0:
            return f"参数 {label} ({name}) 不能为负数"
    except (ValueError, TypeError):
        return f"参数 {label} ({name}) 的值 '{value}' 必须是数值"
    return None
