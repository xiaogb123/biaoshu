from typing import BinaryIO,Protocol
import shutil
from pathlib import Path
from uuid import uuid4
from app.core.config import settings

class Storage(Protocol):
    def save(self,key:str,stream:BinaryIO) -> str: ...
    def open(self,key:str) -> BinaryIO: ...
    def delete(self,key:str) -> None: ...

def make_key(tenant_id:int,suffix:str = ".pdf") -> str:
    return f"{tenant_id}/{uuid4().hex}{suffix}"

class LocalStorage:
    def __init__(self,root:Path) -> None:
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self,key:str) -> Path:
        p = (self.root / key).resolve()
        if not p.is_relative_to(self.root):
            raise ValueError(f"非法存储 key:{key}")
        return p

    def save(self,key:str,stream:BinaryIO) -> str:
        target = self._path(key)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("wb") as f:
            shutil.copyfileobj(stream, f,1024*1024)
        return key

    def open(self,key:str) ->BinaryIO:
        return self._path(key).open("rb")

    def delete(self,key:str) -> None:
        self._path(key).unlink(missing_ok = True)

storage = LocalStorage(settings.UPLOAD_DIR)