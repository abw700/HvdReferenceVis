from app import db
from sqlalchemy import select, MetaData
from nltk.tokenize import word_tokenize
import pandas as pd

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

# SEARCH by title
def get_ids_by_title_search(title_search):
    '''GET article by title search'''

    # Need to break the title_search down into tokens, and convert to RAW SQL statement
    # Use nltk
    title_tokens = word_tokenize(title_search)
    stmt = "SELECT * FROM article WHERE "
    title_token_counter = 0
    for title_part in title_tokens:
        if title_token_counter != 0:
            stmt += "AND "
        stmt += "title LIKE '%" + title_part + "%' "
        title_token_counter += 1

    # read
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
