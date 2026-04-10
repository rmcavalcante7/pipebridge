"""
GraphQL query builders for pipe-related operations.
"""


class PipeQueries:
    """
    Factory for pipe GraphQL queries.

    Each method accepts the dynamic values needed for a query and returns the
    final GraphQL string consumed by the service layer.
    """

    @staticmethod
    def getById(pipe_id: str, query_body: str) -> str:
        """
        Build a pipe-by-id query.

        :param pipe_id: str = Pipe identifier
        :param query_body: str = GraphQL fields for the pipe selection

        :return: str = GraphQL query
        """
        return f"""
        {{
            pipe(id: "{pipe_id}") {{
                {query_body}
            }}
        }}
        """

    @staticmethod
    def getFieldCatalogBody() -> str:
        """
        Build the GraphQL selection body for a pipe field catalog.

        :return: str = GraphQL body
        """
        return """
            id
            name
            cards_count

            organization {
                id
            }

            labels {
                id
                name
                color
            }

            users {
                id
                name
                email
            }

            start_form_fields {
                id
                uuid
                internal_id
                label
                type
                required
                description
                options
            }

            phases {
                id
                name
                fields {
                    id
                    uuid
                    internal_id
                    label
                    type
                    required
                    description
                    options
                }
            }
        """

    @staticmethod
    def getFieldCatalog(pipe_id: str) -> str:
        """
        Build a pipe field-catalog query.

        :param pipe_id: str = Pipe identifier

        :return: str = GraphQL query
        """
        return PipeQueries.getById(
            pipe_id=pipe_id, query_body=PipeQueries.getFieldCatalogBody()
        )
