from reports.models import Report
from reports.schemas import ReportIn
from users.models import User


def create_report(initiator: User, respondent: User, report_data_in: ReportIn) -> Report:
    report = Report(initiator=initiator, respondent=respondent, **report_data_in.model_dump(exclude={'respondent'}))
    report.save()
    return report
