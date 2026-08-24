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
import os

DATA_PATH = "ml/dataset/training_data.csv"
MODEL_PATH = "ml/model/feasibility_model.pkl"

NUMERIC_FEATURES = [
    "population", "households", "competitors", "suppliers",
    "own_capital", "project_cost", "loan_amount", "interest_rate",
    "monthly_revenue", "monthly_opex", "coverage_ratio"
]
CATEGORICAL_FEATURES = ["business_type", "district"]
TARGET = "feasibility_score"

def load_dataset():
    df = pd.read_csv(DATA_PATH)
    if df.empty:
        raise ValueError(
            f"'{DATA_PATH}' has no rows yet. Populate it with historical "
            f"assessment data before training. Each row needs values for: "
            f"{NUMERIC_FEATURES + CATEGORICAL_FEATURES + [TARGET]}"
        )
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

    os.makedirs("ml/model", exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")

if __name__ == "__main__":
    train()