import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.financial_engine import (
    calculate_project_cost, calculate_loan, route_scheme,
    apply_scheme_caps, working_capital_breakdown,
    repayment_schedule, repayment_capacity
)


def test_calculate_project_cost_default_margin():
    assert calculate_project_cost(100000) == 1000000.0

def test_calculate_project_cost_custom_margin():
    assert calculate_project_cost(50000, margin_pct=0.20) == 250000.0

def test_calculate_loan():
    cost = calculate_project_cost(100000)
    assert calculate_loan(cost, 100000) == 900000.0

def test_route_scheme_micro_finance():
    scheme = route_scheme(140000)
    assert scheme["name"] == "Micro Finance"

def test_route_scheme_term_loan():
    scheme = route_scheme(1000000)
    assert scheme["name"] == "Term Loan"

def test_apply_scheme_caps_within_limits():
    cost = calculate_project_cost(100000)
    loan = calculate_loan(cost, 100000)
    scheme = route_scheme(cost)
    capped_cost, capped_loan, was_capped = apply_scheme_caps(cost, loan, scheme)
    assert capped_cost == 1000000.0
    assert capped_loan == 900000.0
    assert was_capped is False

def test_apply_scheme_caps_edge_case_exceeds_limit():
    # ₹6L own capital → ₹60L project cost, but Term Loan caps at ₹50L / ₹45L
    cost = calculate_project_cost(600000)
    loan = calculate_loan(cost, 600000)
    scheme = route_scheme(cost)
    capped_cost, capped_loan, was_capped = apply_scheme_caps(cost, loan, scheme)
    assert cost == 6000000.0
    assert loan == 5400000.0
    assert capped_cost == 5000000.0
    assert capped_loan == 4500000.0
    assert was_capped is True

def test_working_capital_breakdown_sums_close_to_total():
    breakdown = working_capital_breakdown(1000000, "dairy")
    total = sum(breakdown.values())
    assert abs(total - 1000000) < 1  # allow rounding drift

def test_working_capital_breakdown_keys():
    breakdown = working_capital_breakdown(1000000, "dairy")
    expected_keys = {"livestock", "infrastructure", "equipment",
                      "initial_feed", "working_capital", "emergency_reserve"}
    assert set(breakdown.keys()) == expected_keys

def test_repayment_schedule_length():
    schedule = repayment_schedule(900000, 8.0, tenure_years=7,
                                   moratorium_months=6, frequency="quarterly")
    assert len(schedule) == 28  # 7 years * 4 quarters

def test_repayment_schedule_moratorium_has_no_principal():
    schedule = repayment_schedule(900000, 8.0, tenure_years=7,
                                   moratorium_months=6, frequency="quarterly")
    # 6 months moratorium = 2 quarters with zero principal due
    assert schedule[0]["principal"] == 0
    assert schedule[1]["principal"] == 0
    assert schedule[2]["principal"] > 0

def test_repayment_schedule_balance_reaches_zero():
    schedule = repayment_schedule(900000, 8.0, tenure_years=7,
                                   moratorium_months=6, frequency="quarterly")
    assert schedule[-1]["closing"] == 0

def test_repayment_capacity_comfortable():
    result = repayment_capacity(monthly_revenue=50000, monthly_opex=20000,
                                 monthly_debt_obligation=15000)
    assert result["band"] == "🟢 Comfortable"

def test_repayment_capacity_high_risk():
    result = repayment_capacity(monthly_revenue=20000, monthly_opex=18000,
                                 monthly_debt_obligation=5000)
    assert result["band"] == "🔴 High risk"

def test_repayment_capacity_moderate():
    result = repayment_capacity(monthly_revenue=30000, monthly_opex=15000,
                                 monthly_debt_obligation=13000)
    assert result["band"] == "🟡 Moderate"