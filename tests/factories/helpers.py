from mongoengine import ReferenceField
from models import BaseDocument


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
