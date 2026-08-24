def score_market(population, households):
    if population >= 15000:
        return 90
    elif population >= 8000:
        return 70
    else:
        return 50

def score_competition(competitor_count):
    if competitor_count <= 5:
        return 90
    elif competitor_count <= 15:
        return 65
    else:
        return 40

def score_capital_adequacy(own_capital, project_cost):
    ratio = own_capital / project_cost
    if ratio >= 0.15:
        return 85
    elif ratio >= 0.10:
        return 70
    else:
        return 50

def score_repayment_risk(coverage_ratio):
    if coverage_ratio >= 1.5:
        return 85
    elif coverage_ratio >= 1.0:
        return 60
    else:
        return 30

def overall_feasibility(market, competition, capital_adequacy, repayment_risk):
    # weights sum to 1.0 — tune later
    weights = {"market": 0.30, "competition": 0.20, "capital": 0.20, "repayment": 0.30}
    score = (market * weights["market"] + competition * weights["competition"] +
             capital_adequacy * weights["capital"] + repayment_risk * weights["repayment"])
    score = round(score)

    if score >= 70:
        verdict = "🟢 PROCEED WITH CONDITIONS" if score < 85 else "🟢 PROCEED"
    elif score >= 50:
        verdict = "🟡 MODIFY"
    else:
        verdict = "🔴 AVOID"

    return {"score": score, "verdict": verdict}