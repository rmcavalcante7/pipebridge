from dataclasses import dataclass
from typing import Any, Optional

from pipebridge.models.field import Field
from pipebridge.models.phaseField import PhaseField


@dataclass
class ResolvedFieldUpdate:
    """
    Resolved field update ready to be applied to Pipefy.
    """

    field_id: str
    field_type: str
    input_value: Any
    current_field: Optional[Field]
    phase_field: Optional[PhaseField]
    new_value: Any
