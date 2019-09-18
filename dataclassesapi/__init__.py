"""
ASGI App using dataclasses module for request/response objects
"""

__version__ = '0.2.0'

from dataclassesapi.app import asgi_app
from dataclassesapi.method import MethodType
from dataclassesapi.router import Route


__all__ = [asgi_app.__name__, MethodType.__name__, Route.__name__]
