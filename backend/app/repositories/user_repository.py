from app.schemas.user import AuthenticatedUser


class UserRepository:
    def get_by_id(self, user_id: str) -> AuthenticatedUser | None:
        return None


def get_user_repository() -> UserRepository:
    return UserRepository()
