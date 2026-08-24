from fastapi import FastAPI
from pydantic import BaseModel
from app.financial_engine import (calculate_project_cost, calculate_loan, route_scheme,
                                   apply_scheme_caps, working_capital_breakdown,
                                   repayment_schedule, repayment_capacity)
from app.feasibility_engine import (score_market, score_competition,
                                     score_capital_adequacy, score_repayment_risk,
                                     overall_feasibility)
from app.local_data import get_local_snapshot

app = FastAPI()

class AssessmentRequest(BaseModel):
    village: str
    business: str
    capital: float
    language: str = "english"

@app.post("/assess")
def assess(req: AssessmentRequest):
    local = get_local_snapshot(req.village, req.business)

    project_cost = calculate_project_cost(req.capital)
    loan = calculate_loan(project_cost, req.capital)
    scheme = route_scheme(project_cost)
    capped_cost, capped_loan, was_capped = apply_scheme_caps(project_cost, loan, scheme)
    working_capital = working_capital_breakdown(capped_cost, req.business)

    # placeholder revenue/opex assumptions — replace with business-specific model
    monthly_revenue = capped_cost * 0.02
    monthly_opex = capped_cost * 0.012
    monthly_debt = (capped_loan * scheme["interest"] / 100) / 12
    affordability = repayment_capacity(monthly_revenue, monthly_opex, monthly_debt)

    scores = {
        "market": score_market(local["population"], local["households"]),
        "competition": score_competition(local["competitors"]),
        "capital_adequacy": score_capital_adequacy(req.capital, capped_cost),
        "repayment_risk": score_repayment_risk(affordability["coverage_ratio"]),
    }
    feasibility = overall_feasibility(scores["market"], scores["competition"],
                                       scores["capital_adequacy"], scores["repayment_risk"])

    return {
        "local_snapshot": local,
        "financial": {
            "project_cost": capped_cost, "loan": capped_loan,
            "scheme_applied": scheme["name"], "was_capped": was_capped,
            "working_capital": working_capital,
        },
        "affordability": affordability,
        "scores": scores,
        "feasibility": feasibility,
    }