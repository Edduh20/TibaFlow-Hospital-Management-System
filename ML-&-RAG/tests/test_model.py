from src.prediction.predict import predict

def test_predict_returns_expected_keys():
    result = predict("itching, skin_rash, chills")
    expected_keys = {"disease", "description", "severity_score", "precautions", "medications", "diets", "workouts"}
    assert set(result.keys()) == expected_keys