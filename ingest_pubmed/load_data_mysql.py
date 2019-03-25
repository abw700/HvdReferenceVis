#!/usr/bin/python

import pubmed_parser
import pandas as pd
import numpy as np
import sqlalchemy
import os

# paths
data_dir = './data'
search_result = './pmcid/pmc_result.txt'
file_mapping_path = './references/file_mapping.txt'

# read file map
df_file_mapping = pd.read_csv(file_mapping_path, sep='\t')
s_ = df_file_mapping['fullpath']

# parse article xml
data_list_ = []
ref_list_ = []
for i,v in s_.iteritems():
    try:
        data_list_.append(pubmed_parser.parse_pubmed_xml(v))
        ref_list_.append(pd.DataFrame(pubmed_parser.parse_pubmed_references(v)))
    except:
        pass

# combine article info
df_article = pd.DataFrame(data_list_)
cols = df_article.columns.tolist()
cols = ['title' if c == 'full_title' else c for c in cols]
cols = ['year' if c == 'publication_year' else c for c in cols]
df_article.columns = cols
df_article['pubyear'] = df_article['year'].astype(int)
df_journal = pd.DataFrame(df_article['journal'].unique(), columns=['name'])

# combine ref info
df_ref = pd.concat(ref_list_, ignore_index=True)
df_ref = df_ref[['pmid', 'pmid_cited']]
df_ref = df_ref[df_ref['pmid_cited'] != '']
df_ref.columns = ['apmid', 'bpmid']
df_ref = df_ref.drop_duplicates()

# database info
db_config = {
    'endpoints': 'rv-harvard-capstone-db.c5usqplnbvhe.us-east-1.rds.amazonaws.com',
    'dbname': 'rvcapsrv1',
    'username': 'rvcap',
    'password': 'rWJ5is53',
    'pool_recycle': 3600
}
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}/{}?charset=utf8mb4'.format(db_config['username'], db_config['password'], db_config['endpoints'], db_config['dbname'])

# connect and create tables if not exist
conn = sqlalchemy.create_engine(SQLALCHEMY_DATABASE_URI, pool_recycle=db_config['pool_recycle'])

# create tables
conn.execute("DROP TABLE IF EXISTS journal")
conn.execute("DROP TABLE IF EXISTS article")
conn.execute("DROP TABLE IF EXISTS citation")
conn.execute("CREATE TABLE IF NOT EXISTS journal (id INTEGER PRIMARY KEY UNIQUE AUTO_INCREMENT, name text)")
conn.execute("CREATE TABLE IF NOT EXISTS article (id INTEGER PRIMARY KEY UNIQUE, title text, abstract text, pubyear integer, jid integer, keywords text)")
conn.execute("CREATE TABLE IF NOT EXISTS citation (id INTEGER PRIMARY KEY UNIQUE AUTO_INCREMENT, apmid integer, bpmid integer)")
result = conn.execute("SHOW TABLES")
print('List if tables in db...')
print(result.fetchall())

# check if journal already in db if it is, don't add
df_journal_exists = pd.read_sql('journal', con=conn)
df_journal = df_journal.merge(df_journal_exists, how='left', on='name')
df_journal = df_journal[df_journal['id'].isna()][['name']]

# write journals to sql
df_journal.to_sql('journal', con=conn, index=False, if_exists='append')
print('Wrote {:} new journals to MySQL DB'.format(df_journal.shape[0]))

# get list of jid and put into article
df_journal_exists = pd.read_sql('journal', con=conn)
df_article = df_article.merge(df_journal_exists, how='inner', left_on='journal', right_on='name')
df_article = df_article[['pmid', 'title', 'abstract', 'pubyear', 'id', 'keywords']]
df_article.columns = ['id', 'title', 'abstract', 'pubyear', 'jid', 'keywords']

# check if article already in db if it is, don't add
df_article['id'] = df_article['id'].astype(int)
df_article['title'] = df_article['title'].str.encode('utf-8')
df_article['abstract'] = df_article['abstract'].str.encode('utf-8')
article_exists = pd.read_sql('''SELECT id FROM article''', con=conn)['id'].tolist()
df_article = df_article[~df_article['id'].isin(article_exists)]

# write articles to sql
df_article.to_sql('article', con=conn, index=False, if_exists='append')
print('Wrote {:} new articles to MySQL DB'.format(df_article.shape[0]))

# write references to sql
df_ref.to_sql('citation', con=conn, index=False, if_exists='append')
print('Wrote {:} new citations to MySQL DB'.format(df_ref.shape[0]))

# table for storing citation count
conn.execute("CREATE TABLE IF NOT EXISTS citecount (id INTEGER PRIMARY KEY UNIQUE, citations INTEGER)")
conn.execute("INSERT INTO citecount SELECT bpmid AS id, COUNT(1) AS citations FROM citation GROUP BY bpmid")