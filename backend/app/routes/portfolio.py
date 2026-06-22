import random
from fastapi import APIRouter, HTTPException
from app import data_store
from app.scoring.rules import compute_sub_scores
from app.scoring.model import compute_composite_score

router = APIRouter()


@router.get("/portfolio")
def get_portfolio():
    """
    Returns all businesses that have been scored so far, plus aggregate
    portfolio stats (average score, percent flagged high-risk). If a business
    has not yet been scored in this session, it is scored now using its
    default consented-all-sources state so the portfolio view is always full
    for demo purposes.
    """
    all_businesses = data_store.get_all_businesses()
    rows = []

    for b in all_businesses:
        msme_id = b["msme_id"]
        cached = data_store.get_cached_score(msme_id)
        if not cached:
            records = data_store.get_source_records(msme_id)
            sub_scores = compute_sub_scores(records["gst"], records["upi"], records["aa"], records["epfo"])
            composite_score, learned_weights = compute_composite_score(sub_scores)
            cached = {
                "msme_id": msme_id,
                "business_name": b["business_name"],
                "sub_scores": sub_scores,
                "composite_score": composite_score,
                "learned_weights": learned_weights,
            }
            data_store.cache_score(msme_id, cached)
            cached = data_store.get_cached_score(msme_id)

        rows.append({
            "msme_id": msme_id,
            "business_name": b["business_name"],
            "sector": b["sector"],
            "state": b["state"],
            "credit_status": b["credit_status"],
            "composite_score": cached["composite_score"],
            "last_updated": cached.get("last_updated"),
        })

    rows.sort(key=lambda r: r["composite_score"], reverse=True)

    avg_score = round(sum(r["composite_score"] for r in rows) / len(rows), 1) if rows else 0
    high_risk_pct = round(
        len([r for r in rows if r["composite_score"] < 50]) / len(rows) * 100, 1
    ) if rows else 0

    return {
        "businesses": rows,
        "portfolio_stats": {
            "average_health_score": avg_score,
            "high_risk_flagged_pct": high_risk_pct,
            "total_msmes": len(rows),
        }
    }


@router.post("/portfolio/{msme_id}/refresh")
def simulate_refresh(msme_id: str):
    """
    Simulates a near-real-time score refresh triggered by new alternate data
    (e.g. a new UPI transaction batch). Slightly perturbs the cash flow
    sub-score and recomputes the composite, to demo live update behavior
    without building true streaming infrastructure.
    """
    business = data_store.get_business(msme_id=msme_id)
    if not business:
        raise HTTPException(status_code=404, detail="MSME not found")

    records = data_store.get_source_records(msme_id)
    sub_scores = compute_sub_scores(records["gst"], records["upi"], records["aa"], records["epfo"])
    sub_scores["cash_flow_stability"] = round(
        min(max(sub_scores["cash_flow_stability"] + random.uniform(-5, 5), 0), 100), 1
    )
    composite_score, learned_weights = compute_composite_score(sub_scores)

    payload = {
        "msme_id": msme_id,
        "business_name": business["business_name"],
        "sub_scores": sub_scores,
        "composite_score": composite_score,
        "learned_weights": learned_weights,
    }
    data_store.cache_score(msme_id, payload)
    return data_store.get_cached_score(msme_id)
