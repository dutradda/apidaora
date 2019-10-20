"""
ASGI App using dataclasses module for request/response objects
"""

__version__ = '0.10.0'

from apidaora.app import appdaora
from apidaora.bodies import gzip_body
from apidaora.content import ContentType
from apidaora.exceptions import BadRequestError
from apidaora.header import header
from apidaora.method import MethodType
from apidaora.responses import html, json, text
from apidaora.route.decorator import route


__all__ = [
    BadRequestError.__name__,
    ContentType.__name__,
    MethodType.__name__,
    appdaora.__name__,
    gzip_body.__name__,
    header.__name__,
    html.__name__,
    json.__name__,
    text.__name__,
    route.__name__,
]
