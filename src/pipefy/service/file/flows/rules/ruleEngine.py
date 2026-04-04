# ============================================================
# Dependencies
# ============================================================
from typing import List

from pipefy.service.file.flows.rules.baseRule import BaseRule
from pipefy.service.file.flows.pipeline.uploadPipelineContext import UploadPipelineContext


class RuleEngine:
    """
    Executes a collection of validation rules.

    This class is responsible for orchestrating rule execution
    before the upload pipeline is executed.

    DESIGN PRINCIPLES:
        - Rules are independent
        - Execution order is deterministic
        - Fail-fast behavior

    :param rules: list[BaseRule]

    :example:
        >>> callable(RuleEngine.execute)
        True
    """
    def __str__(self) -> str:
        return f"<RuleEngine rules={len(self._rules)}>"

    def __repr__(self) -> str:
        return f"<RuleEngine(rules={self._rules})>"

    def __init__(self, rules: List[BaseRule]) -> None:
        """
        Initializes RuleEngine.

        :param rules: list[BaseRule]
        :attribute priority: int = Execution priority (lower runs first)
        """
        self._rules = sorted(
            rules or [],
            key=lambda rule: rule.priority
        )

    def execute(self, context: UploadPipelineContext) -> None:
        """
        Executes all rules sequentially.

        :param context: UploadPipelineContext

        :return: None

        :raises ValidationError:
            When any rule fails
        """
        for rule in self._rules:
            print(f"Executing rule: {rule}")
            rule.execute(context)