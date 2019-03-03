#!/usr/bin/python

import pubmed_parser
import pandas as pd
import numpy as np
import os

## the script downloads data from medline api
## and save to ./download folder

# import search result
search_result = './pmcid/pmc_result.txt'
oa_ref = './references/oa_file_list.txt'
download_dir = './download'

# load
df_ref = pd.read_csv(oa_ref, sep='\t', skiprows=1, names=['addr', 'journal', 'pmc', 'pm', 'cc_code'])
df_search = pd.read_csv(search_result, sep='\t', names=['pmc'])
df_search['pmcid'] = df_search['pmc'].str.replace('PMC', '')
print("Search contains {:} files".format(df_search.shape[0]))

# merge the reference file and drop null
df = df_search.merge(df_ref, on='pmc')
df = df.dropna(subset=['pm'])
df = df.reset_index(drop=True)
print("Search contains {:} files that have PubmedID".format(df.shape[0]))

# medline api download

# split to run about 500 each time
n = int(df.shape[0] / 500)
l = np.array_split(df['pm'], n)

# loop
print("Downloading in {:} chunks ...".format(n))
for s_ in l:
    data_list_ = []
    for i,v in s_.iteritems():
        pmid_ = v.split(':')[-1]
        try:
            data_list_.append(pubmed_parser.parse_xml_web(pmid_, save_xml=False))
        except:
            pass

    # combine and save
    df_article = pd.DataFrame(data_list_)
    df_journal = pd.DataFrame(df_article['journal'].unique(), columns=['name'])
    df_article['pubyear'] = df_article['year'].astype(int)
    df_article = df_article[['pmid', 'title', 'keywords', 'abstract', 'pubyear', 'doi']]

    # dump to txt
    df_journal.to_csv(os.path.join(download_dir, 'journal_{:}.txt'.format(i)), sep='\t', index=False)
    df_article.to_csv(os.path.join(download_dir, 'article_{:}.txt'.format(i)), sep='\t', index=False)

    # progress
    print("Downloaded {:} / {:} files".format(i, df.shape[0]))

print('Download done!')