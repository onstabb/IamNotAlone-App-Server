from reports import service
from reports.schemas import ReportIn


def test_create_report(report_factory, user_factory):
    initiator, respondent = user_factory.create_batch(size=2, )
    report = report_factory.build(initiator=initiator, respondent=respondent)
    report_in = ReportIn(respondent=respondent.id, reason=report.reason, additional_info=report.additional_info)

    assert service.create_report(initiator, respondent, report_in)