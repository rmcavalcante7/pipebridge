"""
GraphQL query builders for phase-related operations.
"""


class PhaseQueries:
    """
    Factory for phase GraphQL queries.

    All methods are deterministic builders that accept the dynamic parameters
    required by the service layer and return a ready-to-send GraphQL string.
    """

    @staticmethod
    def getById(phase_id: str, query_body: str) -> str:
        """
        Build a phase-by-id query.

        :param phase_id: str = Phase identifier
        :param query_body: str = GraphQL fields for the phase selection

        :return: str = GraphQL query
        """
        return f"""
        {{
            phase(id: "{phase_id}") {{
                {query_body}
            }}
        }}
        """
