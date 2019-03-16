from flask import jsonify, request, abort, url_for
from app import app, models, db_query, graph

# Simple routes using ORM

# index
@app.route('/')
def index():
    '''Index'''
    return 'Reference visualization rocks!!!'

# article list for all articles
@app.route('/article', methods=['POST'])
def get_article_all():
    '''GET all articles'''
    article_limit = 100
    if not request.json:
        article_limit = 100
    else:
        article_limit = request.json['article_limit']

    # TODO: AW to figure out a default if no JSON is provided.

    articles = models.Article().get_all(article_limit)
    if not articles:
        abort(404)
    articles = [obj.to_dict() for obj in articles]
    return jsonify(article=articles), 200


# article by id
@app.route('/article/<int:article_id>', methods=['GET'])
def get_article_by_id(article_id):
    '''GET by id'''

    articles = models.Article().get(article_id)
    if not articles:
        abort(404)
    articles = [obj.to_dict() for obj in articles]
    print(articles)
    return jsonify(article=articles), 200

# article within the period
@app.route('/article/period', methods=['POST'])
def get_article_id_in_period():
    '''GET articles within the year timeframe'''

    if not request.json:
        abort(400)
    min_year = request.json['min_year'] if 'min_year' else 0
    max_year = request.json['max_year'] if 'max_year' else 9999
    print(min_year)

    # check if min < max
    if min_year > max_year:
        abort(400)

    # get
    articles, n = db_query.get_id_by_year(min_year, max_year)
    articles = articles.to_dict(orient='records')
    if not articles:
        abort(404)
    return jsonify(count=n, article=articles), 200

# article within the range of number of incoming citations
@app.route('/article/citation-range', methods=['POST'])
def get_article_id_by_citationcount():
    '''GET articles within incoming count limit'''

    if not request.json:
        abort(400)
    min_cite = request.json['min_cite'] if 'min_cite' else 0
    max_cite = request.json['max_cite'] if 'max_cite' else 999999

    # check if min < max
    if min_cite > max_cite:
        abort(400)

    # get
    ids, n = db_query.get_id_by_incoming_count(min_cite, max_cite)
    ids = ids.drop('citations', axis=1)
    ids = ids.to_dict(orient='records')
    if not ids:
        abort(404)
    return jsonify(count=n, article=ids), 200

# incoming citations
@app.route('/article/<int:article_id>/incoming-citations', methods=['GET'])
def get_incoming_cite(article_id):
    '''GET incoming citations by pmid'''

    citations = models.Citation().get_incoming(article_id)
    if not citations:
        abort(404)
    return jsonify(incoming=citations), 200

# outgoing citations
@app.route('/article/<int:article_id>/outgoing-citations', methods=['GET'])
def get_outgoing_cite(article_id):
    '''GET outgoing citations by pmid'''

    citations = models.Citation().get_outgoing(article_id)
    if not citations:
        abort(404)
    return jsonify(outgoing=citations), 200

# journal
@app.route('/journal', methods=['GET'])
def get_journal_all():
    '''GET all'''
    journals = models.Journal().get_all()
    if not journals:
        abort(404)
    journals = [obj.to_dict() for obj in journals]
    return jsonify(journal=journals), 200

# journal by id
@app.route('/journal/<int:journal_id>', methods=['GET'])
def get_journal_by_id(journal_id):
    '''GET by id'''

    journals = models.Journal().get(journal_id)
    if not journals:
        abort(404)
    journals = [obj.to_dict() for obj in journals]
    return jsonify(journal=journals), 200

# graph
@app.route('/graph', methods=['POST'])
def get_graph_in_period():
    '''GET graph within the year timeframe'''

    if not request.json:
        abort(400)
    min_year = request.json['min_year'] if 'min_year' else 0
    max_year = request.json['max_year'] if 'max_year' else 9999
    min_cite = request.json['min_cite'] if 'min_cite' else 0
    max_cite = request.json['max_cite'] if 'max_cite' else 999999
    rank_var = request.json['rank'] if 'rank' else 'none'

    # check if min < max
    if min_year > max_year or min_cite > max_cite:
        abort(400)

    # get
    gr, n = graph.generate_graph(min_year, max_year, min_cite, max_cite, rank_var)
    # gr = gr.to_dict(orient='records')
    if not gr:
        abort(404)
    return jsonify(count=n, graph=gr), 200

# graph title SEARCH
@app.route('/graph/title', methods=['POST'])
def get_graph_in_period_with_title():
    '''GET graph within the year timeframe, with provided title (SEARCH)'''

    if not request.json:
        abort(400)
    title = request.json['title'] if 'title' else '%'
    min_year = request.json['min_year'] if 'min_year' else 0
    max_year = request.json['max_year'] if 'max_year' else 9999
    min_cite = request.json['min_cite'] if 'min_cite' else 0
    max_cite = request.json['max_cite'] if 'max_cite' else 999999
    rank_var = request.json['rank'] if 'rank' else 'none'

    # check if min < max
    if min_year > max_year or min_cite > max_cite:
        abort(400)

    # get
    gr, n = graph.generate_graph_title_search(title, min_year, max_year, min_cite, max_cite, rank_var)
    # gr = gr.to_dict(orient='records')
    if not gr:
        abort(404)
    return jsonify(count=n, graph=gr), 200
