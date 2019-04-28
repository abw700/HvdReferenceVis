from app import db
from sqlalchemy import select, MetaData
from nltk.tokenize import word_tokenize
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
    stmt = "SELECT a.id, a.title, c.citations FROM article a "
    stmt += "INNER JOIN citecount c ON a.id = c.id AND c.citations BETWEEN " + str(min_cite) + " AND " + str(max_cite) + " "
    stmt += "WHERE pubyear BETWEEN " + str(min_year) + " AND " + str(max_year) + " "

    # if no search or search using wildcard `%`, just return blank
    if (title_search == "%" and keyword_search == "%") or (title_search == "" and keyword_search == ""):
        stmt += "LIMIT 1"
        result = pd.read_sql(stmt, db.engine)
        result = result.iloc[0:0]
    else:
        # title
        if title_search != "%" and title_search != "":
            # Use nltk to tokenize
            title_tokens = word_tokenize(title_search)
        
            # add title to stmt
            title_token_counter = 0
            for title_part in title_tokens:
                stmt += "AND MATCH(title) AGAINST ('" + title_part + "') "
                title_token_counter += 1
            
        # keyword
        if keyword_search != "%" and keyword_search != "":
            # separate keywords by commas
            keyword_tokens = keyword_search.replace(', ', ',').split(',')

            # add keyword
            keyword_token_counter = 0
            for keyword_part in keyword_tokens:
                stmt += "AND MATCH(keywords) AGAINST ('" + keyword_part + "') "
                keyword_token_counter += 1

        # read
        stmt += "ORDER BY citations LIMIT 20"
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


def get_citations_by_id(id_list, id_type=['from', 'to']):
    '''get citation where apmid or bpmid in the list'''

    # statement
    meta = MetaData(bind=db.engine)
    meta.reflect()
    citation = meta.tables['citation']

    # if looking at citation `from`, use apmid
    if id_type == 'from':
        stmt = select([citation.c.apmid, citation.c.bpmid],
                      citation.c.apmid.in_(id_list))
    # if looking at citation `to`, use bpmid
    else:
        stmt = select([citation.c.apmid, citation.c.bpmid],
                      citation.c.bpmid.in_(id_list))

    # read
    result = pd.read_sql(stmt, db.engine)
    result = result.drop_duplicates()
    return result, result.shape[0]


def get_network_by_id(starting_pmid, citation_depth=1):
    '''get citation network (both incoming and outgoing) from starting pmid'''
    
    # iterate through the depth, starting with starting_pmid, store dataframe result in a dict
    l_ = []

    # outgoing
    depth_iteration = 1
    ids = [starting_pmid]
    while depth_iteration <= citation_depth:
        df_citation_out, n = get_citations_by_id(ids, id_type='from')
        df_citation_out['depth'] = depth_iteration
        # add the current batch of nodes to the master list...
        ids = df_citation_out['bpmid'].tolist()
        l_.append(df_citation_out)
        depth_iteration += 1

    # incoming
    depth_iteration = 1
    ids = [starting_pmid]
    while depth_iteration <= citation_depth:
        df_citation_in, n = get_citations_by_id(ids, id_type='to')
        df_citation_in['depth'] = depth_iteration
        # add the current batch of nodes to the master list...
        ids = df_citation_in['apmid'].tolist()
        l_.append(df_citation_in)
        depth_iteration += 1

    # combine all iterations
    return pd.concat(l_, ignore_index=True)

