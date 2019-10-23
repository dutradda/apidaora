import io
from typing import IO, Optional

from dictdaora import DictDaora


try:
    import gzip
except Exception:
    gzip = None  # type: ignore


class GZipFactory(DictDaora):
    mode: str = 'rb'
    compresslevel: int = 9
    encoding: Optional[str] = None
    errors: Optional[str] = None
    newline: Optional[str] = None
    value: bytes

    def open(self) -> IO[str]:
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
