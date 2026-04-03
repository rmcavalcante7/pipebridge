# ============================================================
# Dependencies
# ============================================================
from pipefy.exceptions import ValidationError
from pipefy.exceptions.utils import getExceptionContext


class FileDownloadRequest:
    """
    Represents a request to download attachments from a Pipefy card.

    This object encapsulates all required parameters for downloading
    files from a card field.

    DESIGN PURPOSE:
        - Replace primitive parameter passing
        - Provide validation at construction time
        - Improve API consistency with upload flow

    :param card_id: str = Card identifier
    :param field_id: str = Field identifier
    :param output_dir: str = Output directory path

    :raises ValidationError:
        When parameters are invalid

    :example:
        >>> req = FileDownloadRequest("1", "field", "/tmp")
        >>> isinstance(req, FileDownloadRequest)
        True
    """

    def __init__(
        self,
        card_id: str,
        field_id: str,
        output_dir: str
    ) -> None:
        class_name, method_name = getExceptionContext(self)

        if not card_id:
            raise ValidationError("card_id cannot be empty", class_name, method_name)

        if not field_id:
            raise ValidationError("field_id cannot be empty", class_name, method_name)

        if not output_dir:
            raise ValidationError("output_dir cannot be empty", class_name, method_name)

        self.card_id = card_id
        self.field_id = field_id
        self.output_dir = output_dir