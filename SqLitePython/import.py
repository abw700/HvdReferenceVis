import pandas
from backend import Database;

database = Database()

# Not currently in use... backend.py will import everything for now straight from the CSVs as a bulk import
dfArticles = pandas.read_csv("article.csv")
dfJournals = pandas.read_csv("journal.csv")
dfCitations = pandas.read_csv("relationship_cite.csv")


#print(dfJournals)

#database.drop_table("journals")
#database.drop_all_tables()
#print(database.view_all_table("citations"))
