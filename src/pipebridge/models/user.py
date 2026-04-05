# ============================================================
# Dependencies
# ============================================================
from typing import Dict, Optional, Any
import inspect

from pipebridge.models.base import BaseModel
from pipebridge.exceptions import RequestError


class User(BaseModel):
    """
    Represents a Pipefy user.

    :param id: str = User identifier
    :param name: str | None = User name
    :param email: str | None = User email
    """

    def __init__(
        self, id: str, name: Optional[str] = None, email: Optional[str] = None
    ) -> None:
        """
        Initialize a Pipefy user model.

        :param id: str = User identifier
        :param name: str | None = User name
        :param email: str | None = User email
        """
        self.id: str = id
        self.name: Optional[str] = name
        self.email: Optional[str] = email

    @classmethod
    def fromDict(cls, data: Dict[str, Any]) -> "User":
        """
        Safely parse a User from structured data.

        :param data: dict = Raw user data

        :return: User = Parsed User instance

        :raises RequestError:
            When parsing fails critically

        :example:
            >>> user = User.fromDict({"id": "1", "name": "John"})
            >>> isinstance(user, User)
            True
        """
        try:
            if not isinstance(data, dict):
                raise ValueError("Invalid user data")

            return cls(
                id=str(data.get("id", "")),
                name=data.get("name"),
                email=data.get("email"),
            )

        except Exception as exc:
            raise RequestError(
                f"Class: {cls.__name__}\n" f"Method: fromDict\n" f"Error: {str(exc)}"
            ) from exc


# ============================================================
# Main Test
# ============================================================

if __name__ == "__main__":
    sample = {"id": "user_1", "name": "John Doe"}

    user = User.fromDict(sample)
    print(user.id, user.name)
