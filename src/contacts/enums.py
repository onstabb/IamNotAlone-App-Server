import enum



@enum.unique
class ContactState(enum.StrEnum):
    WAIT = "wait"
    ESTABLISHED = "established"
    REFUSED = "refused"
    BLOCKED = "blocked"

    @classmethod
    def finalized_states(cls) -> tuple['ContactState', ...]:
        return cls.ESTABLISHED, cls.BLOCKED, cls.REFUSED
