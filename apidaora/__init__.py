"""
ASGI App using dataclasses module for request/response objects
"""

__version__ = '0.17.0'

from apidaora.app import appdaora
from apidaora.bodies import GZipFactory
from apidaora.class_controller import ClassController
from apidaora.content import ContentType
from apidaora.exceptions import BadRequestError
from apidaora.header import Header
from apidaora.method import MethodType
from apidaora.middlewares import CorsMiddleware, MiddlewareRequest, Middlewares
from apidaora.responses import (
    Response,
    html,
    json,
    no_content,
    not_found,
    text,
)
from apidaora.route.decorator import route


__all__ = [
    'BadRequestError',
    'GZipFactory',
    'ContentType',
    'MethodType',
    'appdaora',
    'Header',
    'html',
    'json',
    'text',
    'route',
    'no_content',
    'not_found',
    'Response',
    'Middlewares',
    'CorsMiddleware',
    'MiddlewareRequest',
    'ClassController',
]
