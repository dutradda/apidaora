"""
ASGI App using dataclasses module for request/response objects
"""

__version__ = '0.11.1'

from apidaora.app import appdaora
from apidaora.bodies import GZipFactory
from apidaora.content import ContentType
from apidaora.exceptions import BadRequestError
from apidaora.header import header
from apidaora.method import MethodType
from apidaora.responses import html, json, text
from apidaora.route.decorator import route


__all__ = [
    'BadRequestError',
    'GZipFactory',
    'ContentType',
    'MethodType',
    'appdaora',
    'header',
    'html',
    'json',
    'text',
    'route',
]
