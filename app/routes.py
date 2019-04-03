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

    # limit number of articles
    article_limit = 100
    if not request.data or not request.json or 'article_limit' not in request.json:
        article_limit = 100
    else:
        article_limit = request.json['article_limit']

    # get
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

    # check
    if not request.json:
        abort(400)
    min_year, max_year = check_year(request)

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

    # check
    if not request.json:
        abort(400)
    min_cite, max_cite = check_cite(request)

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
    if not citations['citing_pmid']:
        abort(404)
    return jsonify(incoming=citations), 200

# outgoing citations
@app.route('/article/<int:article_id>/outgoing-citations', methods=['GET'])
def get_outgoing_cite(article_id):
    '''GET outgoing citations by pmid'''

    citations = models.Citation().get_outgoing(article_id)
    if not citations['cited_pmid']:
        abort(404)
    print(citations)
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

    # check
    if not request.json:
        abort(400)
    rank_var = check_rankvar(request)
    min_year, max_year = check_year(request)
    min_cite, max_cite = check_cite(request)

    # get
    gr, n = graph.generate_graph(
        min_year, max_year, min_cite, max_cite, rank_var)
    if not gr:
        abort(404)
    return jsonify(count=n, graph=gr), 200

# graph title SEARCH
@app.route('/graph/title', methods=['POST'])
def get_graph_in_period_with_title():
    '''GET graph within the year timeframe, with provided title (SEARCH)'''

    # check
    if not request.json:
        abort(400)
    depth = check_depth(request)
    rank_var = check_rankvar(request)
    cutoff = check_cutoff(request)
    min_year, max_year = check_year(request)
    min_cite, max_cite = check_cite(request)
    
    # default title
    title = request.json['title'] if 'title' in request.json else '%'

    # get
    gr, n = graph.generate_graph_title_search(
        title, depth, min_year, max_year, min_cite, max_cite, rank_var, cutoff)
    if not gr:
        abort(404)
    return jsonify(count=n, graph=gr), 200

# graph started from 1 article ID
@app.route('/graph/<int:article_id>', methods=['POST'])
def get_graph_from_id(article_id):
    '''GET graph from one article ID'''

    # check
    if not request.json:
        abort(400)
    depth = check_depth(request)
    rank_var = check_rankvar(request)

    # get
    gr, n = graph.generate_graph_outgoing_citations(article_id, depth, rank_var)
    if not gr:
        abort(404)
    return jsonify(count=n, graph=gr), 200


# check depth
def check_depth(request):
    # default depth to 2, limit depth to 3
    if not request.data or 'depth' not in request.json or request.json['depth'] <= 0:
        depth = 2
    else:
        depth = min(request.json['depth'], 3)
    return depth

# check rank_var
def check_rankvar(request):
    # default rank_var to `citations`
    if not request.data or 'rank' not in request.json or request.json['rank'] not in ['citations', 'pagerank']:
        rank_var = 'citations'
    else:
        rank_var = request.json['rank']
    return rank_var

# check cutoff
def check_cutoff(request):    
    # default cutoff to 0.3, limit to 0.1 to 0.9
    if 'cutoff' not in request.json:
        cutoff = 0.3
    else:
        cutoff = max(min(request.json['cutoff'], 0.9), 0.1)
    return cutoff

# check min_year, max_year
def check_year(request):
    # default year range
    if not request.data or 'min_year' not in request.json or request.json['min_year'] < 0:
        min_year = 0
    else:
        min_year = request.json['min_year']
    if not request.data or 'max_year' not in request.json or request.json['max_year'] <= 0:
        max_year = 9999
    else:
        max_year = request.json['max_year']
    # check if min < max
    if min_year > max_year or min_year < 0 or max_year <= 0:
        abort(400)
    return min_year, max_year

# check min_cite, max_cite
def check_cite(request):
    # default citation range
    if not request.data or 'min_cite' not in request.json or request.json['min_cite'] < 0:
        min_cite = 0
    else:
        min_cite = request.json['min_cite']
    if not request.data or 'max_cite' not in request.json or request.json['max_cite'] <= 0:
        max_cite = 999999
    else:
        max_cite = request.json['max_cite']
    # check if min < max
    if min_cite > max_cite or min_cite < 0 or max_cite <= 0:
        abort(400)
    return min_cite, max_cite

