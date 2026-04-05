# ============================================================
# Dependencies
# ============================================================
from typing import Dict

from pipebridge.workflow.context.executionContext import ExecutionContext
from pipebridge.workflow.policies.baseExecutionPolicy import BaseExecutionPolicy
from pipebridge.workflow.policies.noOpExecutionPolicy import NoOpExecutionPolicy
from pipebridge.workflow.policies.policyResolver import PolicyResolver
from pipebridge.workflow.steps.baseStep import BaseStep


class ProfilePolicyResolver(PolicyResolver):
    """
    Resolves policies based on step execution profile.

    This resolver allows multiple step types to share the same policy
    configuration by declaring the same ``execution_profile``.

    :param policies_by_profile: Dict[str, BaseExecutionPolicy] = Policy mapping by profile
    :param default_policy: BaseExecutionPolicy | None = Fallback policy

    :example:
        >>> resolver = ProfilePolicyResolver({})
        >>> isinstance(resolver, ProfilePolicyResolver)
        True
    """

    def __init__(
        self,
        policies_by_profile: Dict[str, BaseExecutionPolicy],
        default_policy: BaseExecutionPolicy | None = None,
    ) -> None:
        """
        Initialize ProfilePolicyResolver.

        :param policies_by_profile: Dict[str, BaseExecutionPolicy] = Policy mapping by profile
        :param default_policy: BaseExecutionPolicy | None = Fallback policy

        :return: None

        :example:
            >>> resolver = ProfilePolicyResolver({})
            >>> isinstance(resolver, ProfilePolicyResolver)
            True
        """
        self._policies_by_profile: Dict[str, BaseExecutionPolicy] = (
            policies_by_profile or {}
        )
        self._default_policy: BaseExecutionPolicy = (
            default_policy or NoOpExecutionPolicy()
        )

    def resolve(self, step: BaseStep, context: ExecutionContext) -> BaseExecutionPolicy:
        """
        Resolve policy based on step execution profile.

        :param step: BaseStep = Step being executed
        :param context: ExecutionContext = Shared workflow context

        :return: BaseExecutionPolicy = Resolved policy

        :example:
            >>> class ExampleStep(BaseStep):
            ...     execution_profile = "network"
            ...     def execute(self, context):
            ...         return None
            >>> resolver = ProfilePolicyResolver({})
            >>> resolver.resolve(ExampleStep(), ExecutionContext()).__class__.__name__
            'NoOpExecutionPolicy'
        """
        profile = getattr(step, "execution_profile", "default")
        return self._policies_by_profile.get(profile, self._default_policy)
