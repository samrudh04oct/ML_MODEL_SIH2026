# GramBiz AI

## Know Before You Borrow

GramBiz AI is a prototype decision-support application for rural entrepreneurs. It predicts a business viability score from historical assessment data, calculates a deterministic financing plan, recommends an indicative government scheme, and optionally asks Gemini to explain the result in simple language.

The application is split into three layers:

1. **ML model:** predicts a continuous `viability_score` from 0 to 100.
2. **Deterministic engines:** calculate loan, EMI, repayment values, and scheme routing with formulas and rules.
3. **AI explanation:** Gemini explains the computed result. Gemini does not generate the financial numbers.

## Current Output

After submission, the dashboard presents the GramBiz format:

- Location and business
- Business prediction: viability, market demand, competition, and business risk
- Financial plan: project cost, own contribution, recommended loan, EMI, revenue, and profit
- Scheme: indicative government scheme, loan limit, interest assumption, and tenure
- AI recommendation: Gemini explanation or local fallback

The output is guidance for a prototype. It is not a loan approval, subsidy guarantee, or official eligibility decision.

## Entrepreneur Inputs

The Streamlit form collects:

- Location: village, district, and state
- Business type and business scale
- Available own capital and expected investment
- Experience in business
- Family or workers available
- Land or shop availability
- Basic infrastructure availability
- Raw material or feed availability
- Previous government loan or scheme status and name
- Applicant category and gender

It also collects model assessment inputs: population, households, market distance, competitor count and density, demand index, capital adequacy, infrastructure factors, expected revenue, operating cost, profit, and risk score.

## Dataset and Model

Dataset: `ml/dataset/training_data.csv`. The latest dataset contains 900 historical records.

The model uses these numeric features:

```text
nearby_population, estimated_households, distance_to_market_km,
competitor_count, competitor_density_per_1000_households,
market_demand_index, available_capital_inr, estimated_project_cost_inr,
recommended_loan_need_inr, capital_adequacy_pct, raw_material_availability,
infrastructure_score, season_stability_score, skill_availability_score,
transport_access_score, expected_monthly_revenue_inr,
expected_monthly_operating_cost_inr, expected_monthly_profit_inr,
business_risk_score
```

Categorical features:

```text
village, district, state, business_type,
applicant_caste_category, applicant_gender
```

Target: `viability_score`.

Historical outcome fields such as `viability_class`, `government_scheme`, scheme status, prior scheme usage, and implementation agency are excluded from model predictors to reduce target leakage. They remain useful as context for analysis and future scheme evaluation.

## Training Method and Metrics

The training pipeline is in `ml/train_model.py`.

- Reads the CSV with automatic delimiter detection.
- Validates all required columns.
- Uses `ColumnTransformer` with pass-through numeric features and one-hot categorical features.
- Uses `RandomForestRegressor(n_estimators=200, max_depth=8, random_state=42)`.
- Uses an 80/20 train/test split with `random_state=42`.
- Saves the complete pipeline to `ml/model/feasibility_model.pkl`.

Latest recorded holdout metrics:

- MAE: `1.37` viability points
- R2: `0.947`

This is a regression model, so classification accuracy is not the primary metric. MAE means the average prediction error is about 1.37 points on the recorded holdout split. The dataset is prototype data and should be re-evaluated with real field data before deployment.

## Deterministic Financial Engine

The financial logic is in `app/financial_engine.py` and is intentionally separate from ML.

Implemented calculations:

- Project cost and own contribution assumptions
- Loan need as project cost minus own capital
- Monthly reducing-balance EMI
- Government scheme loan caps
- Repayment schedule with interest and principal components
- Repayment capacity and coverage band
- Working-capital allocation helper

The dashboard uses:

```text
Recommended loan = max(Expected investment - Own capital, 0)
```

The displayed EMI uses the routed scheme tenure and the selected interest assumption.

## Government Scheme Routing

Scheme routing is rule-based. Current indicative profiles include:

- MUDRA Shishu, Kishor, and Tarun
- PMEGP
- Stand-Up India
- NSFDC Micro Finance Scheme for SC/ST applicants within the prototype limit
- Karnataka Udyogini for eligible female applicants within the prototype limit
- Kisan Credit Card for agriculture-related business types

Routing considers project cost, business type, applicant category, and gender. Official eligibility, subsidy, collateral, interest rate, implementing agency, and lender terms must be verified with the relevant government department, bank, or channelizing agency.

## Gemini Explanation Layer

Gemini is used only for the explanation text. The request includes the computed viability score, demand level, competition, risk, revenue, profit, EMI, scheme, and previous scheme context. The prompt instructs Gemini not to invent facts or provide financial guarantees.

The API key is never stored in source code. Configure it in PowerShell:

```powershell
$env:GEMINI_API_KEY = "your-new-rotated-key"
```

The key previously shared in chat should be revoked and replaced. If the variable is absent or the request fails, the app uses a local fallback recommendation.

## Run the Application

From the `gramventure` directory:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

Open `http://localhost:8501` in a browser.

Retrain after replacing the dataset:

```powershell
python ml/train_model.py
```

Run the predictor smoke test:

```powershell
python ml/predict.py
```

## Project Structure

```text
gramventure/
	streamlit_app.py              Streamlit entrepreneur interface
	main.py                       FastAPI prototype endpoint
	requirements.txt              Runtime dependencies
	app/
		financial_engine.py         Loan, EMI, repayment, and scheme rules
		feasibility_engine.py       Earlier rule-based scoring helpers
		local_data.py               Local snapshot helpers
	ml/
		train_model.py              Training and evaluation pipeline
		predict.py                  Saved-model prediction function
		dataset/training_data.csv   Historical training data
		model/feasibility_model.pkl Trained pipeline artifact
	tests/                         Existing financial and feasibility tests
```

## Implementation Timeline

Timeline date note: the available implementation record places the documented work on `2026-09-03`.

### 2026-08-27 - Phase 1: Initial prototype

- Created the GramVenture FastAPI assessment endpoint.
- Added local market snapshot and rule-based feasibility helpers.
- Added project cost, loan need, scheme caps, repayment schedule, and repayment capacity calculations.

### 2026-08-29 - Phase 2: First ML interface

- Added a scikit-learn regression pipeline and saved model artifact.
- Added a Streamlit interface for entering assessment data.
- Made model loading independent of the current working directory.
- Added Streamlit to the project dependencies.

### 2026-09-03 - Phase 3: Dataset migration

- Replaced the original feature contract with the first expanded dataset schema.
- Added automatic delimiter detection for the supplied tab-delimited `.csv` file.
- Retrained and evaluated the model using a fixed holdout split.

### 2026-09-03 - Phase 4: Product flow update

- Added business prediction summaries for demand, competition, and risk.
- Added expected revenue, operating cost, profit, project cost, loan, and EMI outputs.
- Added deterministic government scheme recommendation.
- Added applicant-aware routing for category, gender, and agriculture-related businesses.

### 2026-09-03 - Phase 5: Gemini integration

- Added optional Gemini explanation generation.
- Kept viability predictions and financial calculations local and deterministic.
- Added a local fallback when no API key is configured or the API call fails.
- Documented environment-variable secret handling.

### 2026-09-03 - Phase 6: Latest dataset and entrepreneur workflow

- Updated the model for the expanded 900-record dataset.
- Added market, infrastructure, transport, skills, capital, revenue, profit, risk, applicant category, and gender features.
- Excluded historical scheme outcomes and viability class from predictors to reduce target leakage.
- Added the requested entrepreneur input fields and GramBiz output sections.
- Fixed the stale Streamlit router error by restarting the process with the updated four-argument `route_scheme` function.
- Latest recorded retraining result: MAE `1.37`, R2 `0.947`.

## Known Limitations and Next Steps

- The dataset is prototype historical data concentrated in Harohalli, Ramanagara, Karnataka; more locations are needed for generalization.
- The model predicts viability only. Demand, revenue, competition, and risk displays are currently input-derived or rule-based, not separate trained models.
- Family/workers, business scale, land/shop availability, previous scheme, and raw-material text are collected for the entrepreneur workflow; only fields in the trained feature contract affect the model prediction.
- Government scheme rules are indicative andg must be verified against current official guidelines.
- Interest rates and scheme terms are assumptions, not live bank offers.
- Production should use a server-side secrets manager, authentication, input validation, logging, rate limits, and official scheme data.
- Add automated tests for `calculate_emi`, latest schema validation, scheme routing, model prediction, and the Streamlit submission flow.
