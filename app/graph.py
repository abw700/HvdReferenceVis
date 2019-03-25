from app import db_query, models
import pandas as pd
import networkx as nx
from networkx.readwrite import json_graph
from difflib import get_close_matches

def generate_graph_outgoing_citations(starting_pmid, citation_depth, rank_var='citations'):
    ''' GET graph a number of depth CITATIONs away, '''

    # iterate through the depth, starting with starting_pmid, store dataframe result in a dict
    l_ = []
    depth_iterations = 1
    ids = [starting_pmid]
    while depth_iterations <= citation_depth:
        df_citation_out, n = db_query.get_citations_by_id(ids, id_type='from')
        df_citation_out['depth'] = depth_iterations
        # add the current batch of nodes to the master list...
        ids = df_citation_out['bpmid'].tolist()
        l_.append(df_citation_out)
        depth_iterations += 1

    # combine all iterations
    df = pd.concat(l_, ignore_index=True)

    # build graph
    l_ = df[['apmid', 'bpmid']].values.tolist()
    G = nx.Graph()
    G.add_edges_from(l_)

    # calculate rank
    # use page rank
    if rank_var == 'pagerank':
        rnk_dict = nx.pagerank(G)
        df_rnk = pd.DataFrame([rnk_dict], index=[rank_var]).T
        df_rnk = df_rnk.reset_index().rename(columns={'index':'id'})
    # use citation count
    if rank_var == 'citations':
        df_cnt, n = db_query.get_incoming_count_by_id(G.nodes())
        df_rnk = pd.DataFrame(G.nodes(), columns=['id']).merge(df_cnt, how='left', on='id', copy=False)
        df_rnk.fillna(0, inplace=True)
    df_rnk['rank'] = df_rnk[rank_var].rank(method='dense', ascending=False)
    dict_rnk = df_rnk[['id', 'rank']].to_dict(orient='records')

    # add node metadata
    for n in G:
        # label node with the degree level (i.e. 0 = start node, 1 = first depth layer)
        if n == starting_pmid:
            G.node[n]['degree'] = 0
        else:
            G.node[n]['degree'] = int(df[df['bpmid'] == n]['depth'].values[0])

        # create int variable that tells us rank of each node (compared with all nodes returned)
        G.node[n]['rank'] = df_rnk[df_rnk['id'] == n]['rank'].values[0]

    # export graph to json
    jsonData = json_graph.node_link_data(G)
    return jsonData, len(l_)

def generate_graph_title_search(title_search, min_year, max_year, min_cite, max_cite, rank_var='citations'):
    '''GET graph by year'''

    # GET articles with the search title parameters
    title_search = title_search.replace("'", "")
    df_paper_title_search, n = db_query.get_ids_by_title_search(title_search)

    # filter out those that have low difflib score
    matches = get_close_matches(title_search, df_paper_title_search['title'], n=20, cutoff=0.3)
    df_paper_title_search = df_paper_title_search[df_paper_title_search['title'].isin(matches)]

    # if empty, return and empty graph
    if not matches:
        print('No matched title')
        return json_graph.node_link_data(nx.Graph()), 0

    # keep only articles within min_year and max_year
    year_mask = (df_paper_title_search['pubyear'] >= min_year) & (df_paper_title_search['pubyear'] <= max_year)
    df_paper_title_search = df_paper_title_search[year_mask]
    ids_matched = df_paper_title_search['id'].tolist()

    # keep only articles within min_cite and max_cite
    df_citation_count, n = db_query.get_incoming_count_by_id(ids_matched)
    cnt_mask = (df_citation_count['citations'] >= min_cite) & (df_citation_count['citations'] <= max_cite)
    df_citation_count = df_citation_count[cnt_mask]
    df_paper_title_search = df_paper_title_search.merge(df_citation_count, how='inner', on='id', copy=False)
    ids = df_paper_title_search['id'].tolist()

    # get citations
    df_citation_out, n = db_query.get_citations_by_id(ids, id_type='from')
    df_citation_in, n = db_query.get_citations_by_id(ids, id_type='to')
    df_citation = pd.concat([df_citation_in, df_citation_out], ignore_index=True)

    # build graph
    l_ = df_citation.values.tolist()
    G = nx.Graph()
    G.add_edges_from(l_)

    # calculate rank
    # use page rank
    if rank_var == 'pagerank':
        rnk_dict = nx.pagerank(G)
        df_rnk = pd.DataFrame([rnk_dict], index=[rank_var]).T
        df_rnk = df_rnk.reset_index().rename(columns={'index':'id'})
    # use citation count
    if rank_var == 'citations':
        df_cnt, n = db_query.get_incoming_count_by_id(G.nodes())
        df_rnk = pd.DataFrame(G.nodes(), columns=['id']).merge(df_cnt, how='left', on='id', copy=False)
        df_rnk.fillna(0, inplace=True)
    df_rnk['rank'] = df_rnk[rank_var].rank(method='dense', ascending=False)
    dict_rnk = df_rnk[['id', 'rank']].to_dict(orient='records')

    # add node metadata
    for n in G:
        # create boolean variable that will tell us if n (the node)'s ID is in df_paper_title_search's Id column
        # those not in should be visually represented differently.
        if n in ids:
            G.node[n]['search_returned_paper'] = True
        else:
            G.node[n]['search_returned_paper'] = False

        # create int variable that tells us rank of each node (compared with all nodes returned)
        G.node[n]['rank'] = df_rnk[df_rnk['id'] == n]['rank'].values[0]

    # export graph to json
    jsonData = json_graph.node_link_data(G)
    return jsonData, len(l_)

def generate_graph(min_year, max_year, min_cite, max_cite, rank_var='citations'):
    '''get graph by year'''

    # get articles within year range
    df_paper_yr, n = db_query.get_id_by_year(min_year, max_year)
    ids_yr = df_paper_yr['id'].tolist()

    # get articles within incoming citation range
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

    # calculate rank
    # use page rank
    if rank_var == 'pagerank':
        rnk_dict = nx.pagerank(G)
        df_rnk = pd.DataFrame([rnk_dict], index=[rank_var]).T
        df_rnk = df_rnk.reset_index().rename(columns={'index':'id'})
    # use citation count
    if rank_var == 'citations':
        df_cnt, n = db_query.get_incoming_count_by_id(G.nodes())
        df_rnk = pd.DataFrame(G.nodes(), columns=['id']).merge(df_cnt, how='left', on='id', copy=False)
        df_rnk.fillna(0, inplace=True)
    df_rnk['rank'] = df_rnk[rank_var].rank(method='dense', ascending=False)
    dict_rnk = df_rnk[['id', 'rank']].to_dict(orient='records')

    # add node metadata
    for n in G:
        # create int variable that tells us rank of each node (compared with all nodes returned)
        G.node[n]['rank'] = df_rnk[df_rnk['id'] == n]['rank'].values[0]

    # export graph to json
    jsonData = json_graph.node_link_data(G)
    return jsonData, len(l_)
