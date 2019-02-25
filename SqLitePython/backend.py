import sqlite3
import pandas
import csv


class Database:
    shouldImport = True

    def __init__(self):

        self.conn=sqlite3.connect("pmParkinsons.db")
        self.cur=self.conn.cursor()

        self.drop_all_tables()

        self.cur.execute("CREATE TABLE IF NOT EXISTS journals (jid INTEGER PRIMARY KEY, name text)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS articles (pmid INTEGER PRIMARY KEY, title text, keywords text, pubyear integer, jid integer, FOREIGN KEY(jid) REFERENCES journals(jid))")
        self.cur.execute("CREATE TABLE IF NOT EXISTS citations (cid INTEGER PRIMARY KEY, apmid integer, bpmid integer, FOREIGN KEY(apmid) REFERENCES articles(pmid), FOREIGN KEY(bpmid) REFERENCES articles(pmid))")

        if self.shouldImport:
            self.import_data()

        self.conn.commit()

    def __del__(self):
        self.conn.close()

    def import_data(self):
        #journals
        with open ('journal.csv', 'r', encoding="utf8") as jData:
            dr = csv.DictReader(jData)
            to_db = [(i['jid'], i['name']) for i in dr]

        self.cur.executemany("INSERT INTO journals (jid, name) VALUES (?, ?);", to_db)

        #Articles
        with open ('article.csv', 'r', encoding="utf8") as aData:
            dr = csv.DictReader(aData)
            to_db = [(i['pmid'], i['title'], i['keywords'], i['pubyear'], i['jid']) for i in dr]
        self.cur.executemany("INSERT INTO articles (pmid,title,keywords,pubyear,jid) VALUES (?, ?, ?, ?, ?);", to_db)

        #citations
        with open ('relationship_cite.csv', 'r', encoding="utf8") as aData:
            dr = csv.DictReader(aData)
            to_db = [(i['A'], i['B']) for i in dr]
        self.cur.executemany("INSERT INTO citations VALUES (NULL, ?, ?);", to_db)


    def get_citation_counts(self):
        self.cur.execute("SELECT articles.*, COUNT(citations.bpmid) as NumTimesCited from articles LEFT JOIN citations on articles.pmid = citations.bpmid GROUP BY articles.pmid ORDER BY NumTimesCited DESC")
        rows = self.cur.fetchall()
        return rows

    def run_sql(self, query):
        self.cur.execute(query)
        rows = self.cur.fetchall()
        return rows


    def drop_table(self, tableName):
        self.cur.execute("DROP TABLE IF EXISTS " + tableName)
        self.conn.commit()

    def drop_all_tables(self):
        self.cur.execute("DROP TABLE IF EXISTS citations")
        self.cur.execute("DROP TABLE IF EXISTS articles")
        self.cur.execute("DROP TABLE IF EXISTS journals")
        self.conn.commit()

    def view_all_table(self, tableName):
        self.cur.execute("SELECT * FROM " + tableName)
        rows = self.cur.fetchall()
        return rows

    def insertJournal(self, jid, name):
        self.cur.execute("INSERT INTO journals VALUES (?,?)",(jid, name))
        self.conn.commit()

    def insertArticle(self, pmid, title, keywords, pubyear, jid):
        self.cur.execute("INSERT INTO articles VALUES (?,?,?,?,?)",(pmid,title,keywords,pubyear,jid))
        self.conn.commit()

    def insertCitation(self, apmid, bpmid):
        self.cur.execute("INSERT INTO citations VALUES (NULL,?,?)",(apmid, bpmid))
        self.conn.commit()
