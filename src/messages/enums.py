import enum


@enum.unique
class MessageType(enum.Enum):
    CONTACT_ESTABLISHED = "RELATIONSHIP_ESTABLISHED"
    LIKE = "LIKE"
    MESSAGE = "MESSAGE"
