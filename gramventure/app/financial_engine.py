def calculate_project_cost(own_capital: float, margin_pct: float = 0.10) -> float:
    """Own capital is treated as the margin contribution (default 10%)."""
    return round(own_capital / margin_pct, 2)

def calculate_loan(project_cost: float, own_capital: float) -> float:
    return round(project_cost - own_capital, 2)

# Simple scheme table (expand later from real scheme PDFs)
SCHEMES = [
    {"name": "Micro Finance", "min_cost": 0, "max_cost": 140000, "max_loan": 126000,
     "interest": 7.0, "tenure_years": 5, "moratorium_months": 3},
    {"name": "Term Loan", "min_cost": 140000, "max_cost": 5000000, "max_loan": 4500000,
     "interest": 8.0, "tenure_years": 7, "moratorium_months": 6},
]

def route_scheme(project_cost: float) -> dict:
    for scheme in SCHEMES:
        if scheme["min_cost"] < project_cost <= scheme["max_cost"]:
            return scheme
    # falls above all defined schemes
    return SCHEMES[-1]  # cap at largest scheme, flag separately

def apply_scheme_caps(project_cost, loan, scheme):
    capped_cost = min(project_cost, scheme["max_cost"])
    capped_loan = min(loan, scheme["max_loan"])
    was_capped = (capped_cost < project_cost) or (capped_loan < loan)
    return capped_cost, capped_loan, was_capped

def working_capital_breakdown(project_cost: float, business_type: str = "dairy") -> dict:
    # Simple % allocation — replace with business-specific tables later
    allocations = {
        "livestock": 0.35, "infrastructure": 0.20, "equipment": 0.15,
        "initial_feed": 0.10, "working_capital": 0.12, "emergency_reserve": 0.08,
    }
    return {k: round(project_cost * v, 2) for k, v in allocations.items()}

def repayment_schedule(loan, interest_pct, tenure_years, moratorium_months, frequency="quarterly"):
    periods_per_year = {"quarterly": 4, "monthly": 12, "annually": 1}[frequency]
    total_periods = tenure_years * periods_per_year
    moratorium_periods = round(moratorium_months / (12 / periods_per_year))
    repay_periods = total_periods - moratorium_periods
    principal_per_period = round(loan / repay_periods, 2)
    rate_per_period = interest_pct / 100 / periods_per_year

    schedule = []
    balance = loan
    for p in range(1, total_periods + 1):
        interest_due = round(balance * rate_per_period, 2)
        if p <= moratorium_periods:
            principal_due = 0
        elif p == total_periods:
            principal_due = round(balance, 2)
        else:
            principal_due = round(min(principal_per_period, balance), 2)
        payment = interest_due + principal_due
        balance = round(balance - principal_due, 2)
        schedule.append({
            "period": p, "opening": balance + principal_due, "interest": interest_due,
            "principal": principal_due, "payment": round(payment, 2), "closing": balance
        })
    return schedule

def repayment_capacity(monthly_revenue, monthly_opex, monthly_debt_obligation):
    net_cash = monthly_revenue - monthly_opex
    if monthly_debt_obligation == 0:
        ratio = float("inf")
    else:
        ratio = net_cash / monthly_debt_obligation
    if ratio >= 1.5:
        band = "🟢 Comfortable"
    elif ratio >= 1.0:
        band = "🟡 Moderate"
    else:
        band = "🔴 High risk"
    return {"net_cash": round(net_cash, 2), "coverage_ratio": round(ratio, 2), "band": band}


if __name__ == "__main__":
    cost = calculate_project_cost(100000)
    loan = calculate_loan(cost, 100000)
    scheme = route_scheme(cost)
    capped_cost, capped_loan, capped = apply_scheme_caps(cost, loan, scheme)
    print(cost, loan, scheme["name"], capped_cost, capped_loan, capped)
    # Expect: 1000000.0 900000.0 Term Loan 1000000.0 900000.0 False

    cost2 = calculate_project_cost(600000)
    loan2 = calculate_loan(cost2, 600000)
    scheme2 = route_scheme(cost2)
    capped_cost2, capped_loan2, capped2 = apply_scheme_caps(cost2, loan2, scheme2)
    print(cost2, loan2, scheme2["name"], capped_cost2, capped_loan2, capped2)
    # Expect: 6000000.0 5400000.0 Term Loan 5000000.0 4500000.0 True