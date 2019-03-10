from app import db
from sqlalchemy import select, MetaData
import pandas as pd


# get article by year
def get_article_by_year(min_year, max_year):
    # statement
    meta = MetaData(bind=db.engine)
    meta.reflect()
    article = meta.tables['article']
    stmt = select([article.c.id, article.c.title]).where(article.c.pubyear >= min_year)

    # read
    result = pd.read_sql(stmt, db.engine)
    return result, result.shape[0]

# get citation where apmid in the list
def get_citations_apmid(apmid_list):
    # statement
    meta = MetaData(bind=db.engine)
    meta.reflect()
    citation = meta.tables['citation']
    stmt = select([citation.c.apmid, citation.c.bpmid], citation.c.apmid.in_(apmid_list))

    # read
    result = pd.read_sql(stmt, db.engine)
    result = result.drop_duplicates()
    return result, result.shape[0]
