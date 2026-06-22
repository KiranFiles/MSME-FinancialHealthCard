import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { useAppStore } from "../store/appStore";

const SOURCES = [
  {
    key: "gst",
    label: "GST Returns",
    description: "Monthly filing history and turnover trend used for compliance consistency.",
  },
  {
    key: "upi",
    label: "UPI Transactions",
    description: "Daily transaction volume and consistency used for cash flow stability.",
  },
  {
    key: "aa",
    label: "Account Aggregator (AA)",
    description: "Consent-based bank statement data used for digital footprint assessment.",
  },
  {
    key: "epfo",
    label: "EPFO Records",
    description: "Employee contribution history used for workforce stability.",
  },
];

export default function Consent() {
  const [selected, setSelected] = useState<string[]>(["gst", "upi", "aa", "epfo"]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const business = useAppStore((s) => s.selectedBusiness);
  const setConsentedSources = useAppStore((s) => s.setConsentedSources);
  const setCurrentScore = useAppStore((s) => s.setCurrentScore);

  if (!business) {
    return (
      <div className="screen">
        <p>No business selected. Go back and search for an MSME first.</p>
        <button onClick={() => navigate("/")}>Back to search</button>
      </div>
    );
  }

  function toggleSource(key: string) {
    setSelected((prev) =>
      prev.includes(key) ? prev.filter((s) => s !== key) : [...prev, key]
    );
  }

  async function handleContinue() {
    setError(null);
    setLoading(true);
    try {
      await api.grantConsent(business!.msme_id, selected);
      setConsentedSources(selected);
      const score = await api.getScore(business!.msme_id);
      setCurrentScore(score);
      navigate("/health-card");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Consent step failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="screen">
      <h1>Data Consent</h1>
      <p className="subtitle">
        {business.business_name} ({business.credit_status}) is requesting access
        to the following alternate data sources, through consent-based
        Account Aggregator rails.
      </p>

      <div className="consent-list">
        {SOURCES.map((src) => (
          <label key={src.key} className="consent-item">
            <input
              type="checkbox"
              checked={selected.includes(src.key)}
              onChange={() => toggleSource(src.key)}
            />
            <div>
              <div className="consent-label">{src.label}</div>
              <div className="consent-description">{src.description}</div>
            </div>
          </label>
        ))}
      </div>

      {error && <p className="error">{error}</p>}

      <button
        onClick={handleContinue}
        disabled={loading || selected.length === 0}
      >
        {loading ? "Aggregating data..." : `Grant consent and continue (${selected.length} sources)`}
      </button>
    </div>
  );
}
