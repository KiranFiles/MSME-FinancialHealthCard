import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { useAppStore } from "../store/appStore";

const SAMPLE_IDS = ["MSME1000", "MSME1001", "MSME1002", "MSME1003"];
const SAMPLE_GSTINS = ["182351161559Z5", "313413164752Z6", "308350305641Z4", "286965328710Z2"];

export default function SearchMSME() {
  const [identifier, setIdentifier] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const setSelectedBusiness = useAppStore((s) => s.setSelectedBusiness);

  async function handleSearch(value: string) {
    setError(null);
    setLoading(true);
    try {
      const business = await api.searchMsme(value);
      setSelectedBusiness(business);
      navigate("/consent");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="screen">
      <h1>MSME Financial Health Card</h1>
      <p className="subtitle">
        Search a business by GSTIN or MSME ID to begin assessment.
      </p>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (identifier.trim()) handleSearch(identifier.trim());
        }}
      >
        <input
          type="text"
          value={identifier}
          onChange={(e) => setIdentifier(e.target.value)}
          placeholder="Enter GSTIN or MSME ID (e.g. MSME1000)"
          className="text-input"
        />
        <button type="submit" disabled={loading}>
          {loading ? "Searching..." : "Search"}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      <div className="sample-ids">
        <p>Sample IDs for demo:</p>
        <div className="sample-id-list">
          {SAMPLE_IDS.map((id) => (
            <button
              key={id}
              className="sample-id-btn"
              onClick={() => handleSearch(id)}
              disabled={loading}
            >
              {id}
            </button>
          ))}
        </div>
      </div>

      <div className="sample-ids">
        <p>Try GSTINs for demo:</p>
        <div className="sample-id-list">
          {SAMPLE_GSTINS.map((gstin) => (
            <button
              key={gstin}
              className="sample-id-btn"
              onClick={() => handleSearch(gstin)}
              disabled={loading}
            >
              {gstin}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
