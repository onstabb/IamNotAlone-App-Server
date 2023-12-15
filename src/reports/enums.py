import enum


@enum.unique
class ReportType(enum.StrEnum):
    INAPPROPRIATE_BEHAVIOR = "inappropriate_behavior"
    INAPPROPRIATE_CONTENT = "inappropriate_content"
    FRAUD_OR_AD = "fraud_or_ad"
    UNDERAGE = "underage"
    OTHER = "other"