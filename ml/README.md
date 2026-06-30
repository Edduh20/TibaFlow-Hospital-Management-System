# ML Project

## Structure
| Folder | Purpose |
|--------|---------|
| `data/` | Raw, processed, external, interim datasets |
| `notebooks/` | EDA and experimentation |
| `src/` | Modular pipeline source code |
| `artifacts/` | Encoders, scalers, train/test splits |
| `models/` | Trained model files |
| `reports/` | Figures, charts, summaries |
| `api/` | FastAPI app for serving predictions |
| `tests/` | Unit and integration tests |
| `logs/` | Runtime logs |
| `config/` | YAML config and hyperparameters |
| `deployment/` | Docker, CI/CD configs |

## Setup
```bash
pip install -r requirements.txt
python setup.py develop
```

## Run API
```bash
uvicorn api.app:app --reload
```

## Run Tests
```bash
pytest tests/
```
