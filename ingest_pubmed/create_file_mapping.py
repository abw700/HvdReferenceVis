import pubmed_parser as pp
import pandas as pd
import os

## the script creates a file mapping based on Pubmed OA search result
## file mapping can be used to download more data from Pubmed

# paths
DATA_DIR = './data'
PMC_PATH = './pmcid/pmc_result.txt'

# dump paths to df, keep only folder that have xml files
df = pd.DataFrame.from_dict({'dir': [x[0] for x in os.walk(DATA_DIR)], 
                             'filename': [x[2] for x in os.walk(DATA_DIR)]})
df = df[df['filename'].astype(bool)]

# create df that map filename to path
xml_ = []
for k,v in df.iterrows():
    dir_ = v['dir']
    files_ = v['filename']
    for f_ in files_:
        xml_.append((f_ , os.path.join(dir_, f_)))
df_xml = pd.DataFrame.from_records(xml_, columns=['filename', 'fullpath'])

# read pmcid, build file mapping
df_file_mapping = pd.read_csv(PMC_PATH, names=['filename'])
df_file_mapping['pmc'] = df_file_mapping['filename'].str.replace('PMC', '')
df_file_mapping['filename'] = df_file_mapping['filename'].astype(str) + '.nxml'
df_file_mapping = df_file_mapping.merge(df_xml, how='inner', on='filename')

# find pmid from xml files, keep only those with pmid
df_file_mapping['pmid'] = df_file_mapping['fullpath'].map(lambda x: pp.parse_pubmed_xml(x)['pmid'])
df_file_mapping = df_file_mapping[df_file_mapping['pmid'] != '']

# save to csv
df_file_mapping = df_file_mapping[['pmc', 'pmid', 'filename', 'fullpath']]
df_file_mapping.to_csv('file_mapping.csv', index=False)
