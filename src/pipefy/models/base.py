# ============================================================
# Dependencies
# ============================================================
from typing import Any, Dict


class BaseModel:
    """
    Base model for all SDK models.

    This class enforces explicit parsing through `fromDict`
    implementations in child classes.

    It intentionally does NOT provide automatic parsing logic
    to avoid unsafe instantiation from arbitrary dictionaries.
    """

    @classmethod
    def fromDict(cls, data: Dict[str, Any]):
        """
        Abstract method for parsing dictionaries into model instances.

        Subclasses must implement this method to ensure safe and
        explicit parsing of API data.

        :param data: dict = Raw data to parse into model

        :return: instance = Parsed model instance

        :raises NotImplementedError:
            When subclass does not implement this method

        :example:
            >>> class Example(BaseModel):
            ...     @classmethod
            ...     def fromDict(cls, data):
            ...         return cls()
            >>> isinstance(Example.fromDict({}), Example)
            True
        """