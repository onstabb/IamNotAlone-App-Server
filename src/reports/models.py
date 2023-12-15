from mongoengine import ReferenceField, StringField, EnumField, BooleanField

from models import BaseDocument
from reports.enums import ReportType


class Report(BaseDocument):
    initiator = ReferenceField('User')
    respondent = ReferenceField('User')
    type = EnumField(ReportType)    # type: ReportType
    additional_info = StringField(required=False)   # type: str
    closed = BooleanField(default=False) # type: bool
