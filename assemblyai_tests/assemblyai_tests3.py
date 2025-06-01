from fastapi.testclient import TestClient
# Import the app and ml_models from your app.py
from assemblyai_tests2 import app, ml_models

# Initialize the TestClient with your FastAPI app
client = TestClient(app)


def test_predict_valid_input():
    with TestClient(app) as client:
        # Send a GET request to /predict with x=2.0
        response = client.get("/predict", params={"x": 2.0})
        assert response.status_code == 200  # Check for successful response
        assert response.json() == {"result": 84.0}  # 2.0 * 42 = 84.0


def test_predict_zero_input():
    with TestClient(app) as client:
        response = client.get("/predict", params={"x": 0.0})
        assert response.status_code == 200
        assert response.json() == {"result": 0.0}  # 0.0 * 42 = 0.0


def test_predict_negative_input():
    with TestClient(app) as client:
        response = client.get("/predict", params={"x": -1.0})
        assert response.status_code == 200
        assert response.json() == {"result": -42.0}  # -1.0 * 42 = -42.0


def test_predict_missing_input():
    with TestClient(app) as client:
        # Send a request without the required x parameter
        response = client.get("/predict")
        # Expect validation error (Unprocessable Entity)
        assert response.status_code == 422


def test_predict_invalid_input():
    with TestClient(app) as client:
        # Send a request with a non-float value for x
        response = client.get("/predict", params={"x": "not_a_number"})
        assert response.status_code == 422  # Expect validation error


def test_lifespan():
    # Test that lifespan events work correctly
    with TestClient(app) as client:
        # Inside the with block, the model should be loaded
        assert "answer_to_everything" in ml_models
        assert ml_models["answer_to_everything"](
            2.0) == 84.0  # Verify the model works
    # After the with block, ml_models should be cleared
    assert ml_models == {}


test_lifespan()
