"""
Loads the trained model and scores a single new assessment input.
"""
import joblib
import pandas as pd
from pathlib import Path

MODEL_PATH = Path(__file__).resolve().parent / "model" / "feasibility_model.pkl"

def predict_feasibility(input_dict: dict) -> float:
    pipeline = joblib.load(MODEL_PATH)
    df = pd.DataFrame([input_dict])
    score = pipeline.predict(df)[0]
    return round(float(score), 1)

if __name__ == "__main__":
    sample = {
        "village": "Harohalli", "district": "Ramanagara", "state": "Karnataka",
        "business_type": "Dairy Farming", "nearby_population": 8751,
        "estimated_households": 1907, "distance_to_market_km": 6.8,
        "competitor_count": 9, "competitor_density_per_1000_households": 4.72,
        "market_demand_index": 79, "available_capital_inr": 253402,
        "estimated_project_cost_inr": 496171, "recommended_loan_need_inr": 242769,
        "capital_adequacy_pct": 51.07, "raw_material_availability": 86,
        "infrastructure_score": 66, "season_stability_score": 75,
        "skill_availability_score": 76, "transport_access_score": 67,
        "expected_monthly_revenue_inr": 61790,
        "expected_monthly_operating_cost_inr": 44063,
        "expected_monthly_profit_inr": 17727, "business_risk_score": 23.45,
        "applicant_caste_category": "OBC", "applicant_gender": "Female"
    }
    print(predict_feasibility(sample)) 