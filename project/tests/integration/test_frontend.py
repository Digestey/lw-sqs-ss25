from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_homepage():
    response = client.get("/")
    assert response.status_code == 200
    assert "DexQuiz" in response.text
    
def test_login_frontend():
    response = client.get("/login")
    assert response.status_code == 200
    assert "login" in response.text
    
def test_register_frontend():
    response = client.get("/register")
    assert response.status_code == 200
    assert "register" in response.text