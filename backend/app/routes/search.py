from fastapi import APIRouter, HTTPException
from app import data_store

router = APIRouter()


@router.get("/msme/{identifier}")
def search_msme(identifier: str):
    """
    Looks up a business by GSTIN or msme_id against the synthetic registry.
    Returns identity card data including NTC/NTB credit status flag.
    """
    business = data_store.get_business(gstin=identifier) or data_store.get_business(msme_id=identifier) or data_store.get_business(pan=identifier)
    if not business:
        raise HTTPException(status_code=404, detail="MSME not found for given identifier")
    return business
