from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_get_top_cryptos():
    response = client.get("/top-cryptos?limit=5")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert len(response.json()) <= 5


def test_get_influencers():
    response = client.get("/influencers")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_analyse_influencer():
    response = client.get("/analyse/elonmusk")
    assert response.status_code == 200
    assert "profile" in response.json()


def test_analyse_multiple():
    response = client.post("/analyse-multiple", params={"usernames": ["elonmusk", "VitalikButerin"]})
    assert response.status_code == 200
    assert "individual_analyses" in response.json()
