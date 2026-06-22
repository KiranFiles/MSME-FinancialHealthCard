"""
Layer A: deterministic, rule-based sub-scores per data source.
Each function returns a 0-100 score. These are auditable and explainable,
unlike the composite ML model in model.py which learns the weighting between them.
"""


def score_gst(gst_record):
    """Compliance Consistency dimension."""
    filing_score = gst_record["filing_consistency_pct"]
    turnover = gst_record["avg_monthly_turnover"]
    # modest bonus for higher, more bankable turnover, capped
    turnover_bonus = min(turnover / 50000, 15)
    score = min(filing_score * 0.85 + turnover_bonus, 100)
    return round(score, 1)


def score_upi(upi_record):
    """Cash Flow Stability dimension."""
    active_days = upi_record["active_days_pct"]
    variance = upi_record["inflow_variance"]
    # lower variance is better; invert and scale
    variance_penalty = min(variance * 20, 40)
    score = max(active_days - variance_penalty + 20, 0)
    return round(min(score, 100), 1)


def score_aa(aa_record):
    """Digital Footprint / Account Health dimension."""
    stability = aa_record["cash_flow_stability_pct"]
    vintage_bonus = min(aa_record["account_vintage_months"] / 2, 20)
    overdraft_penalty = aa_record["overdraft_incidents_last_year"] * 5
    score = stability * 0.7 + vintage_bonus - overdraft_penalty
    return round(max(min(score, 100), 0), 1)


def score_epfo(epfo_record):
    """Workforce Stability dimension."""
    consistency = epfo_record["contribution_consistency_pct"]
    trend_bonus = {"growing": 10, "stable": 5, "declining": -10}[epfo_record["employee_count_trend"]]
    score = consistency * 0.8 + trend_bonus
    return round(max(min(score, 100), 0), 1)


def compute_sub_scores(gst_record, upi_record, aa_record, epfo_record):
    return {
        "compliance_consistency": score_gst(gst_record),
        "cash_flow_stability": score_upi(upi_record),
        "digital_footprint": score_aa(aa_record),
        "workforce_stability": score_epfo(epfo_record),
    }
