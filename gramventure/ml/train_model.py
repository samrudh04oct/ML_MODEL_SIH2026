"""
Trains a feasibility-prediction model from historical assessment data.
Dataset must be populated in ml/dataset/training_data.csv before running.
"""
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "dataset" / "training_data.csv"
MODEL_PATH = BASE_DIR / "model" / "feasibility_model.pkl"

NUMERIC_FEATURES = [
    "nearby_population", "estimated_households", "distance_to_market_km",
    "competitor_count", "competitor_density_per_1000_households",
    "market_demand_index", "available_capital_inr", "estimated_project_cost_inr",
    "recommended_loan_need_inr", "capital_adequacy_pct", "raw_material_availability",
    "infrastructure_score", "season_stability_score", "skill_availability_score",
    "transport_access_score", "expected_monthly_revenue_inr",
    "expected_monthly_operating_cost_inr", "expected_monthly_profit_inr",
    "business_risk_score"
]
CATEGORICAL_FEATURES = ["village", "district", "state", "business_type",
                        "applicant_caste_category", "applicant_gender"]
TARGET = "viability_score"

def load_dataset():
    df = pd.read_csv(DATA_PATH, sep=None, engine="python")
    if df.empty:
        raise ValueError(
            f"'{DATA_PATH}' has no rows yet. Populate it with historical "
            f"assessment data before training. Each row needs values for: "
            f"{NUMERIC_FEATURES + CATEGORICAL_FEATURES + [TARGET]}"
        )
    required_columns = NUMERIC_FEATURES + CATEGORICAL_FEATURES + [TARGET]
    missing_columns = [column for column in required_columns if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    return df

def build_pipeline():
    preprocessor = ColumnTransformer(transformers=[
        ("num", "passthrough", NUMERIC_FEATURES),
        ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
    ])
    model = RandomForestRegressor(n_estimators=200, max_depth=8, random_state=42)
    return Pipeline([("preprocess", preprocessor), ("model", model)])

def train():
    df = load_dataset()
    X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    preds = pipeline.predict(X_test)
    print(f"MAE: {mean_absolute_error(y_test, preds):.2f}")
    print(f"R2:  {r2_score(y_test, preds):.3f}")

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")

if __name__ == "__main__":
    train()