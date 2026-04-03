class FieldType:
    """
    Defines supported Pipefy field types.

    These values must match the types retrieved from Pipefy metadata.

    :example:
        >>> FieldType.ATTACHMENT
        'attachment'
    """

    ATTACHMENT: str = "attachment"
    SHORT_TEXT: str = "short_text"
    LONG_TEXT: str = "long_text"
    SELECT: str = "select"
    ASSIGNEE: str = "assignee"
    NUMBER: str = "number"
    DATETIME: str = "datetime"
    DUE_DATE: str = "due_date"