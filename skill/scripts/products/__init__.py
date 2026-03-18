"""
Product auto-discovery package.

Importing this package triggers automatic discovery and registration
of all product definition files in this directory.
"""

from framework.registry import discover_products

# Auto-discover on import
discover_products()
