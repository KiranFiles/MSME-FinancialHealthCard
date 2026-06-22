"""
Layer B: loads the trained composite scoring model and produces a single
unified 0-100 score from the 4 sub-scores. This is the model whose learned
weights answer the 'unified assessment framework' requirement.
"""

import pickle
import os
import numpy as np

_MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "ml", "scoring_model.pkl")

_model = None


def _load_model():
    global _model
    if _model is None:
        with open(_MODEL_PATH, "rb") as f:
            _model = pickle.load(f)
    return _model


def compute_composite_score(sub_scores: dict):
    """
    sub_scores: dict with keys compliance_consistency, cash_flow_stability,
    digital_footprint, workforce_stability (each 0-100).
    Returns: composite score 0-100, and the normalized weights actually
    learned by the model (for display in the UI legend).
    """
    model = _load_model()
    features = np.array([[
        sub_scores["compliance_consistency"],
        sub_scores["cash_flow_stability"],
        sub_scores["digital_footprint"],
        sub_scores["workforce_stability"],
    ]])

    # Use the model's decision function (raw weighted sum) rather than the
    # sigmoid probability. predict_proba saturates near 0 or 1 very quickly
    # for cleanly separable data, which collapses scores toward 0/100 and
    # loses the score spread that makes the portfolio view meaningful.
    # Instead, compute a weighted score directly from the learned
    # coefficients, normalized to land in a realistic 0-100 band.
    coefs = model.coef_[0]
    total_abs = sum(abs(c) for c in coefs)
    normalized_weights = [abs(c) / total_abs for c in coefs]

    weighted_sum = sum(f * w for f, w in zip(features[0], normalized_weights))
    composite_score = round(min(max(weighted_sum, 0), 100), 1)

    coefs = model.coef_[0]
    total = sum(abs(c) for c in coefs)
    learned_weights = {
        "compliance_consistency": round(abs(coefs[0]) / total * 100, 1),
        "cash_flow_stability": round(abs(coefs[1]) / total * 100, 1),
        "digital_footprint": round(abs(coefs[2]) / total * 100, 1),
        "workforce_stability": round(abs(coefs[3]) / total * 100, 1),
    }

    return composite_score, learned_weights
