import enum


@enum.unique
class ContactState(enum.StrEnum):
    ESTABLISHED = "established"
    REFUSED = "refused"
    BLOCKED = "blocked"
