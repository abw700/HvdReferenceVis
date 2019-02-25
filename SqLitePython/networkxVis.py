import pandas
from backend import Database;
from networkx import nx
import matplotlib.pyplot as plt
from networkx.readwrite import json_graph
import json
import flask

database = Database()
# Not currently in use... backend.py will import everything for now straight from the CSVs as a bulk import
dfArticles = pandas.read_csv("article.csv")
dfJournals = pandas.read_csv("journal.csv")
dfCitations = pandas.read_csv("relationship_cite.csv")

dfCitationCounts = pandas.DataFrame(database.get_citation_counts())


dfCitationDataForPaper = pandas.DataFrame(database.run_sql("SELECT citations.apmid as CitingPmid, a1.title as CitingTitle, a1.keywords as CitingKeywords, a1.pubyear as CitingPubyear, a1.jid as CitingJid, a2.pmid as CitedPmid, a2.title as CitedTitle, a2.keywords as CitedKeywords, a2.pubyear as CitedPubyear, a2.jid as CitedJid from citations INNER JOIN articles as a1 on a1.pmid = citations.apmid INNER JOIN articles as a2 on a2.pmid = citations.bpmid"))
#G = nx.convert_matrix.from_pandas_edgelist(dfCitationData, 0, 5)
G = nx.Graph()
vertices = dfArticles["pmid"]
edges = zip(dfCitations["A"], dfCitations["B"])
G.add_nodes_from(vertices)
G.add_edges_from(edges)

for n in G:
    G.node[n]['name'] = n

d = json_graph.node_link_data(G)
# write this JSON out to a file
json.dump(d, open('force/force.json', 'w'))

app = flask.Flask(__name__, static_folder="force")

@app.route('/<path:path>')
def static_proxy(path):
    return app.send_static_file(path)


print('\nGo to http://localhost:8000/force.html to see the example\n')
app.run(port=8000)

run()

#nx.draw(G, with_labels=True)
#plt.show()

#print(dfArticles["pmid"])


#print(dfJournals)

#database.drop_table("journals")
#database.drop_all_tables()
#print(database.view_all_table("citations"))


# Query to get counts
#SELECT articles.*, COUNT(citations.bpmid) as NumTimesCited
#from articles
#LEFT JOIN citations on articles.pmid = citations.bpmid
#GROUP BY articles.pmid


#Query to get all citations WITH data
#SELECT citations.apmid as CitingPmid, a1.title as CitingTitle, a1.keywords as CitingKeywords, a1.pubyear as CitingPubyear, a1.jid as CitingJid,
#a2.pmid as CitedPmid, a2.title as CitedTitle, a2.keywords as CitedKeywords, a2.pubyear as CitedPubyear, a2.jid as CitedJid
#from citations
#INNER JOIN articles as a1 on a1.pmid = citations.apmid
#INNER JOIN articles as a2 on a2.pmid = citations.bpmid
