import datetime
from typing import Type

import factory

from models import BaseDocument


class Objects:
    """
    This class is intended to use with factory.Iterator over a subset of objects from a MongoDB collection
    defined by the document_cls within the specified slice.

    """
    def __init__(self, document_cls: Type[BaseDocument], slice_obj: slice):
        self._doc_cls: Type[BaseDocument] = document_cls
        self._slice: slice = slice_obj

    def __iter__(self):
        return iter(self._doc_cls.objects[self._slice])


def build_json_dict(cls: Type[factory.mongoengine.MongoEngineFactory], **kwargs) -> dict:
    result: dict = factory.build(dict, FACTORY_CLASS=cls, **kwargs)

    for key, value in cls.__dict__.items():
        if isinstance(value, factory.SubFactory):
            result[key] = build_json_dict(cls=value.get_factory())

    for key, value in result.items():
        if isinstance(value, datetime.date):
            result[key] = value.isoformat()

    return result
