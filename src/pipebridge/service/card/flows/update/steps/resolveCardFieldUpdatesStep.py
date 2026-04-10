from pipebridge.exceptions import ValidationError, getExceptionContext
from pipebridge.dispatcher.field.fieldType import FieldType
from pipebridge.service.card.flows.update.context.cardUpdateContext import (
    CardUpdateContext,
)
from pipebridge.service.card.flows.update.dispatcher.cardFieldUpdateDispatcher import (
    CardFieldUpdateDispatcher,
)
from pipebridge.workflow.steps.baseStep import BaseStep


class ResolveCardFieldUpdatesStep(BaseStep):
    """
    Resolve each requested field update using the field dispatcher.
    """

    execution_profile = "local"

    def __init__(self, dispatcher: CardFieldUpdateDispatcher | None = None) -> None:
        """
        Initialize the field-resolution step.

        :param dispatcher: CardFieldUpdateDispatcher | None = Optional dispatcher override
        """
        self._dispatcher = dispatcher or CardFieldUpdateDispatcher()

    def execute(self, context: CardUpdateContext) -> None:
        """
        Resolve each requested field update into a canonical operation.

        :param context: CardUpdateContext = Shared update-flow execution context

        :return: None

        :raises ValidationError:
            When required card or field metadata is unavailable
        """
        class_name, method_name = getExceptionContext(self)

        if context.card is None:
            raise ValidationError(
                message="card must be loaded before resolving field updates",
                class_name=class_name,
                method_name=method_name,
            )

        resolved_operations = []
        for field_id, input_value in context.request.fields.items():
            current_field = context.card.getField(field_id)
            phase_field = context.phase.getField(field_id) if context.phase else None
            field_type = (
                context.phase.getFieldType(field_id) if context.phase else None
            ) or context.card.getFieldType(field_id)

            if not field_type and context.pipe_id is not None:
                pipe_id = context.pipe_id
                pipe = context.pipe_schema_cache.getOrLoad(
                    pipe_id,
                    loader=lambda: context.pipe_service.getPipeFieldCatalog(pipe_id),
                )
                pipe_field = pipe.getField(field_id)
                if pipe_field is not None:
                    field_type = pipe_field.type
                    phase_field = phase_field or pipe_field

            if not field_type:
                raise ValidationError(
                    message=f"Unable to determine field type for '{field_id}'",
                    class_name=class_name,
                    method_name=method_name,
                )

            normalized_input_value = input_value
            if field_type in (FieldType.ASSIGNEE, FieldType.ASSIGNEE_SELECT):
                normalized_input_value = self._resolveAssigneeInput(
                    context=context,
                    field_id=field_id,
                    input_value=input_value,
                    class_name=class_name,
                    method_name=method_name,
                )

            resolved_operations.append(
                self._dispatcher.dispatch(
                    field_id=field_id,
                    field_type=field_type,
                    input_value=normalized_input_value,
                    current_field=current_field,
                    phase_field=phase_field,
                )
            )

        context.resolved_operations = resolved_operations

    @staticmethod
    def _resolveAssigneeInput(
        context: CardUpdateContext,
        field_id: str,
        input_value: object,
        class_name: str,
        method_name: str,
    ) -> list[str]:
        """
        Resolve assignee user references into Pipefy user IDs.

        The flow accepts either a single string or a list of strings. Each
        item can be either a direct user ID already present in the pipe or a
        human-readable user name that must be resolved against the cached pipe
        schema catalog.
        """
        if isinstance(input_value, str):
            requested_values = [input_value]
        elif isinstance(input_value, list) and all(
            isinstance(item, str) for item in input_value
        ):
            requested_values = list(input_value)
        else:
            raise ValidationError(
                message=(
                    f"Assignee field '{field_id}' requires a string or a list "
                    f"of strings representing user IDs or user names"
                ),
                class_name=class_name,
                method_name=method_name,
            )

        if not requested_values:
            return []

        if context.pipe_id is None:
            raise ValidationError(
                message=(
                    f"Unable to resolve assignee values for field '{field_id}' "
                    "because the card pipe_id is unavailable"
                ),
                class_name=class_name,
                method_name=method_name,
            )

        pipe_id = context.pipe_id
        pipe = context.pipe_schema_cache.getOrLoad(
            pipe_id,
            loader=lambda: context.pipe_service.getPipeFieldCatalog(pipe_id),
        )

        resolved_user_ids: list[str] = []
        for requested_value in requested_values:
            if pipe.hasUser(requested_value):
                resolved_user_ids.append(requested_value)
                continue

            user = pipe.getUserByName(requested_value)
            if user is None:
                raise ValidationError(
                    message=(
                        f"User reference '{requested_value}' for field '{field_id}' "
                        f"was not found in pipe '{pipe.id}'"
                    ),
                    class_name=class_name,
                    method_name=method_name,
                )
            resolved_user_ids.append(user.id)

        return resolved_user_ids
