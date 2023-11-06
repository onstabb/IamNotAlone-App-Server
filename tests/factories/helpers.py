from typing import Type

from mongoengine import ReferenceField
from models import BaseDocument



class Objects:

    def __init__(self, document_cls: Type[BaseDocument], slice_obj: slice):
        self._doc_cls: Type[BaseDocument] = document_cls
        self._slice: slice = slice_obj

    def __iter__(self):
        return iter(self._doc_cls.objects[self._slice])


def create_reference_field_documents(document: BaseDocument) -> None:
    for name, field in document.get_field_info().values():
        if isinstance(field, ReferenceField):
            attribute = getattr(document, name)
            if isinstance(attribute, BaseDocument):
                attribute.save()


class CreateReferenceFieldDocumentsMixin:

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        instance = model_class(*args, **kwargs)
        create_reference_field_documents(instance)
        return instance
