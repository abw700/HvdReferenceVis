from flask import Flask
from flask import jsonify, request, make_response, abort, url_for
from flask_sqlalchemy import SQLAlchemy
from config import app_config


# db initialization
db = SQLAlchemy()

# create app
def create_app(config_name):
    
    ## import models
    from app import models, db_query, graph

    ## create app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    db.init_app(app)

    ## HTTP error handling
    @app.errorhandler(404)
    def not_found(error):
        return make_response(jsonify({'error': 'Not found'}), 404)

    @app.errorhandler(400)
    def bad_request(error):
        return make_response(jsonify({'error': 'Bad request'}), 400)


    ## Simple routes using ORM
    # index
    @app.route('/')
    def index():
        return 'Reference visualization rocks!!!'

    ## article
    # GET by id
    @app.route('/api/article/<int:article_id>', methods=['GET'])
    def get_article_by_id(article_id):
        articles = models.Article().get(article_id)
        if not articles:
            abort(404)
        articles = [obj.to_dict() for obj in articles]
        return jsonify(article = articles), 200

    ## journal
    # GET all
    @app.route('/api/journal/', methods=['GET'])
    def get_journal_all():
        journals = models.Journal().get_all()
        if not journals:
            abort(404)
        journals = [obj.to_dict() for obj in journals]
        return jsonify(journal = journals), 200

    # GET by id
    @app.route('/api/journal/<int:journal_id>', methods=['GET'])
    def get_journal_by_id(journal_id):
        journals = models.Journal().get(journal_id)
        if not journals:
            abort(404)
        journals = [obj.to_dict() for obj in journals]
        return jsonify(journal = journals), 200

    ## citation
    # GET incoming citations by pmid
    @app.route('/api/incoming-cite/<int:article_id>', methods=['GET'])
    def get_incoming_cite(article_id):
        citations = models.Citation().get_incoming(article_id)
        if not citations:
            abort(404)
        return jsonify(incoming = citations), 200

    # GET outgoing citations by pmid
    @app.route('/api/outgoing-cite/<int:article_id>', methods=['GET'])
    def get_outgoing_cite(article_id):
        citations = models.Citation().get_outgoing(article_id)
        if not citations:
            abort(404)
        return jsonify(outgoing = citations), 200

    ## Other routes via SQLAlchemy
    # GET articles within the year timeframe
    @app.route('/api/article-in-period/', methods=['POST'])
    def get_articles_in_period():
        if not request.json or not 'min_year' in request.json or not 'max_year' in request.json:
            abort(400)
        min_year = request.json['min_year']
        max_year = request.json['max_year']

        # check if min < max
        if min_year > max_year:
            abort(400)
        
        # get
        articles, n = db_query.get_article_by_year(min_year, max_year)
        articles = articles.to_dict(orient='records')
        if not articles:
            abort(404)
        return jsonify(count = n, article = articles), 200

    # GET graph within the year timeframe
    @app.route('/api/graph-in-period/', methods=['POST'])
    def get_graph_in_period():
        if not request.json or not 'min_year' in request.json or not 'max_year' in request.json:
            abort(400)
        min_year = request.json['min_year']
        max_year = request.json['max_year']

        # check if min < max
        if min_year > max_year:
            abort(400)
        
        # get
        gr, n = graph.generate_graph(min_year, max_year)
        # gr = gr.to_dict(orient='records')
        if not gr:
            abort(404)
        return jsonify(count = n, graph = gr), 200





    return app



