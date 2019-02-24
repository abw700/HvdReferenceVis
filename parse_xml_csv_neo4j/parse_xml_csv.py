import pandas as pd
import os
import pubmed_parser as pp

# this script parses pubmed xml to three csv files
# article.csv
# journal.csv
# relationship_cite.csv
# data is a sample from PubMed Medline 
# the script hits eutilities API to get citations
# store only 2 steps of citation
# [article a] -> [article b] -> [article c]

# dataframe
# df_citations : contains articles cited
# df_citations_info : contains info of articile cited
# df_citations_citations : contains articles cited in the 2nd degree

# topic
topic = 'Parkinson'

# data dir
DATA_DIR = './data'
SAV_DIR = './csv'

# read to dataframe
files = os.listdir(DATA_DIR)
data_list = []
for file in files:
    xml_out = pp.parse_medline_xml(os.path.join(DATA_DIR, file), year_info_only=False, nlm_category=False)
    data_list.append(pd.DataFrame(xml_out))
df = pd.concat(data_list, ignore_index=True)

# do only when contain the topic in the keyword
df = df[df['keywords'].isin([txt for txt in df['keywords'].tolist() if topic in txt])]
df['pubyear'] = df['pubdate'].str[:4].astype(int)
df = df[['pmid', 'title', 'journal', 'keywords', 'pubyear']]

# keep only those that have citation info
pmids = df['pmid'].tolist() #all pmid
pmids_tokeep_list = [] #list to keep pmids that have citation info
citation_list = [] #list to keep citation
i = 0 #just an iterator
print('looking at {:} articles that match our topic '.format(len(pmids)) + topic)
for pmid in pmids:
    # hit eutilities API to get citation info
    d_ = pp.parse_outgoing_citation_web(pmid, id_type='PMID')
    if d_:
        pmids_tokeep_list.append(pmid)
        citation_list.append(d_)
    if i % 100 == 0:
        print('{:} / {:} done'.format(i, len(pmids)))
    i += 1
df = df[df['pmid'].isin(pmids_tokeep_list)]
df_citations = pd.DataFrame(citation_list)

# get info of the articles cited
data_list_ = []
for pmids_ in df_citations['pmid_cited'].tolist():
    for pmid_ in pmids_:
        data_list_.append(pp.parse_xml_web(pmid_, save_xml=False))
df_citations_info = pd.DataFrame(data_list_)
df_citations_info['pubyear'] = df_citations_info['year'].astype(int)
df_citations_info = df_citations_info[['pmid', 'title', 'journal', 'keywords', 'pubyear']]

# find 2nd degree citation and stop there
pmids = df_citations_info['pmid'].tolist() #all pmid in the 1st degree
pmids_tokeep_list = [] #list to keep pmids that have citation info
citation_list = [] #list to keep citation
i = 0 #just an iterator
print('looking at {:} articles that match our topic '.format(len(pmids)) + topic)
for pmid in pmids:
    # hit eutilities API to get citation info
    d_ = pp.parse_outgoing_citation_web(pmid, id_type='PMID')
    if d_:
        pmids_tokeep_list.append(pmid)
        citation_list.append(d_)
    if i % 100 == 0:
        print('{:} / {:} done'.format(i, len(pmids)))
    i += 1
df_citations_citations = pd.DataFrame(citation_list)

# combine data of zero degree and 1st degree
df_all = pd.concat([df, df_citations_info], ignore_index=True)
df_all = df_all.drop_duplicates() #dedup if any

# build journal table, save
df_journal = pd.DataFrame(df_all['journal'].unique(), columns=['journal'])
df_journal['jid'] = df_journal.index + 1 #journal id
df_journal = df_journal[['jid', 'journal']] #reorder
df_journal.columns = ['jid', 'name'] #rename columns
df_journal.to_csv(os.path.join(SAV_DIR, 'journal.csv'), index=False)

# build article table, save
df_article = df_all.merge(df_journal, how='left', left_on='journal', right_on='name')
df_article = df_article[['pmid', 'title', 'keywords', 'pubyear', 'jid']]
df_article.to_csv(os.path.join(SAV_DIR, 'article.csv'), index=False)

# create pairs
pairs = []
valid_pmids = df_all['pmid'].unique().tolist()
dict_ = df_citations[['doc_id', 'pmid_cited']].set_index('doc_id').to_dict()['pmid_cited']
for k,v in dict_.items():
    for v1 in v:
        if v1 in valid_pmids:
            pairs.append([k, v1])
dict_ = df_citations_citations[['doc_id', 'pmid_cited']].set_index('doc_id').to_dict()['pmid_cited']
for k,v in dict_.items():
    for v1 in v:
        if v1 in valid_pmids:
            pairs.append([k, v1])
df_pairs = pd.DataFrame(pairs, columns=['A', 'B']).drop_duplicates()
df_pairs.to_csv(os.path.join(SAV_DIR, 'relationship_cite.csv'), index=False)
