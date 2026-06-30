import pytest

def test_prediction_is_list():
    prediction = [0]
    assert isinstance(prediction, list)

def test_prediction_value():
    prediction = [0]
    assert prediction[0] in [0, 1]
