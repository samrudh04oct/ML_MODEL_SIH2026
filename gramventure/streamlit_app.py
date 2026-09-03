from pathlib import Path
import json
import os
from urllib.request import Request, urlopen

import pandas as pd
import streamlit as st

from ml.predict import predict_feasibility
from app.financial_engine import calculate_emi, route_scheme


st.set_page_config(
    page_title="GramVenture | Feasibility Studio",
    page_icon="GV",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;600;700;800&display=swap');
    :root { --ink: #16211d; --muted: #60706a; --cream: #f6f4ed; --green: #0f7a5a; --coral: #e56b4e; }
    html, body, [class*="css"] { font-family: 'Manrope', sans-serif; color: var(--ink); }
    .stApp { background: var(--cream); }
    [data-testid="stSidebar"] { background: #172b25; }
    [data-testid="stSidebar"] * { color: #edf4ec !important; }
    .eyebrow { font-family: 'DM Mono', monospace; color: var(--coral); font-size: .75rem; letter-spacing: .08em; text-transform: uppercase; }
    h1 { font-size: clamp(2.2rem, 5vw, 4.4rem) !important; line-height: .98 !important; letter-spacing: -0.04em; margin: .25rem 0 1rem !important; }
    h2 { letter-spacing: -0.03em; }
    .intro { color: var(--muted); max-width: 620px; font-size: 1.05rem; line-height: 1.6; margin-bottom: 2rem; }
    .result { padding: 1.5rem; border: 1px solid #dce3db; background: white; border-radius: 8px; margin-top: 1rem; }
    .score { font-size: 4.8rem; font-weight: 800; line-height: 1; letter-spacing: -0.06em; color: var(--green); }
    .score-label { font-family: 'DM Mono', monospace; color: var(--muted); font-size: .75rem; text-transform: uppercase; }
    .verdict { font-size: 1.5rem; font-weight: 800; margin-top: .5rem; }
    .caption { color: var(--muted); font-size: .85rem; }
    div[data-testid="stMetric"] { background: white; border: 1px solid #dce3db; padding: 1rem; border-radius: 8px; }
    </style>
    """,
    unsafe_allow_html=True,
)


def money(value: float) -> str:
    return f"₹{value:,.0f}"


def gemini_explanation(result: dict) -> str | None:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None

    prompt = (
        "Explain this rural business feasibility assessment in two concise sentences. "
        "Mention the strongest positive factor and the main risk. Do not invent facts, "
        "do not give legal or financial guarantees, and do not use markdown.\n\n"
        f"Assessment data: {json.dumps(result)}"
    )
    payload = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8")
    request = Request(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=" + api_key,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception:
        return None


st.markdown('<div class="eyebrow">GramVenture / Model interface</div>', unsafe_allow_html=True)
st.title("Is this venture built to last?")
st.markdown(
    '<p class="intro">Turn a village business idea into a feasibility signal. Adjust the local market, capital, and repayment assumptions, then let the trained model score the opportunity.</p>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### Assessment inputs")
    st.caption("Use values from your local survey or business plan.")
    village = st.text_input("Village", "Harohalli")
    district = st.text_input("District", "Ramanagara")
    state = st.text_input("State", "Karnataka")
    business_type = st.selectbox("Business type", ["Goat Farming", "Vegetable Retail", "Dairy Farming", "Poultry Farming", "Grocery Store", "Mobile Repair", "Agri Input Store", "Fruit & Vegetable Farming", "Handicraft/Handloom", "Tailoring", "Two-Wheeler Repair", "Food Stall", "Small Bakery"])
    business_scale = st.selectbox("Business scale", ["Small", "Medium", "Large"])
    experience_years = st.number_input("Experience in business (years)", min_value=0, value=2, step=1)
    family_workers = st.number_input("Family/workers available", min_value=0, value=2, step=1)
    land_or_shop = st.selectbox("Land/shop available?", ["Yes", "No"])
    infrastructure_available = st.selectbox("Basic infrastructure available?", ["Yes", "No"])
    raw_material_level = st.selectbox("Raw material/feed availability", ["Easily Available", "Available", "Limited", "Not Available"])
    caste_category = st.selectbox("Applicant category", ["General", "OBC", "SC", "ST", "Not Disclosed"])
    gender = st.selectbox("Applicant gender", ["Female", "Male", "Other/Not Disclosed"])
    previous_scheme_availed = st.selectbox("Previous government scheme availed?", ["Yes", "No"])
    previous_scheme_name = st.text_input("Previous scheme name", "NSFDC Term Loan")

    st.markdown("#### Local market")
    population = st.number_input("Nearby population", min_value=0, value=11247, step=500)
    households = st.number_input("Estimated households", min_value=0, value=2649, step=100)
    competitors = st.number_input("Competitor count", min_value=0, value=16, step=1)
    competitor_density = st.number_input("Competitor density / 1,000 households", min_value=0.0, value=6.04, step=0.1)
    distance_to_market_km = st.number_input("Distance to market (km)", min_value=0.0, value=0.71, step=0.1)
    demand_score = st.slider("Market demand index", min_value=0, max_value=100, value=71)
    raw_material = {"Easily Available": 90, "Available": 75, "Limited": 45, "Not Available": 15}[raw_material_level]
    infrastructure = 90 if infrastructure_available == "Yes" else 30
    seasonality_score = st.slider("Season stability score", min_value=0, max_value=100, value=68)
    skill_availability = st.slider("Skill availability score", min_value=0, max_value=100, value=73)
    transport_access = st.slider("Transport access score", min_value=0, max_value=100, value=67)

    st.markdown("#### Financial plan")
    available_capital = st.number_input("Available capital (INR)", min_value=0.0, value=43546.0, step=10000.0)
    project_cost_input = st.number_input("Expected investment (INR)", min_value=0.0, value=300000.0, step=10000.0)
    capital_adequacy = st.number_input("Capital adequacy (%)", min_value=0.0, value=12.25, step=1.0)
    monthly_revenue_input = st.number_input("Expected monthly revenue (INR)", min_value=0.0, value=52952.0, step=1000.0)
    operating_cost = st.number_input("Expected monthly operating cost (INR)", min_value=0.0, value=35890.0, step=1000.0)
    monthly_profit = st.number_input("Expected monthly profit (INR)", min_value=0.0, value=15000.0, step=1000.0)
    business_risk = st.number_input("Business risk score", min_value=0.0, max_value=100.0, value=29.22, step=1.0)
    interest_rate = st.number_input("Interest rate (%)", min_value=0.0, value=8.0, step=0.5)
    run_assessment = st.button("Run assessment", type="primary", use_container_width=True)

if run_assessment:
    model_input = {
        "village": village, "district": district, "state": state, "business_type": business_type,
        "nearby_population": population, "estimated_households": households,
        "distance_to_market_km": distance_to_market_km, "competitor_count": competitors,
        "competitor_density_per_1000_households": competitor_density, "market_demand_index": demand_score,
        "available_capital_inr": available_capital, "estimated_project_cost_inr": project_cost_input,
        "recommended_loan_need_inr": max(project_cost_input - available_capital, 0), "capital_adequacy_pct": capital_adequacy,
        "raw_material_availability": raw_material, "infrastructure_score": infrastructure,
        "season_stability_score": seasonality_score, "skill_availability_score": skill_availability,
        "transport_access_score": transport_access, "expected_monthly_revenue_inr": monthly_revenue_input,
        "expected_monthly_operating_cost_inr": operating_cost, "expected_monthly_profit_inr": monthly_profit,
        "business_risk_score": business_risk, "applicant_caste_category": caste_category,
        "applicant_gender": gender, "business_experience_years": experience_years,
    }
    try:
        score = predict_feasibility(model_input)
        viability_class = "HIGHLY VIABLE" if score >= 80 else "VIABLE" if score >= 60 else "MODERATELY VIABLE"
        if score >= 70:
            verdict, color, guidance = "PROCEED", "#0f7a5a", "The model sees a strong base for this venture. Validate the assumptions before committing capital."
        elif score >= 50:
            verdict, color, guidance = "MODIFY", "#c47b21", "The opportunity has potential, but one or more assumptions need strengthening."
        else:
            verdict, color, guidance = "AVOID", "#c34f42", "The current plan carries substantial feasibility risk. Rework the fundamentals before proceeding."

        st.markdown("<div class='eyebrow'>GRAMBIZ AI / KNOW BEFORE YOU BORROW</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='result'><div class='score' style='color:{color}'>{score:.1f}<span class='score-label'> / 100</span></div><div class='verdict' style='color:{color}'>{viability_class}</div><div class='caption'>{guidance}</div></div>",
            unsafe_allow_html=True,
        )
        st.write("")
        scheme = route_scheme(project_cost_input, business_type, caste_category, gender)
        project_cost = min(project_cost_input, scheme["max_cost"])
        loan = min(max(project_cost - available_capital, 0), scheme["max_loan"])
        emi = calculate_emi(loan, interest_rate, scheme["tenure_years"])
        monthly_revenue = monthly_revenue_input
        surplus = monthly_revenue - operating_cost
        competition_level = "LOW" if competitors <= 3 else "MEDIUM" if competitors <= 7 else "HIGH"
        risk_level = "LOW" if score >= 70 and surplus >= emi else "MEDIUM" if score >= 50 else "HIGH"

        first, second, third = st.columns(3)
        first.metric("Location", village or "Unnamed village")
        second.metric("Business", business_type)
        third.metric("Capital", money(available_capital))

        st.markdown("### BUSINESS PREDICTION")
        prediction_one, prediction_two, prediction_three, prediction_four = st.columns(4)
        prediction_one.metric("Market demand index", f"{demand_score}/100")
        prediction_two.metric("Demand level", "HIGH" if demand_score >= 70 else "MEDIUM" if demand_score >= 45 else "LOW")
        prediction_three.metric("Competition", competition_level)
        prediction_four.metric("Business risk", risk_level)

        st.markdown("### FINANCIAL PLAN")
        finance_one, finance_two, finance_three, finance_four = st.columns(4)
        finance_one.metric("Project cost", money(project_cost))
        finance_two.metric("Own contribution", money(available_capital))
        finance_three.metric("Recommended loan", money(loan))
        finance_four.metric("Estimated EMI", money(emi) + "/mo")
        st.caption(f"Expected Revenue: {money(monthly_revenue)}/month | Expected Profit: {money(monthly_profit)}/month")

        st.markdown("### SCHEME")
        funding_pct = (loan / project_cost * 100) if project_cost else 0
        st.info(f"Recommended government scheme: **{scheme['name']}**\n\nFunding: {funding_pct:.0f}% | Interest: {scheme['interest']:.1f}% | Tenure: {scheme['tenure_years']} years")
        st.caption("Prototype guidance only. Final eligibility, subsidy, interest rate, collateral, and lender terms depend on applicant category, business type, location, and official scheme guidelines.")

        st.markdown("### AI RECOMMENDATION")
        assessment_summary = {
            "location": village, "business": business_type, "viability_score": score,
            "demand_level": "HIGH" if demand_score >= 70 else "MEDIUM" if demand_score >= 45 else "LOW",
            "competition": competition_level, "risk": risk_level,
            "monthly_revenue": monthly_revenue, "monthly_profit": monthly_profit, "monthly_emi": emi,
            "scheme": scheme["name"], "previous_scheme": previous_scheme_name if previous_scheme_availed == "Yes" else "None",
        }
        explanation = gemini_explanation(assessment_summary)
        if explanation is None and score >= 70 and surplus >= emi:
            explanation = f"{business_type} is highly viable at {village}. Demand is strong and the projected surplus can support the estimated EMI."
        elif explanation is None and score >= 50:
            explanation = "This opportunity has potential, but strengthen demand, pricing, or operating costs before borrowing."
        elif explanation is None:
            explanation = "The current assumptions indicate high feasibility risk. Rework the market and capital plan before proceeding."
        st.success(explanation)

        with st.expander("Review submitted assumptions"):
            st.dataframe(pd.DataFrame([model_input]), use_container_width=True, hide_index=True)
    except FileNotFoundError:
        st.error("Model file not found. Train the model first with `python ml/train_model.py`.")
    except Exception as error:
        st.error(f"The assessment could not be completed: {error}")
else:
    st.info("Set your assumptions in the sidebar, then run the assessment.")