# Web Mining Project Team 7
# Paper Importance Prediction

# Feature Engineering: graph based features

# setting up path
import sys
from os.path import join, dirname
from os import pardir
sys.path.insert(1, join(pardir, "data"))
sys.path.insert(1, join(pardir, pardir, "data", "processed"))

import datetime

# reading graph and dataframe
from graphio import read_graph
import pandas as pd
G = read_graph("hep-th-citations_unzipped.txt", "hep-th-slacdates_unzipped.txt")
df = pd.read_csv("../../data/processed/metadata.csv")

# functions to create feature (paper-id -> feature)
def impo_sum(x) -> int:
    s = 0  # count number of cites of cited papers
    if x not in G.nodes:
        return 0
    cited = G[x]
    current_time = G.nodes[x]["time"]
    for paper in cited:
        for a,_ in G.in_edges(paper):
            if a == x:
                continue
            if a in G.nodes and G.nodes[a]["time"] <= current_time:
                s +=1
    return s

def impo_avg(x) -> float:
    s = 0  # count number of cites of cited papers
    if x not in G.nodes:
        return 0
    cited = G[x]
    if len(cited) == 0:
        return 0
    current_time = G.nodes[x]["time"]
    for paper in cited:
        for a,_ in G.in_edges(paper):
            if a == x:
                continue
            if a in G.nodes and G.nodes[a]["time"] <= current_time:
                s +=1
    return s*1.0 / len(cited)

def rec_avg(x):
    if x not in G.nodes:
        return None
    cited = G[x]
    nr_cited = len(cited)
    sum_time_deltas = datetime.timedelta()
    if nr_cited == 0:
        return None
    current_time = G.nodes[x]["time"]
    for paper in cited:
        if paper in G.nodes:
            sum_time_deltas += (current_time-G.nodes[paper]["time"])
    return (sum_time_deltas.days *1.0) / nr_cited


def dif_max(x):
    if x not in G.nodes:
        return None
    cited = [a for a in list(G[x]) if a in G.nodes]  # filter citations, that are in citation graph
    if len(cited)==0:
        return None
    ma = mi = G.nodes[cited[0]]["time"]
    for paper in cited:
        ma = max(ma, G.nodes[paper]["time"])
        mi = min(mi, G.nodes[paper]["time"])
    return (ma-mi).days


# modifying dataframe / adding features
df["paper_id"] = df["paper_id"].apply(lambda x: int(x.split("/")[1]))

"""outdegree (if paper not in graph use 0)"""
df["outdegree"] = df["paper_id"].apply(lambda x: len(G[x]) if x in G.nodes else 0)

"""how many cites do the cited papers have together """
df["importance_of_cited_papers(sum)"] = df["paper_id"].apply(lambda x: impo_sum(x))

"""how many cites do the cited papers have on average """
df["importance_of_cited_papers(avg)"] = df["paper_id"].apply(lambda x: impo_avg(x))

"""average recency of cited papers """
df["recency(avg)"] = df["paper_id"].apply(lambda x: rec_avg(x))

"""Maximum time difference between cited papers"""
df["max_time_diff_cit"] = df["paper_id"].apply(lambda x: dif_max(x))
