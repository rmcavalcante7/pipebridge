# ============================================================
# Dependencies:
# - Python 3.10+
# ============================================================

from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Dict, Optional, Set, List


# ============================================================
# Exceptions
# ============================================================

class FieldPermissionError(Exception):
    """Custom exception for field permission violations."""


class RuleNotFoundError(Exception):
    """Custom exception when a rule is not found."""


# ============================================================
# Domain Models
# ============================================================

@dataclass(frozen=True)
class FieldRule:
    """
    Represents a rule for a specific field.

    :param field_id: str = Unique identifier of the field
    :param allowed_phases: set[str] | None = Explicit allowed phases
    :param blocked_phases: set[str] | None = Explicit blocked phases
    """
    field_id: str
    allowed_phases: Optional[Set[str]] = None
    blocked_phases: Optional[Set[str]] = None


# ============================================================
# Factory
# ============================================================

class FieldRuleFactory:
    """
    Factory responsible for creating FieldRule instances dynamically.

    Supports flexible rule creation from configuration dictionaries.

    This allows external configuration (JSON, YAML, DB, etc.)
    without changing code.

    :example:
        >>> factory = FieldRuleFactory()
        >>> rule = factory.createRule({
        ...     "field_id": "f1",
        ...     "allowed_phases": ["p1", "p2"]
        ... })
        >>> rule.field_id
        'f1'
    """

    def createRule(self, config: Dict) -> FieldRule:
        """
        Create a FieldRule from a configuration dictionary.

        :param config: dict = Rule configuration

        :return: FieldRule = Created rule instance

        :raises ValueError:
            When required fields are missing or invalid
        """
        try:
            field_id: str = config["field_id"]

            allowed_phases: Optional[Set[str]] = (
                set(config["allowed_phases"])
                if "allowed_phases" in config and config["allowed_phases"] is not None
                else None
            )

            blocked_phases: Optional[Set[str]] = (
                set(config["blocked_phases"])
                if "blocked_phases" in config and config["blocked_phases"] is not None
                else None
            )

            return FieldRule(
                field_id=field_id,
                allowed_phases=allowed_phases,
                blocked_phases=blocked_phases
            )

        except KeyError as exc:
            raise ValueError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: createRule\n"
                f"Missing key: {str(exc)}"
            ) from exc

        except Exception as exc:
            raise ValueError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: createRule\n"
                f"Error: {str(exc)}"
            ) from exc


# ============================================================
# Registry
# ============================================================

class FieldRuleRegistry:
    """
    Registry that stores and manages FieldRule instances.

    :example:
        >>> registry = FieldRuleRegistry()
        >>> registry.registerRule(FieldRule("f1"))
        >>> registry.getRule("f1").field_id
        'f1'
    """

    def __init__(self) -> None:
        self._rules: Dict[str, FieldRule] = {}

    def registerRule(self, rule: FieldRule) -> None:
        """
        Register a FieldRule.

        :param rule: FieldRule = Rule to register

        :raises ValueError:
            When rule is invalid
        """
        if not isinstance(rule, FieldRule):
            raise ValueError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: registerRule\n"
                f"Invalid rule type"
            )

        self._rules[rule.field_id] = rule

    def getRule(self, field_id: str) -> FieldRule:
        """
        Retrieve a rule by field_id.

        :param field_id: str = Field identifier

        :return: FieldRule = Corresponding rule

        :raises RuleNotFoundError:
            When rule does not exist
        """
        try:
            return self._rules[field_id]
        except KeyError as exc:
            raise RuleNotFoundError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: getRule\n"
                f"Rule not found for field_id: {field_id}"
            ) from exc


# ============================================================
# Service
# ============================================================

class FieldPermissionService:
    """
    Service responsible for validating field operations.

    :example:
        >>> registry = FieldRuleRegistry()
        >>> registry.registerRule(FieldRule("f1", allowed_phases={"p1"}))
        >>> service = FieldPermissionService(registry)
        >>> service.validateFieldEdit("f1", "p1")
    """

    def __init__(self, registry: FieldRuleRegistry) -> None:
        self._registry = registry

    def validateFieldEdit(self, field_id: str, phase_id: str) -> None:
        """
        Validate if a field can be edited in a given phase.

        :param field_id: str = Field identifier
        :param phase_id: str = Current phase identifier

        :return: None

        :raises FieldPermissionError:
            When operation is not allowed
        :raises RuleNotFoundError:
            When rule is not registered
        """
        try:
            rule: FieldRule = self._registry.getRule(field_id)

            # Block rule has priority
            if rule.blocked_phases and phase_id in rule.blocked_phases:
                self._raisePermissionError(field_id, phase_id, "blocked")

            # Allowed rule acts as whitelist
            if rule.allowed_phases is not None and phase_id not in rule.allowed_phases:
                self._raisePermissionError(field_id, phase_id, "not allowed")

        except Exception as exc:
            if isinstance(exc, (FieldPermissionError, RuleNotFoundError)):
                raise

            raise FieldPermissionError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: validateFieldEdit\n"
                f"Error: {str(exc)}"
            ) from exc

    # ============================================================
    # Helper Methods
    # ============================================================

    def _raisePermissionError(self, field_id: str, phase_id: str, reason: str) -> None:
        """
        Raise a standardized permission error.

        :param field_id: str = Field identifier
        :param phase_id: str = Phase identifier
        :param reason: str = Reason for denial

        :raises FieldPermissionError:
            Always raised
        """
        raise FieldPermissionError(
            f"Class: {self.__class__.__name__}\n"
            f"Method: {inspect.currentframe().f_code.co_name}\n"
            f"Field '{field_id}' cannot be edited in phase '{phase_id}' ({reason})"
        )


# ============================================================
# Example Usage
# ============================================================

if __name__ == "__main__":
    # Simulated dynamic configuration (could come from JSON/YAML/API)
    config_rules: List[Dict] = [
        {
            "field_id": "field_1",
            "allowed_phases": ["phase_a", "phase_b"]
        },
        {
            "field_id": "field_2",
            "blocked_phases": ["phase_c"]
        }
    ]

    factory = FieldRuleFactory()
    registry = FieldRuleRegistry()

    # Load rules dynamically
    for config in config_rules:
        rule = factory.createRule(config)
        registry.registerRule(rule)

    service = FieldPermissionService(registry)

    # Test scenarios
    try:
        print("Valid case:")
        service.validateFieldEdit("field_1", "phase_a")
        print("✔ Allowed")

        print("\nInvalid case:")
        service.validateFieldEdit("field_1", "phase_c")

    except Exception as exc:
        print(f"❌ {str(exc)}")