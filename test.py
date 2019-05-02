import json
import pytest

# post JSON
def post_json(client, url, json_dict):
    """Send dictionary json_dict as a json to the specified url """
    return client.post(url, data=json.dumps(json_dict), content_type='application/json')

# TEST
# create app
@pytest.fixture
def app():
    from app import app
    return app

# routes
# test first page
def test_index(client):
    response = client.get("/")
    assert response.status_code == 200
    
# test journal response
def test_journal(client):
    response = client.get("/v1/journal")
    assert response.status_code == 200
    # valid journal
    response = client.get("/v1/journal/7")
    assert response.status_code == 200
    # invalid journal
    response = client.get("/v1/journal/100000")
    assert response.status_code == 404

# test article response
def test_article(client):
    # all articles
    response = client.post("/v1/article")
    assert response.status_code == 200
    # 10 articles
    json_dict = {'article_limit': 10}
    response = post_json(client, "/v1/article", json_dict)
    assert response.status_code == 200
    # valid article
    response = client.get("/v1/article/26272696")
    assert response.status_code == 200
    # invalid article
    response = client.get("/v1/article/0")
    assert response.status_code == 404

# test article within a period
def test_article_period(client):
    # no json body, return 400
    response = client.post("/v1/article/period")
    assert response.status_code == 400
    # correct json body, return 200
    json_dict = {'min_year': 2015, 'max_year': 2019}
    response = post_json(client, "/v1/article/period", json_dict)
    assert response.status_code == 200
    # wrong json body, fall back to default, return 200
    json_dict = {'min_year': -10, 'max_year': 0}
    response = post_json(client, "/v1/article/period", json_dict)
    assert response.status_code == 200
    # invalid article
    json_dict = {'min_year': 1000, 'max_year': 1001}
    response = post_json(client, "/v1/article/period", json_dict)
    assert response.status_code == 404

# test article within the citation count range
def test_article_citerange(client):
    # no json body, return 400
    response = client.post("/v1/article/citation-range")
    assert response.status_code == 400
    # correct json body, return 200
    json_dict = {'min_cite': 0, 'max_cite': 10}
    response = post_json(client, "/v1/article/citation-range", json_dict)
    assert response.status_code == 200
    # wrong json body, fall back to default, return 200
    json_dict = {'min_cite': -10, 'max_cite': 0}
    response = post_json(client, "/v1/article/citation-range", json_dict)
    assert response.status_code == 200
    # invalid article
    json_dict = {'min_cite': 1000000, 'max_cite': 1000001}
    response = post_json(client, "/v1/article/citation-range", json_dict)
    assert response.status_code == 404

# test incoming citations
def test_incoming(client):
    # wrong id, return 404
    response = client.get("/v1/article/1/incoming-citations")
    assert response.status_code == 404
    # correct id, return 200
    response = client.get("/v1/article/26272696/incoming-citations")
    assert response.status_code == 200

# test outgoing citations
def test_outgoing(client):
    # wrong id, return 404
    response = client.get("/v1/article/1/outgoing-citations")
    assert response.status_code == 404
    # correct id, return 200
    response = client.get("/v1/article/26272696/outgoing-citations")
    assert response.status_code == 200

# test /graph
def test_graph(client):
    # no json body, return 400
    response = client.post("/v1/graph")
    assert response.status_code == 400
    # correct json body, return 200
    json_dict = {'min_cite': 9, 'max_cite': 10}
    response = post_json(client, "/v1/graph", json_dict)
    assert response.status_code == 200
    # correct json body, return 200
    json_dict = {'min_year': 2014, 'max_year': 2015}
    response = post_json(client, "/v1/graph", json_dict)
    assert response.status_code == 200
    # wrong json body, year max < min, return 400
    json_dict = {'min_year': 2010, 'max_year': 2008}
    response = post_json(client, "/v1/graph", json_dict)
    assert response.status_code == 400
    # wrong json body, fall back to default, return 200
    json_dict = {'min_year': -10, 'max_year': 0}
    response = post_json(client, "/v1/graph", json_dict)
    assert response.status_code == 200

# test /graph/title
def test_graph_title(client):
    # no json body, return 400
    response = client.post("/v1/graph/title")
    assert response.status_code == 400
    # correct json body, return 200
    json_dict = {'min_cite': 3, 'max_cite': 10}
    response = post_json(client, "/v1/graph/title", json_dict)
    assert response.status_code == 200
    # correct json body, return 200
    json_dict = {'min_year': 2014, 'max_year': 2015}
    response = post_json(client, "/v1/graph/title", json_dict)
    assert response.status_code == 200
    # correct json body, return 200
    json_dict = {'cutoff': 0.05}
    response = post_json(client, "/v1/graph/title", json_dict)
    assert response.status_code == 200
    # correct json body, return 200
    json_dict = {'depth': 3, 'title': 'liver cancer'}
    response = post_json(client, "/v1/graph/title", json_dict)
    assert response.status_code == 200
    # correct json body, no match, return 200
    json_dict = {'depth': 3, 'title': 'justasearchthatnotmatched'}
    response = post_json(client, "/v1/graph/title", json_dict)
    # wrong depth, fall back to default, return 200
    json_dict = {'depth': -3, 'rank': 'citations'}
    response = post_json(client, "/v1/graph/title", json_dict)
    assert response.status_code == 200
    # wrong json body, year max < min, return 400
    json_dict = {'min_year': 2010, 'max_year': 2008}
    response = post_json(client, "/v1/graph/title", json_dict)
    assert response.status_code == 400
    # wrong json body, fall back to default, return 200
    json_dict = {'min_year': -10, 'max_year': 0, 'rnk': 'citations'}
    response = post_json(client, "/v1/graph/title", json_dict)
    assert response.status_code == 200

# test /graph/id
def test_graph_id(client):
    # no json body, return 400
    response = client.post("/v1/graph/26272696")
    assert response.status_code == 400
    # correct json body, return 200
    json_dict = {'depth': 2, 'rank': 'citations'}
    response = post_json(client, "/v1/graph/26272696", json_dict)
    assert response.status_code == 200
    # correct json body, return 200
    json_dict = {'depth': 1, 'rank': 'pagerank'}
    response = post_json(client, "/v1/graph/26272696", json_dict)
    assert response.status_code == 200
    # wrong json params, fall back to default, return 200
    json_dict = {'depth': -3, 'rank': 'cite'}
    response = post_json(client, "/v1/graph/26272696", json_dict)
    assert response.status_code == 200

# test /graph/keyword
def test_graph_keyword(client):
    # correct json body, matched keyword, return 200
    json_dict = {'depth': 3, 'keyword': 'Hepatocellular carcinoma'}
    response = post_json(client, "/v1/graph/title", json_dict)
    assert response.status_code == 200
    # correct json body, no match, return 200
    json_dict = {'depth': 3, 'keyword': 'justasearchthatnotmatched'}
    response = post_json(client, "/v1/graph/title", json_dict)
    # correct json body, matched two keywords and title, return 200
    json_dict = {'depth': 3, 'title': 'liver cancer', 'keyword': 'Hepatocellular carcinoma,cancer'}
    response = post_json(client, "/v1/graph/title", json_dict)
    assert response.status_code == 200