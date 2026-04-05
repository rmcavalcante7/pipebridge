"""
GraphQL mutation builders for card-related operations.
"""

import json
from typing import Any, Optional


class CardMutations:
    """
    Factory for card GraphQL mutations.

    Methods accept dynamic values and return ready-to-send GraphQL mutations.
    """

    @staticmethod
    def createCard(
        pipe_id: str, title: str, fields_payload: list[dict[str, Any]]
    ) -> str:
        """
        Build the mutation that creates a new card.

        :param pipe_id: str = Pipe identifier
        :param title: str = Card title
        :param fields_payload: list[dict[str, Any]] = Initial field payload

        :return: str = GraphQL mutation
        """
        return f"""
        mutation {{
            createCard(input: {{
                pipe_id: {pipe_id},
                title: "{title}",
                fields_attributes: {json.dumps(fields_payload)}
            }}) {{
                card {{
                    id
                    title
                }}
            }}
        }}
        """

    @staticmethod
    def moveToPhase(card_id: str, phase_id: str) -> str:
        """
        Build the mutation that moves a card to another phase.

        :param card_id: str = Card identifier
        :param phase_id: str = Destination phase identifier

        :return: str = GraphQL mutation
        """
        return f"""
        mutation {{
            moveCardToPhase(input: {{
                card_id: {card_id},
                destination_phase_id: {phase_id}
            }}) {{
                card {{
                    id
                }}
            }}
        }}
        """

    @staticmethod
    def createRelation(parent_id: str, child_id: str, source_id: str) -> str:
        """
        Build the mutation that creates a card relation.

        :param parent_id: str = Parent card identifier
        :param child_id: str = Child card identifier
        :param source_id: str = Relation source identifier

        :return: str = GraphQL mutation
        """
        return f"""
        mutation {{
            createCardRelation(input: {{
                parentId: {parent_id},
                childId: {child_id},
                sourceId: {source_id},
                sourceType: "PipeRelation"
            }}) {{
                cardRelation {{
                    id
                }}
            }}
        }}
        """

    @staticmethod
    def deleteCard(card_id: str) -> str:
        """
        Build the mutation that deletes a card.

        :param card_id: str = Card identifier

        :return: str = GraphQL mutation
        """
        return f"""
        mutation {{
            deleteCard(input: {{ id: {card_id} }}) {{
                success
            }}
        }}
        """

    @staticmethod
    def updateAssigneeIds(card_id: str, assignee_ids: list[str]) -> str:
        """
        Build the mutation that updates card assignee identifiers.

        :param card_id: str = Card identifier
        :param assignee_ids: list[str] = Assignee identifiers

        :return: str = GraphQL mutation
        """
        return f"""
        mutation {{
            updateCard(input: {{
                id: {card_id},
                assignee_ids: {json.dumps(assignee_ids)}
            }}) {{
                card {{
                    id
                    title
                }}
            }}
        }}
        """

    @staticmethod
    def updateLabelIds(card_id: str, label_ids: list[str]) -> str:
        """
        Build the mutation that updates card label identifiers.

        :param card_id: str = Card identifier
        :param label_ids: list[str] = Label identifiers

        :return: str = GraphQL mutation
        """
        return f"""
        mutation {{
            updateCard(input: {{
                id: {card_id},
                label_ids: {json.dumps(label_ids)}
            }}) {{
                card {{
                    id
                    title
                }}
            }}
        }}
        """

    @staticmethod
    def updateCardField(card_id: str, field_id: str, value: Any) -> str:
        """
        Build the generic card field update mutation.

        :param card_id: str = Card identifier
        :param field_id: str = Logical field identifier
        :param value: Any = Final field value to be applied

        :return: str = GraphQL mutation
        """
        serialized_value = CardMutations._toGraphQLLiteral(value)
        return f"""
        mutation {{
          updateCardField(input: {{
            card_id: "{card_id}",
            field_id: "{field_id}",
            new_value: {serialized_value}
          }}) {{
            success
            card {{
              id
            }}
          }}
        }}
        """

    @staticmethod
    def _toGraphQLLiteral(value: Any) -> str:
        if isinstance(value, str):
            return json.dumps(value)
        if isinstance(value, bool):
            return "true" if value else "false"
        if value is None:
            return "null"
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, (list, dict)):
            return json.dumps(value)
        return json.dumps(str(value))

    @staticmethod
    def updateCardAttachmentFieldValue(
        card_id: str, field_uuid: str, urls: list[str]
    ) -> str:
        """
        Build the attachment-specific card field update mutation.

        :param card_id: str = Card identifier
        :param field_uuid: str = Attachment field UUID
        :param urls: list[str] = Final attachment URL list

        :return: str = GraphQL mutation
        """
        urls_str = str(urls).replace("'", '"')
        return f"""
        mutation {{
          updateCardAttachmentFieldValue(
            input: {{
              cardId: "{card_id}"
              fieldId: "{field_uuid}"
              value: {urls_str}
            }}
          ) {{
            field {{
              id
            }}
          }}
        }}
        """
