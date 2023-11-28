from pydantic import BaseModel, constr

from models import PydanticObjectId
from reports.config import REPORT_ADDITIONAL_INFO_MAX_LENGTH
from reports.enums import ReportReason


class ReportIn(BaseModel):
    respondent: PydanticObjectId
    reason: ReportReason
    additional_info: constr(max_length=REPORT_ADDITIONAL_INFO_MAX_LENGTH) | None
