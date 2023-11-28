from mongoengine import PointField as MongoPointField, LazyReferenceField
from starlette_admin import BaseField, StringField
from starlette_admin.contrib.mongoengine.converters import ModelConverter
from starlette_admin.converters import converts

from admin.fields import PointField


class MongoengineModelConverter(ModelConverter):

    @converts(MongoPointField)
    def conv_point_field(self, *args, **kwargs) -> BaseField:
        return PointField(**self._field_common(*args, **kwargs))


    @converts(LazyReferenceField)
    def conv_lazy_reference_field(self, *args, **kwargs) -> BaseField:
        return StringField(**self._field_common(*args, **kwargs))