from enum import Enum


class ContentType(Enum):
    APPLICATION_JSON = 'application/json'
    APPLICATION_YAML = 'application/x-yaml'
    TEXT_HTML = 'text/html; charset=utf-8'
    TEXT_PLAIN = 'text/plain'
    TEXT_CSS = 'text/css'
    TEXT_JAVASCRIPT = 'text/javascript'
