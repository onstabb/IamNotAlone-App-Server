__all__ = ("FileBucket", "BaseBucket")

import typing
from abc import ABC, abstractmethod


FileBucket = typing.TypeVar("FileBucket", bound="BaseBucket")


class BaseBucket(ABC):

    @abstractmethod
    def upload(self, file: typing.BinaryIO, filename: str, **kwargs) -> str:
        pass
