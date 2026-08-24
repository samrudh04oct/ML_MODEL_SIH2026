"""
Loads the trained model and scores a single new assessment input.
"""
import joblib
import pandas as pd

MODEL_PATH = "ml/model/feasibility_model.pkl"

def predict_feasibility(input_dict: dict) -> float:
    pipeline = joblib.load(MODEL_PATH)
    df = pd.DataFrame([input_dict])
    score = pipeline.predict(df)[0]
    return round(float(score), 1)

if __name__ == "__main__":
    sample = {
        "population": 18000, "households": 4500, "competitors": 14, "suppliers": 7,
        "own_capital": 100000, "project_cost": 1000000, "loan_amount": 900000,
        "interest_rate": 8.0, "monthly_revenue": 20000, "monthly_opex": 12000,
        "coverage_ratio": 1.2, "business_type": "dairy", "district": "Ramanagara"
    }
    print(predict_feasibility(sample)) 