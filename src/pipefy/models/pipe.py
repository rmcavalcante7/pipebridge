# ============================================================
# Dependencies
# ============================================================
from typing import Optional, List, Dict, Any

from pipefy.exceptions import RequestError
from pipefy.models.phase import Phase
from pipefy.models.label import Label
from pipefy.models.user import User


class Pipe:
    """
    Represents a Pipefy Pipe with structured and efficient access
    to its related entities.

    This model provides:
        - O(1) access to phases, labels, and users
        - Resilient parsing from API responses
        - Consistent interface aligned with Card and Phase models

    The Pipe acts as an entry point to navigate its internal structure
    without requiring manual iteration.

    :param id: str = Unique identifier of the pipe
    :param name: str | None = Human-readable name of the pipe
    :param phases: list[Phase] | None = List of pipe phases
    :param labels: list[Label] | None = List of pipe labels
    :param users: list[User] | None = List of pipe users

    :example:
        >>> pipe = Pipe(id="1", name="Sales")
        >>> pipe.id
        '1'
    """

    def __init__(
        self,
        id: str,
        name: Optional[str] = None,
        cards_count: int = 0,
        organization_id:  Optional[str] = None,
        phases: Optional[List[Phase]] = None,
        labels: Optional[List[Label]] = None,
        users: Optional[List[User]] = None
    ) -> None:
        """
        Initialize Pipe model.

        :param id: str = Pipe identifier
        :param name: str | None = Pipe name
        :param phases: list[Phase] | None = Pipe phases
        :param labels: list[Label] | None = Pipe labels
        :param users: list[User] | None = Pipe users
        """
        self.id: str = id
        self.name: Optional[str] = name
        self.cards_count: int = cards_count
        self.organization_id: Optional[str] = organization_id

        # ============================================================
        # INTERNAL STORAGE
        # ============================================================
        self._phases: List[Phase] = phases or []
        self._labels: List[Label] = labels or []
        self._users: List[User] = users or []

        # ============================================================
        # FAST ACCESS MAPS (O(1))
        # ============================================================
        self.phases_map: Dict[str, Phase] = {
            phase.id: phase
            for phase in self._phases
            if phase and phase.id
        }

        self.labels_map: Dict[str, Label] = {
            label.id: label
            for label in self._labels
            if label and label.id
        }

        self.users_map: Dict[str, User] = {
            user.id: user
            for user in self._users
            if user and user.id
        }

    # ============================================================
    # FACTORY
    # ============================================================

    @classmethod
    def fromDict(cls, data: Dict[str, Any]) -> "Pipe":
        """
        Create a Pipe instance from structured API data.

        This method performs resilient parsing:
            - Ignores invalid nested items
            - Tracks parsing issues in `_parse_errors`
            - Prevents full failure due to partial inconsistencies

        :param data: dict = Structured pipe data

        :return: Pipe = Parsed Pipe model

        :raises RequestError:
            When input data is invalid or parsing fails critically

        :example:
            >>> pipe = Pipe.fromDict({"id": "1"})
            >>> isinstance(pipe, Pipe)
            True
        """
        try:
            if not isinstance(data, dict):
                raise ValueError("Invalid pipe data")

            # ============================================================
            # Parse error tracking
            # ============================================================
            parse_errors: List[str] = []

            # ============================================================
            # BASIC
            # ============================================================
            id: str = str(data.get("id", ""))
            name: Optional[str] = data.get("name")
            organization_id = data.get("organization", {}).get("id")
            cards_count: int = int(data.get("cards_count") or 0)

            # ============================================================
            # PHASES
            # ============================================================
            phases_data: List[Any] = data.get("phases") or []
            phases: List[Phase] = []

            for item in phases_data:
                try:
                    if item:
                        phases.append(Phase.fromDict(item))
                except Exception as exc:
                    parse_errors.append(
                        f"Phase parse error: {str(exc)}"
                    )
                    continue

            # ============================================================
            # LABELS
            # ============================================================
            labels_data: List[Any] = data.get("labels") or []
            labels: List[Label] = []

            for item in labels_data:
                try:
                    if item:
                        labels.append(Label.fromDict(item))
                except Exception as exc:
                    parse_errors.append(
                        f"Label parse error: {str(exc)}"
                    )
                    continue

            # ============================================================
            # USERS
            # ============================================================
            users_data: List[Any] = data.get("users") or []
            users: List[User] = []

            for item in users_data:
                try:
                    if item:
                        users.append(User.fromDict(item))
                except Exception as exc:
                    parse_errors.append(
                        f"User parse error: {str(exc)}"
                    )
                    continue

            # ============================================================
            # BUILD OBJECT
            # ============================================================
            pipe = cls(
                id=id,
                name=name,
                organization_id=organization_id,
                cards_count=cards_count,
                phases=phases,
                labels=labels,
                users=users
            )

            pipe._parse_errors = parse_errors

            return pipe

        except Exception as exc:
            raise RequestError(
                f"Class: {cls.__name__}\n"
                f"Method: fromDict\n"
                f"Error: {str(exc)}"
            ) from exc

    # ============================================================
    # PROPERTIES
    # ============================================================

    @property
    def phases(self) -> List[Phase]:
        """
        Retrieve all phases associated with the pipe.

        WARNING:
            Prefer using `getPhase()` or `[]` access for O(1) lookup.

        :return: list[Phase] = List of phases

        :example:
            >>> pipe = Pipe.fromDict({"id": "1", "phases": []})
            >>> isinstance(pipe.phases, list)
            True
        """
        return self._phases

    @property
    def labels(self) -> List[Label]:
        """
        Retrieve all labels associated with the pipe.

        WARNING:
            Prefer using `getLabel()` for direct access.

        :return: list[Label]

        :example:
            >>> pipe = Pipe.fromDict({"id": "1", "labels": []})
            >>> isinstance(pipe.labels, list)
            True
        """
        return self._labels

    @property
    def users(self) -> List[User]:
        """
        Retrieve all users associated with the pipe.

        WARNING:
            Prefer using `getUser()` for direct access.

        :return: list[User]

        :example:
            >>> pipe = Pipe.fromDict({"id": "1", "users": []})
            >>> isinstance(pipe.users, list)
            True
        """
        return self._users

    # ============================================================
    # HELPERS (O(1) ACCESS)
    # ============================================================

    def getPhase(self, phase_id: str) -> Optional[Phase]:
        """
        Retrieve a phase by its identifier.

        :param phase_id: str = Phase identifier

        :return: Phase | None = Phase if found, otherwise None

        :example:
            >>> pipe = Pipe.fromDict({"id": "1", "phases": []})
            >>> pipe.getPhase("x") is None
            True
        """
        return self.phases_map.get(phase_id)

    def getLabel(self, label_id: str) -> Optional[Label]:
        """
        Retrieve a label by its identifier.

        :param label_id: str = Label identifier

        :return: Label | None

        :example:
            >>> pipe = Pipe.fromDict({"id": "1", "labels": []})
            >>> pipe.getLabel("x") is None
            True
        """
        return self.labels_map.get(label_id)

    def getUser(self, user_id: str) -> Optional[User]:
        """
        Retrieve a user by its identifier.

        :param user_id: str = User identifier

        :return: User | None

        :example:
            >>> pipe = Pipe.fromDict({"id": "1", "users": []})
            >>> pipe.getUser("x") is None
            True
        """
        return self.users_map.get(user_id)

    def __getitem__(self, phase_id: str) -> Phase:
        """
        Retrieve a phase using dictionary-like access.

        This provides direct O(1) access to phases.

        :param phase_id: str = Phase identifier

        :return: Phase = Requested phase

        :raises KeyError:
            If the phase does not exist

        :example:
            >>> pipe = Pipe.fromDict({"id": "1", "phases": []})
            >>> try:
            ...     pipe["x"]
            ... except KeyError:
            ...     True
            True
        """
        return self.phases_map[phase_id]