# Web Mining Project Team 7
# Paper Importance Prediction
# graphio file

import networkx as nx
from datetime import date

from os.path import join, dirname
from os import pardir
directory = join(join(dirname(__file__), pardir), pardir)
datadir = join(join(directory, "data"), "raw")


def read_graph(file : str, file_times : str = None ) -> nx.DiGraph:
    G = nx.DiGraph()  # create empty directed graph
    print("loading Graph...")
    with open(join(datadir, file)) as file:
        lines = file.readlines()
        lines = [line.split() for line in lines]  # split lines by whitespace
        edges = [(int(l1), int(l2)) for [l1, l2] in lines]  # change to int
    G.add_edges_from(edges)

    if file_times:
        with open(join(datadir, file_times)) as file:
            lines = file.readlines()
            lines = [line.split() for line in lines]  # split lines by whitespace
            lines = [(int(node), date.fromisoformat(time)) for [node, time] in lines]  # change to int and date
            nr = 0  # counter for unused dates
            for node, time in lines:
                if node in G.nodes:
                    G.nodes[node]["time"] = time  # create attribute "time" for each node
                else:
                    nr += 1
            # print(f"{nr} dates not used.")

    print("Graph loaded.")
    return G


if __name__ == "__main__":  # is True iff you start the execution with this file
    G = read_graph("hep-th-citations_unzipped.txt", "hep-th-slacdates_unzipped.txt")
    # test some properties:
    assert G.number_of_nodes() == 27_770, "Number of Nodes does not fit."
    assert G.number_of_edges() == 352_807, "Number of Edges does not fit."
    if True:
        for u in G.nodes:  # check that all nodes have a time
            assert len(G.nodes[u]) == 1, f"Number of attributes does not fit for node {u}"
        nr = 0  # counter for future citations
        for u,v in G.edges():
            if G.nodes[u]["time"] < G.nodes[v]["time"]:
                # print(f"Paper {u} cites paper {v} thats in the future")
                nr += 1
        print(f"{nr} future citations")
