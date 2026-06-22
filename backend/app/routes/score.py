from fastapi import APIRouter, HTTPException
from app import data_store
from app.scoring.rules import compute_sub_scores
from app.scoring.model import compute_composite_score

router = APIRouter()


@router.get("/score/{msme_id}")
def get_score(msme_id: str):
    """
    Computes the full health card: 4 rule-based sub-scores (Layer A) and one
    composite score with learned weights (Layer B). Requires consent to have
    been granted first via POST /consent.
    """
    business = data_store.get_business(msme_id=msme_id)
    if not business:
        raise HTTPException(status_code=404, detail="MSME not found")

    consent = data_store.get_consent(msme_id)
    if not consent:
        raise HTTPException(status_code=400, detail="Consent not granted yet for this MSME")

    records = data_store.get_source_records(msme_id)
    sub_scores = compute_sub_scores(records["gst"], records["upi"], records["aa"], records["epfo"])
    composite_score, learned_weights = compute_composite_score(sub_scores)

    # comparison badge: simulate what a traditional document-only process would show
    traditional_outcome = "Insufficient documentation - Rejected" if business["credit_status"] == "NTC" else "Limited file - Manual review required"
    health_card_outcome = "Approved-eligible" if composite_score >= 60 else "Review recommended"

    payload = {
        "msme_id": msme_id,
        "business_name": business["business_name"],
        "sub_scores": sub_scores,
        "composite_score": composite_score,
        "learned_weights": learned_weights,
        "traditional_outcome": traditional_outcome,
        "health_card_outcome": health_card_outcome,
    }

    data_store.cache_score(msme_id, payload)
    return data_store.get_cached_score(msme_id)
