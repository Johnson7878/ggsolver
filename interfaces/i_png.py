"""
Implements to_png for Graph.

Define all fancy coloring etc.
"""

from ggsolver.graph import Graph
import networkx as nx


def to_png(graph, fpath, nlabel=None, elabel=None):
    """
    Generates a PNG image of the graph.

    :param graph: (Graph instance) Graph to be saved as PNG.
    :param fpath: (str) Path to which the file should be saved. Must include an extension.
    :param nlabel: (list of str) Specifies the node properties to use to annotate a node in image.
    :param elabel: (list of str) Specifies the edge properties to use to annotate an edge in image.

    :warning: If the node labels are not unique, the generated figure may contain 0, 1, 2, ...
        that avoid duplication.
    """
    max_nodes = 500
    if graph.number_of_nodes() > max_nodes:
        raise ValueError(f"Cannot draw a graph with more than {max_nodes} nodes.")

    g = graph

    # If node properties to displayed are specified, process them.
    if nlabel is not None:
        g = nx.MultiDiGraph()

        # If more than one property is selected, then display as tuple.
        if len(nlabel) == 1:
            node_state_map = {n: graph[prop][n] for prop in nlabel for n in graph.nodes()}
        else:
            node_state_map = {n: tuple(graph[prop][n] for prop in nlabel) for n in graph.nodes()}

        # Add nodes to dummy graph
        for n in node_state_map.values():
            g.add_node(str(n))

        # If edge labels to be displayed are specified, process them.
        if elabel is not None:
            for u, v, k in graph.edges():
                if len(elabel) == 1:
                    g.add_edge(str(node_state_map[u]), str(node_state_map[v]),
                               label=graph[elabel[0]][(u, v, k)])
                else:
                    g.add_edge(str(node_state_map[u]), str(node_state_map[v]),
                               label=tuple(graph[prop][(u, v, k)] for prop in elabel))
        else:
            for u, v, k in graph.edges(keys=True):
                g.add_edge(str(node_state_map[u]), str(node_state_map[v]))

    # If edge labels to be displayed are specified, process them.
    if elabel is not None:
        for u, v, k in graph.edges():
            if len(elabel) == 1:
                g.add_edge(u, v, label=graph[elabel[0]][(u, v, k)])
            else:
                g.add_edge(u, v, label=tuple(graph[prop][(u, v, k)] for prop in elabel))
    
    dot_graph = nx.nx_agraph.to_agraph(g)
    dot_graph.layout("dot")
    dot_graph.draw(fpath)

