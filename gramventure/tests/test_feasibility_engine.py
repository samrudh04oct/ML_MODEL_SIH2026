import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.feasibility_engine import (
    score_market, score_competition, score_capital_adequacy,
    score_repayment_risk, overall_feasibility
)


def test_score_market_high_population():
    assert score_market(18000, 4500) == 90

def test_score_market_medium_population():
    assert score_market(10000, 2500) == 70

def test_score_market_low_population():
    assert score_market(5000, 1200) == 50

def test_score_competition_low():
    assert score_competition(3) == 90

def test_score_competition_moderate():
    assert score_competition(14) == 65

def test_score_competition_high():
    assert score_competition(20) == 40

def test_score_capital_adequacy_strong():
    # A 15% contribution meets the strong-capital threshold.
    assert score_capital_adequacy(150000, 1000000) == 85

def test_score_capital_adequacy_moderate():
    assert score_capital_adequacy(100000, 1000000) == 70  # ratio = 0.10

def test_score_capital_adequacy_weak():
    assert score_capital_adequacy(50000, 1000000) == 50  # ratio = 0.05

def test_score_repayment_risk_low_risk():
    assert score_repayment_risk(1.6) == 85

def test_score_repayment_risk_moderate():
    assert score_repayment_risk(1.1) == 60

def test_score_repayment_risk_high():
    assert score_repayment_risk(0.7) == 30

def test_overall_feasibility_proceed_with_conditions():
    result = overall_feasibility(market=90, competition=65,
                                  capital_adequacy=70, repayment_risk=60)
    assert result["score"] == 72
    assert result["verdict"] == "🟢 PROCEED WITH CONDITIONS"

def test_overall_feasibility_avoid():
    result = overall_feasibility(market=50, competition=40,
                                  capital_adequacy=50, repayment_risk=30)
    assert result["score"] < 50
    assert result["verdict"] == "🔴 AVOID"

def test_overall_feasibility_proceed_clean():
    result = overall_feasibility(market=90, competition=90,
                                  capital_adequacy=85, repayment_risk=85)
    assert result["score"] >= 85
    assert result["verdict"] == "🟢 PROCEED"