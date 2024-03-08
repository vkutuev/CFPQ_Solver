from collections import defaultdict
from typing import Hashable

import graphblas as gb
import networkx as nx
from graphblas import Matrix
from graphblas.monoid import TypedBuiltinMonoid
from graphblas.semiring import TypedBuiltinSemiring
from graphblas.dtypes import BOOL
from graphblas.semiring import any_pair
from pyformlang.cfg import CFG

from .algorithms import AllPairsReachabilityAlgorithm
from ..grammars import WCNF
from ..graphs import GraphBooleanDecomposition, gbd_from_nx_graph


class MatrixReachabilityAlgorithm(AllPairsReachabilityAlgorithm):
    _wcnf: WCNF
    _matrix_graph: GraphBooleanDecomposition
    _t: GraphBooleanDecomposition
    _nodes_mapping: list[Hashable]
    _all_pairs_solved: bool

    def __init__(self, grammar: CFG, graph: nx.MultiDiGraph):
        # prepare WCNF from GFG
        self._wcnf = WCNF(grammar)
        # prepare GraphBooleanDecomposition from nx.MultiDiGraph
        self._matrix_graph, self._nodes_mapping = gbd_from_nx_graph(graph)
        self._all_pairs_solved = False

    def solve_all_pairs(self) -> set[tuple[Hashable, Hashable]]:
        # if the `graph` is empty, then the answer is empty
        # if graph.number_of_nodes() == 0:
        #     return set()

        if not self._all_pairs_solved:
            # find transitive closure for each non-terminal of `wcnf`
            self._solve_all_pairs()
            self._all_pairs_solved = True

        # convert transitive closure for `wcnf.start_variable`
        # to set of pairs of nodes of `graph`
        rows, cols, _ = self._t[self._wcnf.start_variable.to_text()].to_coo()
        return set(
            (self._nodes_mapping[u], self._nodes_mapping[v]) for u, v in zip(rows, cols)
        )

    def _solve_all_pairs(self) -> None:
        graph = self._matrix_graph
        grammar = self._wcnf
        any_pair_bool: TypedBuiltinSemiring = any_pair[bool]
        any_bool: TypedBuiltinMonoid = any_pair_bool.monoid

        # Initialize matrices for variables
        self._t = GraphBooleanDecomposition(graph.matrices_size)
        for variable in grammar.variables:
            self._t[variable.to_text()] = gb.Matrix(
                BOOL, nrows=graph.matrices_size, ncols=graph.matrices_size
            )

        # 0. Variable -> Epsilon
        id_indices = list(range(graph.matrices_size))
        m_id = Matrix.from_coo(
            rows=id_indices,
            columns=id_indices,
            values=True,
            dtype=BOOL,
            nrows=graph.matrices_size,
            ncols=graph.matrices_size,
        )
        for rule in grammar.epsilon_productions:
            self._t[rule.head.to_text()] = m_id.dup()

        # 1. Variable -> Terminal
        for rule in grammar.unary_productions:
            terminal = rule.body[0].to_text()
            if terminal in graph:
                self._t[rule.head.to_text()] << any_bool.binaryop(
                    self._t[rule.head.to_text()] | graph[terminal]
                )

        # 2. Transitive closure calculation
        nnz = defaultdict(int)

        changed = True
        while changed:
            changed = False
            for rule in grammar.binary_productions:
                l, r1, r2 = (
                    rule.head.to_text(),
                    rule.body[0].to_text(),
                    rule.body[1].to_text(),
                )

                self._t[l](accum=any_bool.binaryop) << any_pair_bool(
                    self._t[r1] @ self._t[r2]
                )

                new_nnz = self._t[l].nvals
                changed |= nnz[l] != new_nnz
                nnz[l] = new_nnz
