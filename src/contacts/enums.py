import enum


@enum.unique
class ContactState(enum.StrEnum):
    ESTABLISHED = "established"
    REFUSED = "refused"
    BLOCKED = "blocked"


@enum.unique
class ContactType(enum.StrEnum):
    LIKES = "likes"
    NEW_ESTABLISHED = "established"
