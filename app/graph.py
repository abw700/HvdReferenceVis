from app import db_query, models
import pandas as pd
import networkx as nx
from networkx.readwrite import json_graph
import time


def generate_graph_outgoing_citations(starting_pmid, citation_depth, rank_var='citations'):
    ''' GET graph a number of depth CITATIONs away, '''

    # get both incoming and outgoing citations from starting_pmid
    df = db_query.get_network_by_id([starting_pmid], citation_depth)

    # build graph
    l_ = df[['apmid', 'bpmid']].values.tolist()
    G = nx.Graph()
    G.add_edges_from(l_)
    df_rnk = get_rank(G, rank_var)

    # add node metadata
    for n in G:
        # label node with the degree level (i.e. 0 = start node, 1 = first depth layer, -1 = first depth layer)
        # if starting node, then degree = 0
        if n == starting_pmid:
            G.node[n]['degree'] = 0
        # if citing the starting node, then degree = -1,-2,-3...
        elif len(df[df['apmid'] == n]['depth']) > 0:
            G.node[n]['degree'] = -int(df[df['apmid'] == n]['depth'].min())
        # else, degree = 1,2,3...
        else:
            G.node[n]['degree'] = int(df[df['bpmid'] == n]['depth'].min())

        # create int variable that tells us rank of each node (compared with all nodes returned)
        G.node[n]['rank'] = df_rnk[df_rnk['id'] == n]['rank'].values[0]

    # export graph to json
    jsonData = json_graph.node_link_data(G)
    return jsonData, len(l_)


def generate_graph_title_keyword(title_search, keyword_search, citation_depth, min_year, max_year, min_cite, max_cite, rank_var='citations', cutoff=0.3):
    '''GET graph by year'''

    t0 = time.time()
    # GET articles with the search title and keyword parameters
    title_search = title_search.replace("'", "")
    keyword_search = keyword_search.replace("'", "")
    
    # flag exact title phrase search
    if title_search.startswith('"'):
        # if exact title phrase search, ignore min_cite 
        min_cite = 1
        pass
    else: 
        # try exact title first
        title_search = '"' + title_search + '"'
    exact_title = True
    df_paper_title_kw, n = db_query.get_ids_by_title_keyword(
        title_search, keyword_search, min_year, max_year, min_cite, max_cite)

    # if exact search and empty result, search again
    if len(df_paper_title_kw) == 0 and title_search.startswith('"'):
        exact_title = False
        # strip out double quote and search again
        title_search = title_search.replace('"', '')
        df_paper_title_kw, n = db_query.get_ids_by_title_keyword(
            title_search, keyword_search, min_year, max_year, min_cite, max_cite)

    # if empty, return and empty graph
    if len(df_paper_title_kw) == 0:
        print('No matched title or keyword')
        return json_graph.node_link_data(nx.Graph()), 0

    # iterate all starting pmids to get their citations
    ids = df_paper_title_kw['id'].tolist()
    cite_list = []
    # for starting_pmid in ids:
    cite_list.append(db_query.get_network_by_id(
        ids, citation_depth))
    df = pd.concat(cite_list)

    # build graph
    l_ = df[['apmid', 'bpmid']].drop_duplicates().values.tolist()
    G = nx.Graph()
    G.add_edges_from(l_)
    # df_rnk = get_rank(G, rank_var)

    # add node metadata
    for n in G:
        # create boolean variable that will tell us if n (the node)'s ID is in df_paper_title_kw's Id column
        # those not in should be visually represented differently.
        # label node with the degree level (i.e. 0 = start node, 1 = first depth layer, -1 = first depth layer)
        # if starting node, then degree = 0
        if n in ids:
            G.node[n]['search_returned_paper'] = True
            G.node[n]['degree'] = 0
        # if citing the starting node, then degree = -1,-2,-3...
        elif len(df[df['apmid'] == n]['depth']) > 0:
            G.node[n]['search_returned_paper'] = False
            G.node[n]['degree'] = -int(df[df['apmid'] == n]['depth'].min())
        # else, degree = 1,2,3...
        else:
            G.node[n]['search_returned_paper'] = False
            G.node[n]['degree'] = int(df[df['bpmid'] == n]['depth'].min())

        # create int variable that tells us rank of each node (compared with all nodes returned)
        # G.node[n]['rank'] = df_rnk[df_rnk['id'] == n]['rank'].values[0]

    # export graph to json
    jsonData = json_graph.node_link_data(G)
    jsonData['exact_title_phrase'] = exact_title
    print('Time taken', time.time() - t0)
    return jsonData, len(l_)


def generate_graph(min_year, max_year, min_cite, max_cite, rank_var='citations'):
    '''get graph by year'''

    # get articles within year range
    df_paper_yr, n = db_query.get_id_by_year(min_year, max_year)
    ids_yr = df_paper_yr['id'].tolist()

    # get articles within incoming citation range
    df_paper_ct, n = db_query.get_id_by_incoming_count(min_cite, max_cite)
    df_paper_ct = df_paper_ct[df_paper_ct['id'].isin(ids_yr)]

    # if no match, just return a blank graph
    if len(df_paper_ct) == 0:
        G = nx.Graph()
        jsonData = json_graph.node_link_data(G)
        return jsonData, 0

    # filter only top 20 articles
    df_paper_ct = df_paper_ct.nlargest(20, 'citations')
    ids = df_paper_ct['id'].tolist()

    # get citations
    df_citation_out, n = db_query.get_citations_by_id(ids, id_type='from')
    df_citation_in, n = db_query.get_citations_by_id(ids, id_type='to')
    df_citation = pd.concat(
        [df_citation_in, df_citation_out], ignore_index=True)

    # build graph
    l_ = df_citation.values.tolist()
    G = nx.Graph()
    G.add_edges_from(l_)
    df_rnk = get_rank(G, rank_var)

    # add node metadata
    for n in G:
        # create int variable that tells us rank of each node (compared with all nodes returned)
        G.node[n]['rank'] = df_rnk[df_rnk['id'] == n]['rank'].values[0]

    # export graph to json
    jsonData = json_graph.node_link_data(G)
    return jsonData, len(l_)


def get_rank(G, rank_var):
    '''calculate rank based on pagerank or citation count'''
    # use page rank
    if rank_var == 'pagerank':
        rnk_dict = nx.pagerank(G)
        df_rnk = pd.DataFrame([rnk_dict], index=[rank_var]).T
        df_rnk = df_rnk.reset_index().rename(columns={'index': 'id'})
    # use citation count
    if rank_var == 'citations':
        df_cnt, n = db_query.get_incoming_count_by_id(G.nodes())
        df_rnk = pd.DataFrame(G.nodes(), columns=['id']).merge(
            df_cnt, how='left', on='id', copy=False)
        df_rnk.fillna(0, inplace=True)
    df_rnk['rank'] = df_rnk[rank_var].rank(method='first', ascending=False)
    return df_rnk