import io
from typing import IO, Optional, Type

from dictdaora import DictDaora
from jsondaora import jsondaora


try:
    import gzip
except Exception:
    gzip = None  # type: ignore


class _GZipFactory(DictDaora):  # type: ignore
    mode: str
    compresslevel: int
    encoding: Optional[str]
    errors: Optional[str]
    newline: Optional[str]
    value: bytes

    def open(self) -> IO[bytes]:
        if self.value:
            return gzip.open(
                io.BytesIO(self.value),
                self.mode,
                self.compresslevel,
                self.encoding,
                self.errors,
                self.newline,
            )

        raise ValueError(self.value)


def gzip_body(
    mode: str = 'rb',
    compresslevel: int = 9,
    encoding: Optional[str] = None,
    errors: Optional[str] = None,
    newline: Optional[str] = None,
) -> Type[_GZipFactory]:
    cls_attributes = dict(
        mode=mode,
        compresslevel=compresslevel,
        encoding=encoding,
        errors=errors,
        newline=newline,
    )
    factory = type('GZipFactory', (_GZipFactory,), cls_attributes)
    return jsondaora(factory)  # type: ignore
