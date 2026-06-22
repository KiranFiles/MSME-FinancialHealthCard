import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, type PortfolioResponse } from "../api/client";

export default function LenderPortfolio() {
  const navigate = useNavigate();
  const [data, setData] = useState<PortfolioResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshingId, setRefreshingId] = useState<string | null>(null);
  const [sortDesc, setSortDesc] = useState(true);

  function load() {
    setLoading(true);
    api
      .getPortfolio()
      .then(setData)
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    load();
  }, []);

  async function handleRefresh(msmeId: string) {
    setRefreshingId(msmeId);
    try {
      await api.refreshScore(msmeId);
      await load();
    } finally {
      setRefreshingId(null);
    }
  }

  if (loading || !data) {
    return (
      <div className="screen">
        <p>Loading portfolio...</p>
      </div>
    );
  }

  const sorted = [...data.businesses].sort((a, b) =>
    sortDesc ? b.composite_score - a.composite_score : a.composite_score - b.composite_score
  );

  return (
    <div className="screen wide">
      <h1>Lender Portfolio View</h1>
      <p className="subtitle">
        All assessed MSMEs, ranked by unified financial health score.
      </p>

      <div className="portfolio-stats">
        <div className="stat-box">
          <div className="stat-value">{data.portfolio_stats.average_health_score}</div>
          <div className="stat-label">Portfolio average score</div>
        </div>
        <div className="stat-box">
          <div className="stat-value">{data.portfolio_stats.high_risk_flagged_pct}%</div>
          <div className="stat-label">High-risk flagged</div>
        </div>
        <div className="stat-box">
          <div className="stat-value">{data.portfolio_stats.total_msmes}</div>
          <div className="stat-label">Total MSMEs assessed</div>
        </div>
      </div>

      <table className="portfolio-table">
        <thead>
          <tr>
            <th>Business</th>
            <th>Sector</th>
            <th>State</th>
            <th>Status</th>
            <th onClick={() => setSortDesc(!sortDesc)} className="sortable">
              Score {sortDesc ? "(high to low)" : "(low to high)"}
            </th>
            <th>Last updated</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((row) => (
            <tr key={row.msme_id}>
              <td>{row.business_name}</td>
              <td>{row.sector}</td>
              <td>{row.state}</td>
              <td>{row.credit_status}</td>
              <td className={row.composite_score < 50 ? "score-risk" : "score-ok"}>
                {row.composite_score}
              </td>
              <td>{row.last_updated ? new Date(row.last_updated).toLocaleTimeString() : "-"}</td>
              <td>
                <button
                  className="refresh-btn"
                  onClick={() => handleRefresh(row.msme_id)}
                  disabled={refreshingId === row.msme_id}
                >
                  {refreshingId === row.msme_id ? "Refreshing..." : "Simulate new data"}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <button onClick={() => navigate("/")}>Assess another MSME</button>
    </div>
  );
}
