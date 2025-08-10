"""
browser package

This is the main package for the Python web browser project.
It exposes key classes and functions from subpackages for easy importing.
"""

# You can expose common functionality at the package level
from .core.Browser import Browser
from .core.URL import URL

__all__ = [
    "Browser",
    "URL",
]
