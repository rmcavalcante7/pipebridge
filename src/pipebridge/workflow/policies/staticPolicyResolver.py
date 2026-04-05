# ============================================================
# Dependencies
# ============================================================
from pipebridge.workflow.context.executionContext import ExecutionContext
from pipebridge.workflow.policies.baseExecutionPolicy import BaseExecutionPolicy
from pipebridge.workflow.policies.noOpExecutionPolicy import NoOpExecutionPolicy
from pipebridge.workflow.policies.policyResolver import PolicyResolver
from pipebridge.workflow.steps.baseStep import BaseStep


class StaticPolicyResolver(PolicyResolver):
    """
    Resolver that always returns the same execution policy.

    :param policy: BaseExecutionPolicy | None = Policy shared by all steps

    :example:
        >>> resolver = StaticPolicyResolver()
        >>> isinstance(resolver, StaticPolicyResolver)
        True
    """

    def __init__(self, policy: BaseExecutionPolicy | None = None) -> None:
        """
        Initialize StaticPolicyResolver.

        :param policy: BaseExecutionPolicy | None = Policy shared by all steps

        :return: None

        :example:
            >>> resolver = StaticPolicyResolver()
            >>> isinstance(resolver, StaticPolicyResolver)
            True
        """
        self._policy: BaseExecutionPolicy = policy or NoOpExecutionPolicy()

    def resolve(self, step: BaseStep, context: ExecutionContext) -> BaseExecutionPolicy:
        """
        Return the same policy for all steps.

        :param step: BaseStep = Step being executed
        :param context: ExecutionContext = Shared workflow context

        :return: BaseExecutionPolicy = Shared policy

        :example:
            >>> class ExampleStep(BaseStep):
            ...     def execute(self, context):
            ...         return None
            >>> resolver = StaticPolicyResolver()
            >>> resolver.resolve(ExampleStep(), ExecutionContext()).__class__.__name__
            'NoOpExecutionPolicy'
        """
        return self._policy
