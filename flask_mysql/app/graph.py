from app import db_query
import pandas as pd
import networkx as nx
from networkx.readwrite import json_graph


# get graph by year
def generate_graph(min_year, max_year):

    # get articles
    df_paper, n = db_query.get_article_by_year(min_year, max_year)
    ids = df_paper['id'].tolist()
    
    # get citations
    df_citation, n = db_query.get_citations_apmid(ids)

    # build graph
    l_ = df_citation.values.tolist()
    G = nx.Graph()
    G.add_edges_from(l_)

    jsonData = json_graph.node_link_data(G)
    return jsonData, n