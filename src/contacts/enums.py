import enum


@enum.unique
class ContactState(enum.StrEnum):
    ESTABLISHED = "established"
    REFUSED = "refused"
    BLOCKED = "blocked"


@enum.unique
class ContactUpdateAction(enum.StrEnum):
    ESTABLISH = "establish"
    REFUSE = "refuse"
    BLOCK = "block"
    SEEN = "seen"


@enum.unique
class ContactType(enum.StrEnum):
    LIKE = "likes"
    DIALOG = "dialogs"