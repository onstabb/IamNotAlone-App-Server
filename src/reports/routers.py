from fastapi import APIRouter

from reports import service
from reports.schemas import ReportIn
from users.dependencies import CurrentActiveUser, get_active_completed_user


router = APIRouter()


@router.post("")
def create_report(data: ReportIn, current_user: CurrentActiveUser):
    respondent = get_active_completed_user(data.respondent)
    new_report = service.create_report(current_user, respondent, data)
    return new_report
