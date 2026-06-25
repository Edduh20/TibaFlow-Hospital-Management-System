import pytest
import pandas as pd

def test_dataframe_not_empty():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    assert not df.empty

def test_required_columns():
    df = pd.DataFrame({"feature1": [1.0], "feature2": [2.0], "target": [0]})
    required = ["feature1", "feature2", "target"]
    assert all(col in df.columns for col in required)
