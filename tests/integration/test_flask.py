import pytest

from app import app


@pytest.fixture
def client():
    """Fixture pour configurer un client de test Flask"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_index(client):
    """Test index page"""
    response = client.get('/')
    assert response.status_code == 200


def test_gestionnaire_parties(client):
    response = client.get('/parties')
    assert response.status_code == 200
