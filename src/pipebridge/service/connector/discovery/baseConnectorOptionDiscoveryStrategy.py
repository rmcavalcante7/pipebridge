from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from pipebridge.models.connectorFieldSpec import ConnectorFieldSpec
from pipebridge.models.connectorOption import ConnectorOption


class BaseConnectorOptionDiscoveryStrategy(ABC):
    """
    Base class for connector option discovery strategies.
    """

    @abstractmethod
    def supports(self, spec: ConnectorFieldSpec) -> bool:
        """
        Check whether the strategy can handle a connector specification.
        """

    @abstractmethod
    def listOptions(
        self,
        spec: ConnectorFieldSpec,
        search: Optional[str],
        limit: Optional[int],
    ) -> List[ConnectorOption]:
        """
        List dynamic connector options for the provided specification.
        """

    def listOptionsForResolution(
        self,
        spec: ConnectorFieldSpec,
        desired_title: str,
    ) -> List[ConnectorOption]:
        """
        Retrieve options for exact-title resolution.
        """
        return self.listOptions(spec=spec, search=desired_title, limit=None)
