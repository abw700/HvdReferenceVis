#!/usr/bin/python

from ftplib import FTP
import pubmed_parser
import pandas as pd
import tarfile
import os

## the script downloads data from OA package FTP
## and save to ./download folder

search_result = './pmcid/pmc_result.txt'
oa_ref = './references/oa_file_list.txt'
ftp_link = 'ftp.ncbi.nlm.nih.gov'
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

# ftp download
print("Downloading...")
with FTP(ftp_link) as ftp:
    ftp.login()
    for i,v in df.iterrows():
        # download
        dir_ = '/'.join(['/pub/pmc'] + v['addr'].split('/')[:-1])
        ftp.cwd(dir_)
        filename = v['addr'].split('/')[-1]
        filedata = open(filename, 'wb')
        ftp.retrbinary('RETR ' + filename, filedata.write)
        filedata.close()
        
        # extract only .nxml
        tf = tarfile.open(filename)
        for tarinfo in tf:
            if os.path.splitext(tarinfo.name)[1] == ".nxml":
                tf.extract(member=tarinfo, path=download_dir)
        tf.close()
        
        # delete tar
        os.remove(filename)

        # progress
        if i % 1000 == 1:
            print("Downloaded {:} / {:} files".format(i + 1, df.shape[0]))
    ftp.quit()
print("All done!")
