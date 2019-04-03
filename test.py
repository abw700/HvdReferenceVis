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
# test journal response
def test_journal(client):
    response = client.get("/journal")
    assert response.status_code == 200

# test article response
def test_article(client):
    response = client.post("/article")
    assert response.status_code == 200

# test article within a period
def test_article_period(client):
    # no json body, return 400
    response = client.post("/article/period")
    assert response.status_code == 400
    # correct json body, return 200
    json_dict = {'min_year': 2015, 'max_year': 2019}
    response = post_json(client, "/article/period", json_dict)
    assert response.status_code == 200
