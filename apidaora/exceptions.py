class APIDaoraError(Exception):
    ...


class MethodNotFoundError(APIDaoraError):
    ...


class PathNotFoundError(APIDaoraError):
    ...


class InvalidPathParams(APIDaoraError):
    ...
