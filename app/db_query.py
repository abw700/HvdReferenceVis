from app import db
from sqlalchemy import select, MetaData
import pandas as pd
import sqlalchemy

def get_id_by_year(min_year, max_year):
    '''get article by year'''

    # statement
    meta = MetaData(bind=db.engine)
    meta.reflect()
    article = meta.tables['article']
    stmt = select([article.c.id]).where(
        article.c.pubyear >= min_year).where(article.c.pubyear <= max_year)

    # read
    result = pd.read_sql(stmt, db.engine)
    return result, result.shape[0]

# SEARCH by title and/or keyword
def get_ids_by_title_keyword(title_search, keyword_search, min_year, max_year, min_cite, max_cite):
    '''GET article by title and/or keyword search'''

    # Need to break the title_search down into tokens, and convert to RAW SQL statement
    # first part of SQL statement 
    stmt = "SELECT a.id FROM article a "
    stmt += "WHERE pubyear BETWEEN " + str(min_year) + " AND " + str(max_year) + " "
    stmt += "AND citations BETWEEN " + str(min_cite) + " AND " + str(max_cite) + " "

    # if no search or search using wildcard `%`, just return blank
    if (title_search == "%" and keyword_search == "%") or (title_search == "" and keyword_search == ""):
        stmt += "LIMIT 1"
        result = pd.read_sql(stmt, db.engine)
        result = result.iloc[0:0]
    else:
        # title
        if title_search != "%" and title_search != "":
            # if exact phrase
            if title_search.startswith('"'):
                stmt += "AND MATCH(title) AGAINST ('" + title_search + "' IN BOOLEAN MODE) "
            else:
                stmt += "AND MATCH(title) AGAINST ('" + title_search + "') "

        # keyword
        if keyword_search != "%" and keyword_search != "":
            # separate keywords by commas
            keyword_tokens = ['+' + kw for kw in keyword_search.replace(', ', ',').split(',')]

            # add keyword
            stmt += "AND MATCH(keywords) AGAINST ('" + " ".join(keyword_tokens) + "' IN BOOLEAN MODE) "
            
        # read
        stmt += "ORDER BY citations DESC LIMIT 10"
        stmt = sqlalchemy.text(stmt)
        result = pd.read_sql(stmt, db.engine)
    return result, result.shape[0]


def get_id_by_incoming_count(min_cite, max_cite):
    '''get article IDs where incoming citations are within the range limit'''

    # statement
    meta = MetaData(bind=db.engine)
    meta.reflect()
    citecount = meta.tables['citecount']
    stmt = select([citecount.c.id, citecount.c.citations]).where(
        citecount.c.citations >= min_cite).where(citecount.c.citations <= max_cite)

    # read
    result = pd.read_sql(stmt, db.engine)
    result = result.sort_values('citations', ascending=False)
    return result, result.shape[0]


def get_incoming_count_by_id(id_list):
    '''get incoming citation count by article IDs'''

    # statement
    meta = MetaData(bind=db.engine)
    meta.reflect()
    citecount = meta.tables['citecount']
    stmt = select([citecount.c.id, citecount.c.citations], citecount.c.id.in_(tuple(id_list)))

    # read
    result = pd.read_sql(stmt, db.engine)
    result = result.sort_values('citations', ascending=False)
    return result, result.shape[0]


def get_citations_by_id(id_list, id_type=['from', 'to', 'both']):
    '''get citation where apmid or bpmid in the list'''

    # statement
    meta = MetaData(bind=db.engine)
    meta.reflect()
    citation = meta.tables['citation']

    # if looking at citation `from`, use apmid
    if id_type == 'from':
        stmt = select([citation.c.apmid, citation.c.bpmid],
                      citation.c.apmid.in_(id_list))
        result = pd.read_sql(stmt, db.engine)
    # if looking at citation `to`, use bpmid
    elif id_type == 'to':
        stmt = select([citation.c.apmid, citation.c.bpmid],
                      citation.c.bpmid.in_(id_list))
        result = pd.read_sql(stmt, db.engine)
    # else both direction
    else:
        stmt1 = select([citation.c.apmid, citation.c.bpmid],
                      citation.c.apmid.in_(id_list))
        stmt2 = select([citation.c.apmid, citation.c.bpmid],
                      citation.c.bpmid.in_(id_list))
        result1 = pd.read_sql(stmt1, db.engine)
        result2 = pd.read_sql(stmt2, db.engine)
        result = pd.concat([result1, result2], ignore_index=True)

    # read
    result = result.drop_duplicates()
    return result, result.shape[0]


def get_network_by_id(starting_pmids, citation_depth=1):
    '''get citation network (both incoming and outgoing) from starting pmid'''
    
    # iterate through the depth, starting with starting_pmids, store dataframe result in a dict
    l_ = []

    # outgoing
    depth_iteration = 1
    ids = starting_pmids[:]
    while depth_iteration <= citation_depth:
        df_citation_out, n = get_citations_by_id(ids, id_type='from')
        df_citation_out['depth'] = depth_iteration
        # add the current batch of nodes to the master list...
        ids = df_citation_out['bpmid'].tolist()
        l_.append(df_citation_out)
        depth_iteration += 1

    # incoming
    depth_iteration = 1
    ids = starting_pmids[:]
    while depth_iteration <= citation_depth:
        df_citation_in, n = get_citations_by_id(ids, id_type='to')
        df_citation_in['depth'] = depth_iteration
        # add the current batch of nodes to the master list...
        ids = df_citation_in['apmid'].tolist()
        l_.append(df_citation_in)
        depth_iteration += 1

    # combine all iterations
    nodes = pd.concat(l_, ignore_index=True)
    nodes = nodes.drop_duplicates()
    return nodes
