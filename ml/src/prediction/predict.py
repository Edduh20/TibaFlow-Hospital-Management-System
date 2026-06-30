import pandas as pd
import numpy as np
import ast
from src.utils.helpers import load_object
from src.utils.logger import logger

model = load_object("models/Random-Forest-Model.joblib")
le = load_object("models/Label-Encoder.joblib")
training_df = pd.read_csv("data/processed/train/Training.csv", nrows=1)
diet_df = pd.read_csv("data/processed/diet/diets.csv")
medications_df = pd.read_csv("data/processed/medication/medications.csv")
description_df = pd.read_csv("data/processed/description/description.csv")
precautions_df = pd.read_csv("data/processed/precaution/precautions_df.csv", index_col=[0])
symptoms_df = pd.read_csv("data/processed/symptoms/symtoms_df.csv", index_col=[0])
symptoms_severity_df = pd.read_csv("data/processed/symptom-severity/Symptom-severity.csv")
workout_df = pd.read_csv("data/processed/workout/workout_df.csv", index_col=[0, 1])

symptom_columns = training_df.drop(columns=["prognosis"]).columns

def predict(symptoms: str) -> dict:
    symptoms_list = [s.strip() for s in symptoms.split(",")]
    input_vector = np.zeros(len(symptom_columns))
    for symptom in symptoms_list:
        index = symptom_columns.get_loc(symptom)
        input_vector[index] = 1

    input_df = pd.DataFrame([input_vector], columns=symptom_columns)
    prediction = model.predict(input_df)[0]
    disease = le.classes_[prediction]
    severity_score = symptoms_severity_df[symptoms_severity_df["Symptom"].isin(symptoms_list)]["weight"].sum()
    diets = diet_df[diet_df["Disease"] == disease]["Diet"].values[0]
    workouts = workout_df[workout_df["disease"] == disease]["workout"].tolist()
    precautions = precautions_df[precautions_df["Disease"] == disease][
        ["Precaution_1", "Precaution_2", "Precaution_3", "Precaution_4"]].values[0]
    medications = medications_df[medications_df["Disease"] == disease]["Medication"].values[0]
    description = description_df[description_df["Disease"] == disease]["Description"].values[0]

    medications = ast.literal_eval(medications)
    diets = ast.literal_eval(diets)

    return {
        "disease": disease,
        "description": description,
        "severity_score": int(severity_score),
        "precautions": precautions.tolist(),
        "medications": medications,
        "diets": diets,
        "workouts": workouts
    }
