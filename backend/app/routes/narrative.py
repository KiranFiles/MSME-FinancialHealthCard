from fastapi import APIRouter, HTTPException
from app import data_store
from app.llm.gemini_client import generate_narrative

router = APIRouter()


@router.get("/narrative/{msme_id}")
def get_narrative(msme_id: str):
    """
    Generates strengths/risks narrative from an already-computed score.
    Requires GET /score/{msme_id} to have been called first.
    """
    business = data_store.get_business(msme_id=msme_id)
    if not business:
        raise HTTPException(status_code=404, detail="MSME not found")

    cached_score = data_store.get_cached_score(msme_id)
    if not cached_score:
        raise HTTPException(status_code=400, detail="Score not computed yet. Call /score first.")

    records = data_store.get_source_records(msme_id)
    narrative = generate_narrative(
        business["business_name"],
        cached_score["sub_scores"],
        cached_score["composite_score"],
        records
    )
    return {"msme_id": msme_id, "narrative": narrative}
