import networkx as nx
import pytest
from pyformlang.cfg import CFG

from flpq_solver.algorithms import MatrixReachabilityAlgorithm


@pytest.fixture(
    scope="function",
    params=[MatrixReachabilityAlgorithm],
    ids=lambda a: a.__name__,
)
def param_algo(request):
    return request.param


def test_no_reachable_vertices(param_algo):
    """
    Test with the result is an empty set of reachable vertices.
    """
    g = nx.MultiDiGraph()
    g.add_edge(0, 1, label="b")
    g.add_edge(1, 2, label="c")
    g.add_edge(2, 0, label="d")

    cfg = CFG.from_text("S -> S S | a")

    algo = param_algo(cfg, g)
    reachable_vertices = algo.solve_all_pairs()

    assert reachable_vertices == set()


def test_worst_case(param_algo):
    """
    The graph is two cycles of coprime lengths with a single common vertex.
    The first cycle is labeled by the open bracket.
    The second cycle is labeled by the close bracket.
    """
    g = nx.MultiDiGraph()
    g.add_edge(0, 1, label="a")
    g.add_edge(1, 2, label="a")
    g.add_edge(2, 0, label="a")
    g.add_edge(0, 3, label="b")
    g.add_edge(3, 0, label="b")

    cfg = CFG.from_text("S -> a S b | a b")

    algo = param_algo(cfg, g)
    reachable_vertices = algo.solve_all_pairs()

    assert reachable_vertices == {(0, 0), (1, 0), (0, 3), (1, 3), (2, 0), (2, 3)}


def test_worst_case_with_graph_vertices_numbering(param_algo):
    """
    The graph is two cycles of coprime lengths with a single common vertex.
    The first cycle is labeled by the open bracket.
    The second cycle is labeled by the close bracket.
    Vertices in the graph are identified by numbers and strings.
    """
    g = nx.MultiDiGraph()
    g.add_edge(-1, 7, label="a")
    g.add_edge(7, 2, label="a")
    g.add_edge(2, -1, label="a")
    g.add_edge(-1, "A", label="b")
    g.add_edge("A", -1, label="b")

    cfg = CFG.from_text("S -> a S b | a b")

    algo = param_algo(cfg, g)
    reachable_vertices = algo.solve_all_pairs()

    assert reachable_vertices == {
        (-1, -1),
        (7, -1),
        (-1, "A"),
        (2, -1),
        (7, "A"),
        (2, "A"),
    }


def test_full_graph_result(param_algo):
    """
    The case when the input graph is sparse, but the result is a full graph.
    Input graph is a cycle, all edges of which are labeled by the same token.
    """
    g = nx.MultiDiGraph()
    g.add_edge(0, 1, label="a")
    g.add_edge(1, 2, label="a")
    g.add_edge(2, 3, label="a")
    g.add_edge(3, 0, label="a")

    cfg = CFG.from_text("S -> S S | a")

    algo = param_algo(cfg, g)
    reachable_vertices = algo.solve_all_pairs()

    assert reachable_vertices == {
        (v, to) for v in range(g.number_of_nodes()) for to in range(g.number_of_nodes())
    }
