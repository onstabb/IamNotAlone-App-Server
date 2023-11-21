import enum


@enum.unique
class NotificationType(enum.StrEnum):
    CONTACT_ESTABLISHED = "RELATIONSHIP_ESTABLISHED"
    LIKE = "LIKE"
    MESSAGE = "MESSAGE"
