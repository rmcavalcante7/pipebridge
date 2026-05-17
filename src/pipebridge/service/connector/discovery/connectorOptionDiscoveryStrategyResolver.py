from __future__ import annotations

from typing import List

from pipebridge.exceptions import ValidationError
from pipebridge.models.connectorFieldSpec import ConnectorFieldSpec
from pipebridge.service.connector.discovery.baseConnectorOptionDiscoveryStrategy import (
    BaseConnectorOptionDiscoveryStrategy,
)


class ConnectorOptionDiscoveryStrategyResolver:
    """
    Resolve the concrete discovery strategy for a connector field.
    """

    def __init__(self, strategies: List[BaseConnectorOptionDiscoveryStrategy]) -> None:
        self._strategies = list(strategies)

    def resolve(self, spec: ConnectorFieldSpec) -> BaseConnectorOptionDiscoveryStrategy:
        for strategy in self._strategies:
            if strategy.supports(spec):
                return strategy

        raise ValidationError(
            message=(
                f"No connector discovery strategy is registered for field "
                f"'{spec.field_id}'"
            ),
            class_name=self.__class__.__name__,
            method_name="resolve",
        )
