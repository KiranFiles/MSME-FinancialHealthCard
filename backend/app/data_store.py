"""
Loads synthetic JSON data sources into memory at startup. Using in-memory
dicts rather than SQLite for the hackathon build keeps this simple; swap
for SQLite easily later if persistence across restarts becomes necessary.
"""

import json
import os

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

_businesses = None
_gst = None
_upi = None
_aa = None
_epfo = None

# in-memory cache of computed results, keyed by msme_id, populated after consent
_consented_data = {}
_scored_cache = {}


def _load_all():
    global _businesses, _gst, _upi, _aa, _epfo
    if _businesses is not None:
        return
    with open(f"{_DATA_DIR}/synthetic_msmes.json") as f:
        _businesses = {b["msme_id"]: b for b in json.load(f)}
    with open(f"{_DATA_DIR}/synthetic_gst.json") as f:
        _gst = json.load(f)
    with open(f"{_DATA_DIR}/synthetic_upi.json") as f:
        _upi = json.load(f)
    with open(f"{_DATA_DIR}/synthetic_aa.json") as f:
        _aa = json.load(f)
    with open(f"{_DATA_DIR}/synthetic_epfo.json") as f:
        _epfo = json.load(f)


def get_business(msme_id=None, gstin=None, pan=None):
    _load_all()
    if msme_id:
        return _businesses.get(msme_id)
    if gstin:
        for b in _businesses.values():
            if b["gstin"] == gstin:
                return b
    if pan:
        for b in _businesses.values():
            if b["pan"] == pan:
                return b
    return None


def get_all_businesses():
    _load_all()
    return list(_businesses.values())


def get_source_records(msme_id):
    _load_all()
    return {
        "gst": _gst.get(msme_id),
        "upi": _upi.get(msme_id),
        "aa": _aa.get(msme_id),
        "epfo": _epfo.get(msme_id),
    }


def mark_consented(msme_id, sources):
    _consented_data[msme_id] = sources


def get_consent(msme_id):
    return _consented_data.get(msme_id)


def cache_score(msme_id, score_payload):
    import datetime
    score_payload["last_updated"] = datetime.datetime.utcnow().isoformat() + "Z"
    _scored_cache[msme_id] = score_payload


def get_cached_score(msme_id):
    return _scored_cache.get(msme_id)


def get_all_cached_scores():
    return _scored_cache
