# ============================================================
# Dependencies
# ============================================================
from typing import Any, Dict, Generic, List, Optional, TypeVar, Callable

from pipefy.models.base import BaseModel
from pipefy.exceptions import ParsingError

T = TypeVar("T")


class PageInfo(BaseModel):
    """
    Represents GraphQL pagination metadata.
    """

    def __init__(
        self,
        hasNextPage: bool,
        endCursor: Optional[str] = None
    ) -> None:
        """
        Initialize PageInfo.

        :param hasNextPage: bool = Indicates if there are more pages
        :param endCursor: str | None = Cursor for the next page
        """
        self.hasNextPage: bool = hasNextPage
        self.endCursor: Optional[str] = endCursor

    @classmethod
    def fromDict(cls, data: Dict[str, Any]) -> "PageInfo":
        """
        Create PageInfo instance from dictionary.

        :param data: dict = Raw pageInfo data from API

        :return: PageInfo = Parsed PageInfo instance

        :raises ParsingError:
            When data is not a valid dictionary
        """
        if not isinstance(data, dict):
            raise ParsingError("Invalid pageInfo structure")

        return cls(
            hasNextPage=data.get("hasNextPage", False),
            endCursor=data.get("endCursor")
        )


class Edge(Generic[T]):
    """
    Represents a GraphQL edge.
    """

    def __init__(self, node: T) -> None:
        """
        Initialize Edge.

        :param node: T = Node contained in the edge
        """
        self.node: T = node

    @classmethod
    def fromDict(
        cls,
        data: Dict[str, Any],
        node_parser: Callable[[Any], T]
    ) -> "Edge[T]":
        """
        Create Edge instance from dictionary.

        :param data: dict = Raw edge data from API
        :param node_parser: callable = Function to parse node into target type

        :return: Edge[T] = Parsed edge instance

        :raises ParsingError:
            When data is not valid or node parsing fails
        """
        if not isinstance(data, dict):
            raise ParsingError("Invalid edge structure")

        node_data = data.get("node")

        try:
            node = node_parser(node_data)
        except Exception as exc:
            raise ParsingError(f"Failed to parse node: {str(exc)}") from exc

        return cls(node)


class PaginatedResponse(Generic[T]):
    """
    Represents a paginated GraphQL response.
    """

    def __init__(
        self,
        edges: List[Edge[T]],
        page_info: PageInfo
    ) -> None:
        """
        Initialize PaginatedResponse.

        :param edges: list[Edge[T]] = List of edges
        :param page_info: PageInfo = Pagination metadata
        """
        self.edges: List[Edge[T]] = edges
        self.page_info: PageInfo = page_info

    def nodes(self) -> List[T]:
        """
        Extract nodes from edges.

        :return: list[T] = List of nodes extracted from edges
        """
        return [edge.node for edge in self.edges]

    @classmethod
    def fromDict(
        cls,
        data: Dict[str, Any],
        node_parser: Callable[[Any], T]
    ) -> "PaginatedResponse[T]":
        """
        Create PaginatedResponse from dictionary.

        :param data: dict = Raw pagination data from API
        :param node_parser: callable = Function to parse node into target type

        :return: PaginatedResponse[T] = Parsed paginated response

        :raises ParsingError:
            When structure is invalid or parsing fails
        """
        if not isinstance(data, dict):
            raise ParsingError("Invalid paginated response structure")

        page_info_data = data.get("pageInfo")
        edges_data = data.get("edges")

        if not isinstance(page_info_data, dict):
            raise ParsingError("Missing or invalid pageInfo")

        if not isinstance(edges_data, list):
            raise ParsingError("Missing or invalid edges")

        page_info = PageInfo.fromDict(page_info_data)

        edges = [
            Edge.fromDict(edge, node_parser)
            for edge in edges_data
            if isinstance(edge, dict)
        ]

        return cls(edges, page_info)


# ============================================================
# Main (Usage Example)
# ============================================================
if __name__ == "__main__":
    example_data = {
        "pageInfo": {"hasNextPage": False, "endCursor": None},
        "edges": [{"node": {"id": "1"}}]
    }

    def mockParser(data: Dict[str, Any]) -> Dict[str, Any]:
        return data

    try:
        paginated = PaginatedResponse.fromDict(example_data, mockParser)
        print(paginated.nodes())
    except Exception as error:
        print(error)