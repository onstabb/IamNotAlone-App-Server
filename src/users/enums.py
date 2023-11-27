import enum


@enum.unique
class UserRole(enum.StrEnum):
    USER = "user"
# VIP_USER
    MODERATOR = "moderator"
    ADMIN = "admin"

    @classmethod
    def managers(cls) -> tuple['UserRole', ...]:
        return cls.ADMIN, cls.MODERATOR
