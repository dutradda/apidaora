"""
ASGI App using dataclasses module for request/response objects
"""

__version__ = '0.28.0'

from apidaora.app import appdaora
from apidaora.bodies import GZipFactory
from apidaora.class_controller import ClassController
from apidaora.content import ContentType
from apidaora.exceptions import BadRequestError
from apidaora.header import Header
from apidaora.method import MethodType
from apidaora.middlewares import (
    BackgroundTaskMiddleware,
    CorsMiddleware,
    Middlewares,
)
from apidaora.request import Request
from apidaora.responses import (
    Response,
    css,
    html,
    javascript,
    json,
    no_content,
    not_found,
    text,
)
from apidaora.route.decorator import RoutedControllerTypeHint, route


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
    'Request',
    'ClassController',
    'BackgroundTaskMiddleware',
    'RoutedControllerTypeHint',
    'css',
    'javascript',
]
