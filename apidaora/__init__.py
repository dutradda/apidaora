"""
ASGI App using dataclasses module for request/response objects
"""

__version__ = '0.5.1'

from apidaora.content import ContentType
from apidaora.method import MethodType


__all__ = [ContentType.__name__, MethodType.__name__]
