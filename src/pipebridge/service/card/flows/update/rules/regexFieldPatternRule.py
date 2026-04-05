import re
from typing import Mapping, Pattern

from pipebridge.exceptions import ValidationError, getExceptionContext
from pipebridge.service.card.flows.update.context.cardUpdateContext import (
    CardUpdateContext,
)
from pipebridge.workflow.rules.baseRule import BaseRule


class RegexFieldPatternRule(BaseRule):
    """
    Validate selected fields against user-provided regex patterns.

    This offers a lightweight extension point for consumers that want custom
    field validation without creating a dedicated rule class.
    """

    def __init__(
        self,
        patterns: Mapping[str, str | Pattern[str]],
        priority: int = 50,
    ) -> None:
        """
        Initialize regex-driven custom validation rule.

        :param patterns: Mapping[str, str | Pattern[str]] = Regex patterns keyed
            by logical field ID
        :param priority: int = Rule execution priority inside the rule engine
        """
        self.priority = priority
        self._patterns = {
            field_id: re.compile(pattern) if isinstance(pattern, str) else pattern
            for field_id, pattern in patterns.items()
        }

    def execute(self, context: CardUpdateContext) -> None:
        """
        Validate configured field values against custom regex patterns.

        :param context: CardUpdateContext = Shared update-flow execution context

        :return: None

        :raises ValidationError:
            When a field value does not match its configured regex pattern
        """
        class_name, method_name = getExceptionContext(self)

        for field_id, pattern in self._patterns.items():
            if field_id not in context.request.fields:
                continue

            value = context.request.fields[field_id]
            if not isinstance(value, str) or not pattern.fullmatch(value):
                raise ValidationError(
                    message=(
                        f"Field '{field_id}' does not match the configured regex pattern. "
                        f"Received value: '{value}'"
                    ),
                    class_name=class_name,
                    method_name=method_name,
                )
