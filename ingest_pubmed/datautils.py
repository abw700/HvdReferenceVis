import sqlalchemy
import pandas as pd
import os


# creates a file address mapping of all files in the directory
# file mapping also can be used to download more data from Pubmed
def create_address_mapping(data_dir):
    # dump paths to df, keep only folder that have xml files
    df = pd.DataFrame.from_dict({'dir': [x[0] for x in os.walk(data_dir)], 
                                'filename': [x[2] for x in os.walk(data_dir)]})
    df = df[df['filename'].astype(bool)]

    # create df that map filename to path
    xml_ = []
    for k,v in df.iterrows():
        dir_ = v['dir']
        files_ = v['filename']
        for f_ in files_:
            xml_.append((f_ , os.path.join(dir_, f_)))
    df_xml = pd.DataFrame.from_records(xml_, columns=['filename', 'fullpath'])
    return df_xml[['fullpath']]


# create tables
def create_tables(conn):
    conn.execute("DROP TABLE IF EXISTS journal")
    conn.execute("DROP TABLE IF EXISTS article")
    conn.execute("DROP TABLE IF EXISTS citation")
    conn.execute("DROP TABLE IF EXISTS citecount")
    conn.execute(
        "CREATE TABLE IF NOT EXISTS journal (id INTEGER PRIMARY KEY UNIQUE AUTO_INCREMENT, name TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS article (id INTEGER PRIMARY KEY UNIQUE, title TEXT, abstract TEXT, pubyear INTEGER, jid INTEGER, keywords TEXT)")
    conn.execute(
        "CREATE TABLE IF NOT EXISTS citation (id INTEGER PRIMARY KEY UNIQUE AUTO_INCREMENT, apmid INTEGER, bpmid INTEGER)")
    conn.execute(
        "CREATE TABLE IF NOT EXISTS citecount (id INTEGER PRIMARY KEY UNIQUE, citations INTEGER, has_data TINYINT)")
    print('Tables created')
    return


# list tables
def list_tables(conn):
    result = conn.execute("SHOW TABLES")
    return result.fetchall()


# write to tables
def write_tables(conn, df, table_name):
    df.to_sql(table_name, con=conn, index=False, if_exists='append')
    return df.shape[0]


# check if journal exists in db, inserting if necessary, return jid
def get_jid(conn, journal):
    # while loop to add, check jid
    jid = 0
    while jid == 0:
        # find jid
        stmt = sqlalchemy.text(
            '''SELECT DISTINCT id FROM journal WHERE name = :j''')
        stmt = stmt.bindparams(j=journal)
        result = conn.execute(stmt).fetchall()
        if result:
            jid = result[0][0]
            return jid
        # insert jid
        stmt = sqlalchemy.text('''INSERT INTO journal VALUES (NULL, :j)''')
        stmt = stmt.bindparams(j=journal)
        conn.execute(stmt)
    return jid


# check if id exist in article, return 0 if not exist
def get_id(conn, id):
    # find jid
    stmt = sqlalchemy.text('''SELECT DISTINCT id FROM article WHERE id = :i''')
    stmt = stmt.bindparams(i=id)
    result = conn.execute(stmt).fetchall()
    if result:
        return id
    else:
        return 0


