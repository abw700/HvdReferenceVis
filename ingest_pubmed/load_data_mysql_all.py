#!/usr/bin/python

import sqlalchemy
import multiprocessing
import pandas as pd
import numpy as np
import pubmed_parser
import argparse
from tqdm import tqdm
from time import time
from datautils import create_tables, list_tables, write_tables, get_id, get_jid, create_address_mapping

# DB config
DB_CONFIG = {
    'endpoints': '0.0.0.0:3306',
    'dbname': 'rvcapsrv1',
    'username': 'root',
    'password': 'rWJ5is53',
    'pool_recycle': 3600
}
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + \
    DB_CONFIG['username'] + ':' + DB_CONFIG['password'] + '@' + \
    DB_CONFIG['endpoints'] + '/' + DB_CONFIG['dbname'] + '?charset=utf8mb4'

# Connection
conn = sqlalchemy.create_engine(
    SQLALCHEMY_DATABASE_URI, pool_recycle=DB_CONFIG['pool_recycle'])


# read, parse xml for one article and its citations
def read_xml(conn, filepath):
    # article
    df_article = pd.DataFrame([pubmed_parser.parse_pubmed_xml(filepath)])
    if df_article['pmid'][0] == '':
        return
    cols = df_article.columns.tolist()
    cols = ['title' if c == 'full_title' else c for c in cols]
    cols = ['year' if c == 'publication_year' else c for c in cols]
    df_article.columns = cols
    df_article['pubyear'] = df_article['year'].astype(int)

    # get jid and format article
    jid = get_jid(conn, df_article['journal'][0])
    df_article['jid'] = jid
    df_article = df_article[['pmid', 'title',
                             'abstract', 'pubyear', 'jid', 'keywords']]
    df_article.columns = ['id', 'title',
                          'abstract', 'pubyear', 'jid', 'keywords']

    # citations
    df_citations = pd.DataFrame(
        pubmed_parser.parse_pubmed_references(filepath))
    df_citations = df_citations[['pmid', 'pmid_cited']]
    df_citations = df_citations[df_citations['pmid_cited'] != '']
    df_citations.columns = ['apmid', 'bpmid']
    df_citations = df_citations.drop_duplicates()

    # return df_article, df_citations
    return df_article, df_citations


# process data
def worker(paths):
    conn = sqlalchemy.create_engine(
        SQLALCHEMY_DATABASE_URI, pool_recycle=DB_CONFIG['pool_recycle'])
    article_list = []
    citations_list = []
    for filepath in tqdm(paths):
        # read and write article, citations
        try:
            # read xml
            df_article, df_citations = read_xml(conn, filepath)
            if get_id(conn, df_article['id'][0]) == 0:
                article_list.append(df_article)
                citations_list.append(df_citations)
        except Exception:
            pass

    # write to tables
    if article_list and citations_list:
        # try:
        write_tables(conn, pd.concat(
            article_list, ignore_index=True), 'article')
        write_tables(conn, pd.concat(citations_list,
                                     ignore_index=True), 'citation')
        # except Exception:
        # print('Write failed')
    else:
        print('Nothing to write')
    return


# main
def main(args):
    # read file map
    df_file_mapping = create_address_mapping(args['data_dir'])
    l_ = df_file_mapping['fullpath'].tolist()
    paths = np.array_split(l_, 20)
    print('Processing {:} files in {:} chunks'.format(len(l_), len(paths)))

    # check if tables in db
    tables = list_tables(conn)

    # if no tables, create them
    if not tables:
        create_tables(conn)

    # read / write
    t0 = time()
    jobs = []
    for path_chunk in paths:
        p = multiprocessing.Process(target=worker, args=(path_chunk,))
        jobs.append(p)
        p.start()
    for j in jobs:
        j.join()
    print('Finished in {:.1f} seconds'.format(time() - t0))

    # table for storing citation count
    conn.execute("TRUNCATE TABLE citecount")
    sqltext = '''INSERT INTO citecount
                SELECT
                bpmid AS id
                , COUNT(1) AS citations
                , CASE WHEN a.id IS NULL THEN 1 ELSE 0 END AS has_data
                FROM citation c
                LEFT OUTER JOIN article a
                ON c.bpmid = a.id
                GROUP BY bpmid, title;
                '''
    conn.execute(sqltext)
    return


# cli
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-dir', help='data directory',
                        default='./data')
    args = vars(parser.parse_args())
    main(args)
