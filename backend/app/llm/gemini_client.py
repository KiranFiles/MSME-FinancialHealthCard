"""
Calls Gemini API to generate a strengths/risks narrative from an already
computed score. The LLM never computes or alters the score itself -- it only
explains a number that has already been produced deterministically by
rules.py and model.py. This separation is intentional and should be stated
explicitly in the pitch: the model scores, the LLM narrates.
"""

import os
import json
import urllib.request

GEMINI_BASE_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash:generateContent?key="
)


def generate_narrative(business_name, sub_scores, composite_score, source_records):
    # Read the key here, at call time, not at module load time.
    # This means restarting uvicorn after setting the env var is enough --
    # no code change needed. Previously the key was baked into GEMINI_URL
    # at import time, so setting it after startup had no effect.
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()

    if not api_key:
        return _fallback_narrative(sub_scores, composite_score)

    prompt = (
        f"You are a credit underwriting assistant at an Indian bank evaluating "
        f"an MSME loan application using alternate data only (no traditional "
        f"financial documents available). "
        f"Business name: {business_name}. "
        f"Composite financial health score: {composite_score}/100. "
        f"Dimension scores out of 100: "
        f"Compliance Consistency (GST filing regularity): {sub_scores['compliance_consistency']}, "
        f"Cash Flow Stability (UPI transaction consistency): {sub_scores['cash_flow_stability']}, "
        f"Digital Footprint (Account Aggregator bank data): {sub_scores['digital_footprint']}, "
        f"Workforce Stability (EPFO contribution history): {sub_scores['workforce_stability']}. "
        f"Raw data signals: "
        f"GST filing consistency: {source_records['gst']['filing_consistency_pct']}%, "
        f"GST late filings in last 12 months: {source_records['gst']['late_filings_count']}, "
        f"UPI active transaction days: {source_records['upi']['active_days_pct']}%, "
        f"UPI inflow variance: {source_records['upi']['inflow_variance']}, "
        f"Bank cash flow stability: {source_records['aa']['cash_flow_stability_pct']}%, "
        f"Overdraft incidents last year: {source_records['aa']['overdraft_incidents_last_year']}, "
        f"EPFO contribution consistency: {source_records['epfo']['contribution_consistency_pct']}%, "
        f"Employee count trend: {source_records['epfo']['employee_count_trend']}. "
        f"Write exactly 2 strengths and 2 risks. "
        f"Each point must reference a specific data signal from above with its actual number. "
        f"Use plain underwriting language a credit officer would write in a loan file. "
        f"Format exactly as:\n"
        f"Strengths:\n- [point 1]\n- [point 2]\n\nRisks:\n- [point 1]\n- [point 2]\n"
        f"No preamble, no extra text outside this format."
    )

    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 300,
        }
    }).encode("utf-8")

    url = GEMINI_BASE_URL + api_key
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            return text.strip()
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        return _fallback_narrative(
            sub_scores, composite_score,
            error=f"Gemini HTTP {e.code}: {error_body[:200]}"
        )
    except Exception as e:
        return _fallback_narrative(sub_scores, composite_score, error=str(e))


def _fallback_narrative(sub_scores, composite_score, error=None):
    """
    Used when no API key is set or the Gemini call fails.
    Produces a rule-based narrative so the demo never breaks.
    The error reason is not shown to the user but is logged here for debugging.
    """
    if error:
        print(f"[gemini_client] Falling back to rule-based narrative. Reason: {error}")

    strengths = []
    risks = []

    if sub_scores["compliance_consistency"] >= 65:
        strengths.append(
            f"GST filing consistency of {sub_scores['compliance_consistency']}/100 "
            f"reflects strong regulatory discipline and reliable tax compliance."
        )
    if sub_scores["cash_flow_stability"] >= 65:
        strengths.append(
            f"UPI-based cash flow stability score of {sub_scores['cash_flow_stability']}/100 "
            f"indicates predictable, consistent day-to-day revenue inflow."
        )
    if sub_scores["workforce_stability"] >= 65:
        strengths.append(
            f"EPFO contribution consistency score of {sub_scores['workforce_stability']}/100 "
            f"signals a stable and growing workforce, indicating operational continuity."
        )
    if sub_scores["digital_footprint"] >= 65:
        strengths.append(
            f"Account Aggregator digital footprint score of {sub_scores['digital_footprint']}/100 "
            f"reflects a well-established and active banking relationship."
        )

    if sub_scores["compliance_consistency"] < 50:
        risks.append(
            f"GST compliance score of {sub_scores['compliance_consistency']}/100 is below "
            f"acceptable threshold, indicating irregular or late GST filings that raise "
            f"regulatory risk concerns."
        )
    elif sub_scores["compliance_consistency"] < 65:
        risks.append(
            f"GST compliance score of {sub_scores['compliance_consistency']}/100 is marginal — "
            f"occasional late filings noted, requiring monitoring."
        )

    if sub_scores["cash_flow_stability"] < 50:
        risks.append(
            f"Cash flow stability score of {sub_scores['cash_flow_stability']}/100 is weak, "
            f"with high UPI inflow variance suggesting unpredictable or seasonal revenue patterns."
        )
    elif sub_scores["cash_flow_stability"] < 65:
        risks.append(
            f"Cash flow stability score of {sub_scores['cash_flow_stability']}/100 is moderate — "
            f"some inflow variability observed, which may affect repayment consistency."
        )

    if sub_scores["digital_footprint"] < 50:
        risks.append(
            f"Digital footprint score of {sub_scores['digital_footprint']}/100 is low, "
            f"indicating overdraft incidents or limited account history that reduces "
            f"confidence in cash buffer availability."
        )

    if sub_scores["workforce_stability"] < 50:
        risks.append(
            f"Workforce stability score of {sub_scores['workforce_stability']}/100 suggests "
            f"declining employee count or irregular EPFO contributions, signalling "
            f"possible operational contraction."
        )

    if not strengths:
        strengths.append(
            f"Composite score of {composite_score}/100 reflects a baseline presence "
            f"across all four alternate data sources."
        )
        strengths.append(
            "Business is registered and transacting digitally, providing a foundation "
            "for alternate-data-based credit evaluation."
        )

    if not risks:
        risks.append(
            f"No material risk flags identified across GST, UPI, AA, and EPFO signals "
            f"at the current composite score of {composite_score}/100."
        )
        risks.append(
            "Recommend standard loan officer review to validate alternate-data findings "
            "against any available informal financial records."
        )

    return (
        "Strengths:\n- " + "\n- ".join(strengths[:2]) +
        "\n\nRisks:\n- " + "\n- ".join(risks[:2])
    )
