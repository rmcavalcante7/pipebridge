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
    ASSIGNEE_SELECT: str = "assignee_select"
    NUMBER: str = "number"
    CURRENCY: str = "currency"
    EMAIL: str = "email"
    PHONE: str = "phone"
    CPF: str = "cpf"
    CNPJ: str = "cnpj"
    DATETIME: str = "datetime"
    DATE: str = "date"
    TIME: str = "time"
    DUE_DATE: str = "due_date"
    LABEL_SELECT: str = "label_select"
    RADIO_HORIZONTAL: str = "radio_horizontal"
    RADIO_VERTICAL: str = "radio_vertical"
    CHECKLIST_HORIZONTAL: str = "checklist_horizontal"
    CHECKLIST_VERTICAL: str = "checklist_vertical"
    CONNECTOR: str = "connector"
