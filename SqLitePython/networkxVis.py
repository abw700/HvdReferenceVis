import pandas
from backend import Database;
from networkx import nx
import matplotlib.pyplot as plt
from networkx.readwrite import json_graph
import json
from flask import Flask, redirect, render_template, request

database = Database()
# Not currently in use... backend.py will import everything for now straight from the CSVs as a bulk import
# dfArticles = pandas.read_csv("article.csv")
dfJournals = pandas.read_csv("journal.csv")
dfCitations = pandas.read_csv("relationship_cite.csv")

dfCitationCounts = pandas.DataFrame(database.get_citation_counts())


dfCitationDataForPaper = ""
jsonData = ""


#G = nx.convert_matrix.from_pandas_edgelist(dfCitationData, 0, 5)
def generate_graph(minYear, maxYear):
    dfCitationDataForPaper = pandas.DataFrame(database.query_articles_with_pubyear(minYear, maxYear))

        # Get only the union between the two data sets (articles and citations -- only make nodes out of articles WITH a citation associated)
    dfPapers = pandas.concat([dfCitationDataForPaper.drop_duplicates(subset=[0]), dfCitationDataForPaper.drop_duplicates(subset=[5])])
    print("The size of the new Citations graph is %d  for years %s - %s" %(len(dfPapers), minYear, maxYear))
    print("Rendering Graph")
    G = nx.Graph()
    vertices = dfPapers[0]

    edges = list(zip(dfCitationDataForPaper[0], dfCitationDataForPaper[5]))

    G.add_nodes_from(vertices)
    G.add_edges_from(list(edges))

    # Add MetaDAta! TODO: Add citation count and pub date and such
    index = 0
    for n in G:
        if index < len(dfPapers):
            G.node[n]['pmid'] = n
            G.node[n]['title'] = dfPapers.iloc[index,1]
            G.node[n]['pubyear'] = str(dfPapers.iloc[index,3])
            index = index + 1

    # Get JSON in text format to pass via results to HTML side...
    jsonData = json_graph.node_link_data(G)
    jsonData = json.dumps(jsonData)

    print("Received JSON -- Sending along to HTML under RESULTS param")
    return jsonData

# Defaults to 1900 - 2020


app = Flask(__name__, static_folder="force")

@app.route('/')
def main_route():
    jsonData = generate_graph(1900, 2020)
    return render_template("main.html", results = jsonData)

@app.route('/success', methods=['POST'])
def success():
    if request.method == 'POST':
        minYear = request.form["years_old_min"]
        maxYear = request.form["years_old_max"]
        if minYear and maxYear:
            print("The min year is %s and the max year is %s" %(minYear, maxYear))
            jsonData = generate_graph(minYear, maxYear)
            # print(jsonData)
        return render_template("main.html", results = jsonData)
        # return render_template("main.html", results = jsonData)


print('\nGo to http://localhost:8000/force.html to see the example\n')

if(__name__ == "__main__"):
    app.run(debug = True, port = 8000)
