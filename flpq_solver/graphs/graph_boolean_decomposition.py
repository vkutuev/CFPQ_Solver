"""Module contains base class for a Labeled Graph decomposed into Boolean Matrices."""

from typing import Hashable

import networkx as nx
from graphblas import Matrix
from graphblas.dtypes import BOOL


__all__ = [
    "GraphBooleanDecomposition",
    "gbd_from_nx_graph",
]


class GraphBooleanDecomposition:
    """A Labeled Graph decomposed into Boolean Matrices."""

    def __init__(self, n: int = 0):
        """Initialize a Labeled Graph decomposed into `n` x `n` Boolean Matrices.

        :param n: The number of nodes in graph.
        """
        self._matrices: dict[str, Matrix] = dict()
        self._matrices_size: int = n

    def __getitem__(self, label: str) -> Matrix:
        if label not in self._matrices:
            raise KeyError(f"{label}")
        return self._matrices[label]

    def __setitem__(self, label: str, matrix: Matrix) -> None:
        self._matrices[label] = matrix

    def __contains__(self, label: str) -> bool:
        return label in self._matrices

    @property
    def matrices_size(self) -> int:
        """The number of vertices in the graph."""
        return self._matrices_size

    def add_edge(self, u: int, v: int, label: str) -> None:
        """Add an edge between `u` and `v` with label `label`.

        # The nodes `u` and `v` will be automatically added if they are not already in the graph.
        *Note:* If `u` or `v` is greater than `self.matrices_size` the matrices will be resized.

        :param u: The tail of the edge
        :param v: The head of the edge
        :param label: The label of the edge
        """
        if min(u, v) > self._matrices_size:
            for label in self._matrices:
                self._matrices_size = max(u, v)
                self._matrices[label].resize(self._matrices_size, self._matrices_size)

        if label not in self._matrices:
            self._matrices[label] = Matrix(
                dtype=BOOL, nrows=self._matrices_size, ncols=self._matrices_size
            )

        self._matrices[label][u, v] = True


def gbd_from_nx_graph(
    graph: nx.MultiDiGraph,
) -> tuple[GraphBooleanDecomposition, list[Hashable]]:
    """Create a GraphBooleanDecomposition from NetworkX MultiDiGraph.

    Each edge of the `graph` is expected to have a "label" attribute

    :param graph: The graph represented NetworkX MultiDiGraph
    :return: `(g, nodes_mapping)` where `g` — constructed GraphBooleanDecomposition,
        `nodes_mapping` — mapping matrix index to a `graph` node
    """
    g = GraphBooleanDecomposition(graph.number_of_nodes())

    nodes_dict = dict()
    nodes_list = []
    nodes_num = 0

    for node in graph:
        if node not in nodes_dict:
            nodes_dict[node] = nodes_num
            nodes_num += 1
            nodes_list.append(node)

    for u, v, edge in graph.edges(data=True):
        u = nodes_dict[u]
        v = nodes_dict[v]
        label = edge["label"]

        g.add_edge(u, v, label)

    return g, nodes_list
