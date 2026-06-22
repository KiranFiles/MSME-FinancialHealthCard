import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { useAppStore } from "../store/appStore";

export default function StrengthsRisks() {
  const navigate = useNavigate();
  const business = useAppStore((s) => s.selectedBusiness);
  const score = useAppStore((s) => s.currentScore);
  const [narrative, setNarrative] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!business) return;
    setLoading(true);
    api
      .getNarrative(business.msme_id)
      .then((res) => setNarrative(res.narrative))
      .catch((err) =>
        setError(err instanceof Error ? err.message : "Failed to load narrative")
      )
      .finally(() => setLoading(false));
  }, [business]);

  if (!business || !score) {
    return (
      <div className="screen">
        <p>No business selected. Go back and search for an MSME first.</p>
        <button onClick={() => navigate("/")}>Back to search</button>
      </div>
    );
  }

  return (
    <div className="screen">
      <h1>Strengths and Risks</h1>
      <p className="subtitle">
        {business.business_name} - Composite score {score.composite_score}/100
      </p>

      {loading && <p>Generating narrative...</p>}
      {error && <p className="error">{error}</p>}
      {!loading && !error && (
        <div className="narrative-box">
          {narrative.split("\n").map((line, i) => (
            <p key={i}>{line}</p>
          ))}
        </div>
      )}

      <button onClick={() => navigate("/")}>
        Go to home 
      </button>
    </div>
  );
}
