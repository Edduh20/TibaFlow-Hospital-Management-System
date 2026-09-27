import joblib, yaml, os

def save_object(file_path: str, obj):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    joblib.dump(obj, file_path)

def load_object(file_path: str):
    return joblib.load(file_path)

def load_config(path: str = "config/config.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)

def load_params(path: str = "config/params.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)
