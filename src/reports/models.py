from mongoengine import ReferenceField, StringField, EnumField, BooleanField

from models import BaseDocument
from reports.enums import ReportReason


class Report(BaseDocument):
    initiator = ReferenceField('User')
    respondent = ReferenceField('User')
    reason = EnumField(ReportReason)    # type: ReportReason
    additional_info = StringField(required=False)   # type: str
    opened = BooleanField(default=True) # type: bool
