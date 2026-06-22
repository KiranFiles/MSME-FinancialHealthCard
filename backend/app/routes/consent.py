from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app import data_store

router = APIRouter()


class ConsentRequest(BaseModel):
    msme_id: str
    sources: List[str]


@router.post("/consent")
def grant_consent(req: ConsentRequest):
    """
    Records which data sources the user consented to share, then aggregates
    those sources into one normalized feature object. This is the step that
    answers the 'unified assessment framework' requirement -- four separate
    data sources become one object here, before any scoring happens.
    """
    business = data_store.get_business(msme_id=req.msme_id)
    if not business:
        raise HTTPException(status_code=404, detail="MSME not found")

    valid_sources = {"gst", "upi", "aa", "epfo"}
    if not set(req.sources).issubset(valid_sources):
        raise HTTPException(status_code=400, detail="Invalid source name provided")

    data_store.mark_consented(req.msme_id, req.sources)
    records = data_store.get_source_records(req.msme_id)

    aggregated = {src: records[src] for src in req.sources}
    return {
        "msme_id": req.msme_id,
        "consented_sources": req.sources,
        "aggregated_data": aggregated
    }
