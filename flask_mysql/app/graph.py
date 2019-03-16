from app import db_query
import pandas as pd
import networkx as nx
from networkx.readwrite import json_graph


def generate_graph(min_year, max_year, min_cite, max_cite, rank_var='none'):
    '''get graph by year'''

    # get articles within year range
    df_paper_yr, n = db_query.get_id_by_year(min_year, max_year)
    ids_yr = df_paper_yr['id'].tolist()

    # get articles within income citation range
    df_paper_ct, n = db_query.get_id_by_incoming_count(min_cite, max_cite)
    ids_ct = df_paper_ct['id'].tolist()

    # get citations
    ids = list(set(ids_yr + ids_ct))
    df_citation_out, n = db_query.get_citations_by_id(ids, id_type='from')
    df_citation_in, n = db_query.get_citations_by_id(ids, id_type='to')
    df_citation = pd.concat([df_citation_in, df_citation_out], ignore_index=True)

    # build graph
    l_ = df_citation.values.tolist()
    G = nx.Graph()
    G.add_edges_from(l_)

    # add rank
    if rank_var != 'none':
        # use page rank
        if rank_var == 'pagerank':
            rnk_dict = nx.pagerank(G)
            df_rnk = pd.DataFrame([rnk_dict], index=[rank_var]).T
        # use citation count
        if rank_var == 'citations':
            df_rnk = df_paper_ct.copy()
        df_rnk['rank'] = df_rnk[rank_var].rank(method='dense', ascending=False)
        df_rnk = df_rnk.reset_index().rename(columns={'index':'id'})
        dict_rnk = df_rnk[['id', 'rank']].to_dict(orient='records')        

    # export graph to json
    jsonData = json_graph.node_link_data(G)
    if dict_rnk:
        # add rank to nodes
        jsonData['nodes'] = dict_rnk 
    # print(jsonData)
    return jsonData, len(l_)
