"""Module builder DSL for constructing BSS modules declaratively.

This module provides a fluent API for building module configurations
used in Alibaba Cloud BSS OpenAPI requests.

Example:
    >>> from builders import ModuleBuilder
    >>> modules = (
    ...     ModuleBuilder()
    ...     .add("Instance", "instance_type={instance_type}")
    ...     .add_conditional("Disk", "size={disk_size}", condition=lambda p: p.get("disk_size", 0) > 0)
    ...     .build({"instance_type": "ecs.g7.large", "disk_size": 100})
    ... )
    >>> print(modules)
    [{'module_code': 'Instance', 'config': 'instance_type=ecs.g7.large', 'price_type': 'Monthly'},
     {'module_code': 'Disk', 'config': 'size=100', 'price_type': 'Monthly'}]
"""

from typing import Any, Callable, Dict, List, Optional


class ModuleBuilder:
    """Builder class for constructing BSS module configurations.

    Provides a fluent, chainable API for defining modules with support
    for conditional modules and template string formatting.

    Attributes:
        _definitions: List of module definitions (code, template, condition).
        _default_price_type: Default price type for modules.
    """

    def __init__(self, default_price_type: str = "Monthly"):
        """Initialize the ModuleBuilder.

        Args:
            default_price_type: Default pricing type for modules.
                               Common values: "Monthly", "PayAsYouGo".
        """
        self._definitions: List[Dict[str, Any]] = []
        self._default_price_type: str = default_price_type

    def add(
        self,
        module_code: str,
        config_template: str,
        price_type: Optional[str] = None,
    ) -> "ModuleBuilder":
        """Add a module definition.

        Args:
            module_code: The BSS module code (e.g., "Instance", "Disk").
            config_template: Template string for config, uses {param} syntax.
                            Example: "instance_type={instance_type}".
            price_type: Override default price type (uses default if None).

        Returns:
            self for method chaining.

        Example:
            >>> builder = ModuleBuilder()
            >>> builder.add("Instance", "type={instance_type}")
        """
        self._definitions.append({
            "module_code": module_code,
            "config_template": config_template,
            "price_type": price_type,
            "condition": None,
        })
        return self

    def add_conditional(
        self,
        module_code: str,
        config_template: str,
        condition: Callable[[Dict[str, Any]], bool],
        price_type: Optional[str] = None,
    ) -> "ModuleBuilder":
        """Add a conditional module definition.

        The module is only included if the condition function returns True.

        Args:
            module_code: The BSS module code.
            config_template: Template string for config.
            condition: Function that takes params dict and returns bool.
            price_type: Override default price type.

        Returns:
            self for method chaining.

        Example:
            >>> builder = ModuleBuilder()
            >>> builder.add_conditional(
            ...     "Disk",
            ...     "size={disk_size}",
            ...     condition=lambda p: p.get("disk_size", 0) > 0
            ... )
        """
        self._definitions.append({
            "module_code": module_code,
            "config_template": config_template,
            "price_type": price_type,
            "condition": condition,
        })
        return self

    def add_multiple(
        self,
        modules: List[Dict[str, Any]],
    ) -> "ModuleBuilder":
        """Add multiple module definitions at once.

        Args:
            modules: List of module definition dicts with keys:
                    - module_code (str, required)
                    - config_template (str, required)
                    - price_type (str, optional)
                    - condition (callable, optional)

        Returns:
            self for method chaining.

        Example:
            >>> builder = ModuleBuilder()
            >>> builder.add_multiple([
            ...     {"module_code": "Instance", "config_template": "type={t}"},
            ...     {"module_code": "Disk", "config_template": "size={s}",
            ...      "condition": lambda p: p.get("s", 0) > 0},
            ... ])
        """
        for module in modules:
            self._definitions.append({
                "module_code": module["module_code"],
                "config_template": module["config_template"],
                "price_type": module.get("price_type"),
                "condition": module.get("condition"),
            })
        return self

    def _format_config(self, template: str, params: Dict[str, Any]) -> str:
        """Format a config template with parameters.

        Args:
            template: Template string with {placeholder} syntax.
            params: Parameter dictionary for substitution.

        Returns:
            Formatted config string.

        Note:
            Missing placeholders are left as-is (not replaced).
        """
        try:
            return template.format(**params)
        except KeyError:
            # Partial formatting - only replace existing keys
            result = template
            for key, value in params.items():
                placeholder = "{" + key + "}"
                if placeholder in result:
                    result = result.replace(placeholder, str(value))
            return result

    def build(self, params: Dict[str, Any]) -> List[Dict[str, str]]:
        """Build the final module list from parameters.

        Args:
            params: Dictionary of parameter values for template substitution
                   and condition evaluation.

        Returns:
            List of module dicts ready for BSS API:
            [{"module_code": str, "config": str, "price_type": str}, ...]

        Example:
            >>> builder = ModuleBuilder()
            >>> builder.add("Instance", "type={t}")
            >>> modules = builder.build({"t": "ecs.g7.large"})
            >>> print(modules)
            [{'module_code': 'Instance', 'config': 'type=ecs.g7.large', 'price_type': 'Monthly'}]
        """
        result: List[Dict[str, str]] = []

        for definition in self._definitions:
            # Check condition
            condition = definition["condition"]
            if condition is not None and not condition(params):
                continue

            # Format config template
            config = self._format_config(definition["config_template"], params)

            # Determine price type
            price_type = definition["price_type"] or self._default_price_type

            result.append({
                "module_code": definition["module_code"],
                "config": config,
                "price_type": price_type,
            })

        return result

    def clear(self) -> "ModuleBuilder":
        """Clear all module definitions.

        Returns:
            self for method chaining.
        """
        self._definitions.clear()
        return self

    def copy(self) -> "ModuleBuilder":
        """Create a copy of this builder with the same definitions.

        Returns:
            New ModuleBuilder instance with copied definitions.
        """
        new_builder = ModuleBuilder(self._default_price_type)
        new_builder._definitions = self._definitions.copy()
        return new_builder


def create_builder(default_price_type: str = "Monthly") -> ModuleBuilder:
    """Factory function to create a new ModuleBuilder instance.

    Args:
        default_price_type: Default pricing type for modules.

    Returns:
        New ModuleBuilder instance.

    Example:
        >>> from builders import create_builder
        >>> builder = create_builder("PayAsYouGo")
    """
    return ModuleBuilder(default_price_type)


def build_modules_from_specs(
    params: Dict[str, Any],
    specs: List[Dict[str, Any]],
    default_price_type: str = "Monthly",
) -> List[Dict[str, str]]:
    """Build modules from a list of specifications.

    Convenience function for simple use cases without maintaining
    a builder instance.

    Args:
        params: Parameter values for template substitution.
        specs: List of module specification dicts with keys:
               - module_code (str, required)
               - config_template (str, required)
               - price_type (str, optional)
               - condition (callable, optional)
        default_price_type: Default price type for modules.

    Returns:
        List of module dicts ready for BSS API.

    Example:
        >>> specs = [
        ...     {"module_code": "Instance", "config_template": "type={t}"},
        ...     {"module_code": "Disk", "config_template": "size={s}",
        ...      "condition": lambda p: p.get("s", 0) > 0},
        ... ]
        >>> modules = build_modules_from_specs({"t": "ecs", "s": 100}, specs)
    """
    builder = ModuleBuilder(default_price_type)
    builder.add_multiple(specs)
    return builder.build(params)
