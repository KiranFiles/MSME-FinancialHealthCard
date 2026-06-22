"""
Generates synthetic MSME datasets: business registry, GST, UPI, AA, EPFO.
Run from project root: python scripts/generate_synthetic_data.py
Output: backend/data/*.json

Each business is assigned a deliberate risk tier (strong, moderate, weak)
so the generated dataset always spans the full score range on purpose.
Without this, random generation tends to cluster everyone in a healthy
band by chance, leaving no believable risky example to demo.
"""

import json
import random
from datetime import datetime, timedelta

random.seed(42)

SECTORS = [
    "Textiles", "Food Processing", "Auto Components", "Electronics Retail",
    "Pharmaceuticals", "Handicrafts", "IT Services", "Construction Materials",
    "Agro Products", "Furniture Manufacturing"
]

STATES = [
    "Karnataka", "Maharashtra", "Tamil Nadu", "Gujarat", "Uttar Pradesh",
    "Telangana", "West Bengal", "Rajasthan"
]

BUSINESS_NAME_PARTS = [
    "Sri", "Shree", "National", "Royal", "Prime", "United", "Modern",
    "Classic", "Elite", "Metro"
]
BUSINESS_NAME_NOUNS = [
    "Traders", "Industries", "Enterprises", "Textiles", "Foods",
    "Electronics", "Components", "Crafts", "Solutions", "Works"
]

# Risk tier definitions control how the synthetic data is generated for
# each business. Each tier maps to a probability range used throughout
# the generator functions below, so a "weak" business is weak across all
# four data sources, not just by random chance in one.
RISK_TIERS = {
    "strong": {
        "late_filing_prob": (0.0, 0.08),
        "active_days_pct": (88, 100),
        "inflow_variance": (0.15, 0.40),
        "cash_flow_stability_pct": (78, 95),
        "overdraft_incidents": (0, 1),
        "late_contributions": (0, 1),
        "employee_trend_weights": {"growing": 0.5, "stable": 0.45, "declining": 0.05},
    },
    "moderate": {
        "late_filing_prob": (0.10, 0.25),
        "active_days_pct": (70, 88),
        "inflow_variance": (0.40, 0.80),
        "cash_flow_stability_pct": (55, 78),
        "overdraft_incidents": (1, 3),
        "late_contributions": (1, 3),
        "employee_trend_weights": {"growing": 0.25, "stable": 0.55, "declining": 0.20},
    },
    "weak": {
        "late_filing_prob": (0.30, 0.55),
        "active_days_pct": (40, 68),
        "inflow_variance": (0.80, 1.50),
        "cash_flow_stability_pct": (25, 55),
        "overdraft_incidents": (3, 7),
        "late_contributions": (3, 7),
        "employee_trend_weights": {"growing": 0.05, "stable": 0.35, "declining": 0.60},
    },
}

# Distribution of tiers across the 30 businesses. Weighted toward strong
# and moderate since that reflects a realistic portfolio, but guarantees
# enough weak examples to always have risky cases available to demo.
TIER_DISTRIBUTION = (
    ["strong"] * 10 +
    ["moderate"] * 12 +
    ["weak"] * 8
)


def random_date_within_years(years_back_min, years_back_max):
    days_back = random.randint(years_back_min * 365, years_back_max * 365)
    return (datetime(2026, 6, 20) - timedelta(days=days_back)).strftime("%Y-%m-%d")


def make_gstin(state_code):
    digits = "".join([str(random.randint(0, 9)) for _ in range(10)])
    return f"{state_code}{digits}Z{random.choice('123456789')}"


def generate_msme_registry(n=30):
    businesses = []
    tiers = TIER_DISTRIBUTION[:]
    random.shuffle(tiers)

    for i in range(n):
        sector = random.choice(SECTORS)
        state = random.choice(STATES)
        name = f"{random.choice(BUSINESS_NAME_PARTS)} {random.choice(BUSINESS_NAME_NOUNS)}"
        incorp_date = random_date_within_years(1, 12)
        is_ntc = random.random() < 0.6
        risk_tier = tiers[i]
        businesses.append({
            "msme_id": f"MSME{1000 + i}",
            "business_name": name,
            "gstin": make_gstin(str(random.randint(10, 36)).zfill(2)),
            "pan": f"{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=5))}{random.randint(1000,9999)}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}",
            "sector": sector,
            "state": state,
            "incorporation_date": incorp_date,
            "credit_status": "NTC" if is_ntc else "NTB",
            # included for transparency in the synthetic dataset only;
            # not used anywhere downstream as a scoring shortcut, the
            # actual score is still computed independently from the
            # generated GST/UPI/AA/EPFO numbers below
            "_synthetic_risk_tier": risk_tier,
        })
    return businesses


def generate_gst_data(businesses):
    records = {}
    for b in businesses:
        tier = RISK_TIERS[b["_synthetic_risk_tier"]]
        base_turnover = random.randint(150000, 4000000)
        months = []
        late_count = 0
        late_prob = random.uniform(*tier["late_filing_prob"])
        for m in range(12):
            seasonal_factor = 1.0
            if b["sector"] in ("Food Processing", "Handicrafts", "Electronics Retail") and m in (9, 10, 11):
                seasonal_factor = random.uniform(1.3, 1.8)
            turnover = round(base_turnover * seasonal_factor * random.uniform(0.85, 1.15))
            filed_late = random.random() < late_prob
            if filed_late:
                late_count += 1
            months.append({
                "month_index": m,
                "turnover": turnover,
                "filed_on_time": not filed_late
            })
        records[b["msme_id"]] = {
            "monthly": months,
            "avg_monthly_turnover": round(sum(x["turnover"] for x in months) / 12),
            "late_filings_count": late_count,
            "filing_consistency_pct": round((12 - late_count) / 12 * 100, 1)
        }
    return records


def generate_upi_data(businesses):
    records = {}
    for b in businesses:
        tier = RISK_TIERS[b["_synthetic_risk_tier"]]
        base_volume = random.randint(20000, 600000)
        days = []
        for d in range(90):
            seasonal = 1.0
            if d % 7 in (5, 6):
                seasonal = random.uniform(1.1, 1.4)
            vol = round(base_volume / 30 * seasonal * random.uniform(0.7, 1.3))
            days.append(vol)
        avg_ticket = random.randint(150, 8000)
        records[b["msme_id"]] = {
            "monthly_volume": round(sum(days) / 3),
            "avg_ticket_size": avg_ticket,
            "inflow_variance": round(random.uniform(*tier["inflow_variance"]), 2),
            "active_days_pct": round(random.uniform(*tier["active_days_pct"]), 1)
        }
    return records


def generate_aa_data(businesses):
    records = {}
    for b in businesses:
        tier = RISK_TIERS[b["_synthetic_risk_tier"]]
        incorp_year = int(b["incorporation_date"][:4])
        vintage_months = (2026 - incorp_year) * 12 + random.randint(-6, 6)
        vintage_months = max(vintage_months, 3)
        records[b["msme_id"]] = {
            "account_vintage_months": vintage_months,
            "avg_closing_balance": random.randint(5000, 800000),
            "cash_flow_stability_pct": round(random.uniform(*tier["cash_flow_stability_pct"]), 1),
            "overdraft_incidents_last_year": random.randint(*tier["overdraft_incidents"])
        }
    return records


def generate_epfo_data(businesses):
    records = {}
    for b in businesses:
        tier = RISK_TIERS[b["_synthetic_risk_tier"]]
        employee_count = random.randint(2, 80)
        late_contributions = random.randint(*tier["late_contributions"])
        trend = random.choices(
            list(tier["employee_trend_weights"].keys()),
            weights=list(tier["employee_trend_weights"].values())
        )[0]
        records[b["msme_id"]] = {
            "employee_count": employee_count,
            "contribution_consistency_pct": round(max((12 - late_contributions) / 12 * 100, 0), 1),
            "employee_count_trend": trend
        }
    return records


def main():
    businesses = generate_msme_registry(30)
    gst = generate_gst_data(businesses)
    upi = generate_upi_data(businesses)
    aa = generate_aa_data(businesses)
    epfo = generate_epfo_data(businesses)

    out_dir = "backend/data"
    with open(f"{out_dir}/synthetic_msmes.json", "w") as f:
        json.dump(businesses, f, indent=2)
    with open(f"{out_dir}/synthetic_gst.json", "w") as f:
        json.dump(gst, f, indent=2)
    with open(f"{out_dir}/synthetic_upi.json", "w") as f:
        json.dump(upi, f, indent=2)
    with open(f"{out_dir}/synthetic_aa.json", "w") as f:
        json.dump(aa, f, indent=2)
    with open(f"{out_dir}/synthetic_epfo.json", "w") as f:
        json.dump(epfo, f, indent=2)

    tier_counts = {}
    for b in businesses:
        t = b["_synthetic_risk_tier"]
        tier_counts[t] = tier_counts.get(t, 0) + 1

    print(f"Generated {len(businesses)} MSME records across GST, UPI, AA, EPFO sources.")
    print(f"Risk tier distribution: {tier_counts}")
    print(f"Files written to {out_dir}/")


if __name__ == "__main__":
    main()
