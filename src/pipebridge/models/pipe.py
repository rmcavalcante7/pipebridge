# ============================================================
# Dependencies
# ============================================================
from typing import Optional, List, Dict, Any

from pipebridge.exceptions import RequestError
from pipebridge.models.base import BaseModel
from pipebridge.models.phase import Phase
from pipebridge.models.label import Label
from pipebridge.models.user import User


class Pipe(BaseModel):
    """
    Represents a Pipefy Pipe with structured and efficient access
    to its related entities.

    This model provides:
        - O(1) access to phases, labels, and users
        - Resilient parsing from API responses
        - Consistent interface aligned with Card and Phase models

    The Pipe acts as an entry point to navigate its internal structure
    without requiring manual iteration. Internal maps are kept for efficient
    lookup, but semantic helper methods should be preferred over direct map
    access in SDK code.

    Preferred access patterns:

    - ``getPhase(...)``
    - ``hasPhase(...)``
    - ``requirePhase(...)``
    - ``iterPhases()``
    - ``getLabel(...)``
    - ``requireLabel(...)``
    - ``iterLabels()``
    - ``getUser(...)``
    - ``requireUser(...)``
    - ``iterUsers()``
    - ``iterAllFields()``
    - ``getFieldsByType(...)``

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
        organization_id: Optional[str] = None,
        phases: Optional[List[Phase]] = None,
        labels: Optional[List[Label]] = None,
        users: Optional[List[User]] = None,
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
            phase.id: phase for phase in self._phases if phase and phase.id
        }

        self.labels_map: Dict[str, Label] = {
            label.id: label for label in self._labels if label and label.id
        }

        self.users_map: Dict[str, User] = {
            user.id: user for user in self._users if user and user.id
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
                    parse_errors.append(f"Phase parse error: {str(exc)}")
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
                    parse_errors.append(f"Label parse error: {str(exc)}")
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
                    parse_errors.append(f"User parse error: {str(exc)}")
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
                users=users,
            )

            pipe._parse_errors = parse_errors

            return pipe

        except Exception as exc:
            raise RequestError(
                f"Class: {cls.__name__}\n" f"Method: fromDict\n" f"Error: {str(exc)}"
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

    def hasPhase(self, phase_id: str) -> bool:
        """
        Check whether a phase exists in the pipe.

        :param phase_id: str = Phase identifier

        :return: bool = Whether the phase exists
        """
        return self.getPhase(phase_id) is not None

    def requirePhase(self, phase_id: str) -> Phase:
        """
        Retrieve a phase and fail when it does not exist.

        :param phase_id: str = Phase identifier

        :return: Phase = Requested phase

        :raises RequestError:
            When the phase does not exist in the pipe
        """
        phase = self.getPhase(phase_id)
        if phase is None:
            raise RequestError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: requirePhase\n"
                f"Error: Phase '{phase_id}' does not exist in pipe '{self.id}'"
            )
        return phase

    def iterPhases(self) -> List[Phase]:
        """
        Return all phases as an ordered list.

        :return: list[Phase] = Pipe phases
        """
        return list(self.phases)

    def iterAllFields(self) -> List[Any]:
        """
        Return all phase fields from the pipe in a flat list.

        :return: list[Any] = All fields across phases
        """
        fields: List[Any] = []
        for phase in self.phases:
            fields.extend(phase.iterFields())
        return fields

    def getFieldsByType(self, field_type: str) -> List[Any]:
        """
        Retrieve all fields across all phases matching a given type.

        :param field_type: str = Field type

        :return: list[Any] = Matching fields across phases
        """
        fields: List[Any] = []
        for phase in self.phases:
            fields.extend(phase.getFieldsByType(field_type))
        return fields

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

    def hasLabel(self, label_id: str) -> bool:
        """
        Check whether a label exists in the pipe.

        :param label_id: str = Label identifier

        :return: bool = Whether the label exists
        """
        return self.getLabel(label_id) is not None

    def requireLabel(self, label_id: str) -> Label:
        """
        Retrieve a label and fail when it does not exist.

        :param label_id: str = Label identifier

        :return: Label = Requested label

        :raises RequestError:
            When the label does not exist in the pipe
        """
        label = self.getLabel(label_id)
        if label is None:
            raise RequestError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: requireLabel\n"
                f"Error: Label '{label_id}' does not exist in pipe '{self.id}'"
            )
        return label

    def iterLabels(self) -> List[Label]:
        """
        Return all labels as an ordered list.

        :return: list[Label] = Pipe labels
        """
        return list(self.labels)

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

    def getUserByName(self, user_name: str) -> Optional[User]:
        """
        Retrieve a user by human-readable name using case-insensitive matching.

        :param user_name: str = User display name

        :return: User | None = Matching user when found
        """
        normalized_name = str(user_name or "").strip().casefold()
        if not normalized_name:
            return None

        for user in self.users:
            if str(user.name or "").strip().casefold() == normalized_name:
                return user
        return None

    def requireUserByName(self, user_name: str) -> User:
        """
        Retrieve a user by name and fail when it does not exist.

        :param user_name: str = User display name

        :return: User = Requested user

        :raises RequestError:
            When the user does not exist in the pipe user list
        """
        user = self.getUserByName(user_name)
        if user is None:
            raise RequestError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: requireUserByName\n"
                f"Error: User named '{user_name}' does not exist in pipe '{self.id}'"
            )
        return user

    def hasUser(self, user_id: str) -> bool:
        """
        Check whether a user exists in the pipe user list.

        :param user_id: str = User identifier

        :return: bool = Whether the user exists
        """
        return self.getUser(user_id) is not None

    def requireUser(self, user_id: str) -> User:
        """
        Retrieve a user and fail when it does not exist.

        :param user_id: str = User identifier

        :return: User = Requested user

        :raises RequestError:
            When the user does not exist in the pipe
        """
        user = self.getUser(user_id)
        if user is None:
            raise RequestError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: requireUser\n"
                f"Error: User '{user_id}' does not exist in pipe '{self.id}'"
            )
        return user

    def iterUsers(self) -> List[User]:
        """
        Return all users as an ordered list.

        :return: list[User] = Pipe users
        """
        return list(self.users)

    def __getitem__(self, phase_id: str) -> Phase:
        """
        Retrieve a phase using dictionary-like access.

        This provides direct O(1) access to phases, but semantic helpers such
        as ``getPhase()`` and ``requirePhase()`` should be preferred in SDK
        code.

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
