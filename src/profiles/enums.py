import enum


@enum.unique
class Gender(enum.StrEnum):
    MALE = "male"
    FEMALE = "female"
    ANY = "any"


@enum.unique
class ResidenceLength(enum.StrEnum):
    LOCAL = "local"
    LONG = "long"
    SOMETIME = "sometime"
    RECENTLY = "recently"


@enum.unique
class ResidencePlan(enum.StrEnum):
    IDK = "idk"
    STAY = "stay"
    MOVE = "move"
    BACK = "back"

