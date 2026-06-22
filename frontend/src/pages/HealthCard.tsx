import { useNavigate } from "react-router-dom";
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import { useAppStore } from "../store/appStore";

const DIMENSION_CONFIG: Record<string, {
  label: string;
  source: string;
  plain: string;
}> = {
  compliance_consistency: {
    label: "Compliance Consistency",
    source: "GST Returns",
    plain: "How regularly and on time the business files its GST returns",
  },
  cash_flow_stability: {
    label: "Cash Flow Stability",
    source: "UPI Transactions",
    plain: "How steady and predictable the daily money coming in is",
  },
  digital_footprint: {
    label: "Digital Footprint",
    source: "Account Aggregator",
    plain: "How active and stable the business bank account history is",
  },
  workforce_stability: {
    label: "Workforce Stability",
    source: "EPFO Records",
    plain: "How consistently employee provident fund contributions are made",
  },
};

const SCORE_BANDS = [
  { label: "Poor", min: 0,  max: 40,  color: "#b3261e", bg: "#fce8e6" },
  { label: "Fair", min: 40, max: 60,  color: "#e67e00", bg: "#fff3e0" },
  { label: "Good", min: 60, max: 80,  color: "#1f6f54", bg: "#e8f5e9" },
  { label: "Strong", min: 80, max: 100, color: "#0d4f3c", bg: "#c8e6c9" },
];

function getBand(score: number) {
  return SCORE_BANDS.find((b) => score >= b.min && score < b.max) || SCORE_BANDS[3];
}

function getBarColor(score: number) {
  return getBand(score).color;
}

function ScoreBandStrip({ score }: { score: number }) {
  const band = getBand(score);
  return (
    <div className="score-band-wrap">
      <div className="score-band-strip">
        {SCORE_BANDS.map((b) => (
          <div
            key={b.label}
            className="score-band-segment"
            style={{ background: b.bg, borderBottom: `3px solid ${b.color}` }}
          >
            <span style={{ color: b.color, fontWeight: 600, fontSize: 12 }}>
              {b.label}
            </span>
            <span style={{ color: "#888", fontSize: 11 }}>
              {b.min}–{b.max}
            </span>
          </div>
        ))}
      </div>
      <div
        className="score-band-pointer"
        style={{
          left: `${score}%`,
          borderTopColor: band.color,
        }}
      >
        <span style={{ color: band.color, fontWeight: 700, fontSize: 13 }}>
          {score} — {band.label}
        </span>
      </div>
    </div>
  );
}

function DimensionCards({
  subScores,
  learnedWeights,
}: {
  subScores: Record<string, number>;
  learnedWeights: Record<string, number>;
}) {
  return (
    <div className="dimension-cards">
      {Object.entries(subScores).map(([key, value]) => {
        const band = getBand(value);
        const config = DIMENSION_CONFIG[key];
        const weight = learnedWeights[key];
        return (
          <div
            key={key}
            className="dimension-card"
            style={{ borderLeft: `4px solid ${band.color}` }}
          >
            <div className="dim-card-top">
              <div>
                <div className="dim-card-label">{config.label}</div>
                <div className="dim-card-source">Source: {config.source}</div>
              </div>
              <div
                className="dim-card-score"
                style={{ color: band.color }}
              >
                {value}
                <span className="dim-card-score-max">/100</span>
              </div>
            </div>
            <div className="dim-progress-bg">
              <div
                className="dim-progress-fill"
                style={{ width: `${value}%`, background: band.color }}
              />
            </div>
            <div className="dim-card-plain">{config.plain}</div>
            <div className="dim-card-footer">
              <span
                className="dim-band-badge"
                style={{ background: band.bg, color: band.color }}
              >
                {band.label}
              </span>
              <span className="dim-weight-label">
                Model weight: {weight}%
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default function HealthCard() {
  const navigate = useNavigate();
  const business = useAppStore((s) => s.selectedBusiness);
  const score = useAppStore((s) => s.currentScore);

  if (!business || !score) {
    return (
      <div className="screen">
        <p>No score available. Go back and complete the consent step first.</p>
        <button onClick={() => navigate("/")}>Back to search</button>
      </div>
    );
  }

  const band = getBand(score.composite_score);

  const radarData = Object.entries(score.sub_scores).map(([key, value]) => ({
    dimension: DIMENSION_CONFIG[key].label,
    score: value,
  }));

  const barData = Object.entries(score.sub_scores).map(([key, value]) => ({
    name: DIMENSION_CONFIG[key].label.replace(" ", "\n"),
    score: value,
    color: getBarColor(value),
  }));

  return (
    <div className="screen wide">
      {/* Header */}
      <div className="hc-header">
        <div>
          <h1 style={{ marginBottom: 4 }}>{business.business_name}</h1>
          <p className="subtitle" style={{ marginBottom: 0 }}>
            {business.sector} — {business.state} —{" "}
            <span
              className="dim-band-badge"
              style={{ background: "#fff3cd", color: "#856404", fontSize: 13 }}
            >
              {business.credit_status} (New-to-Credit)
            </span>
          </p>
        </div>
      </div>

      {/* Composite score */}
      <div
        className="hc-score-block"
        style={{ borderLeft: `5px solid ${band.color}` }}
      >
        <div>
          <div
            className="gauge-number"
            style={{ color: band.color, textAlign: "left", fontSize: 64 }}
          >
            {score.composite_score}
            <span style={{ fontSize: 20, color: "#888", marginLeft: 4 }}>
              / 100
            </span>
          </div>
          <div style={{ fontSize: 14, color: "#5b6b62", marginTop: 2 }}>
            Unified Financial Health Score
          </div>
          <div style={{ fontSize: 13, color: "#888", marginTop: 4 }}>
            Computed from GST, UPI, Account Aggregator and EPFO alternate data
          </div>
        </div>
        <div style={{ textAlign: "right" }}>
          <div
            className="dim-band-badge"
            style={{
              background: band.bg,
              color: band.color,
              fontSize: 16,
              padding: "8px 16px",
            }}
          >
            {band.label}
          </div>
        </div>
      </div>

      {/* Score band strip */}
      <ScoreBandStrip score={score.composite_score} />

      {/* Outcome comparison */}
      <div className="outcome-comparison">
        <div
          className="outcome-box"
          style={{ borderTop: "3px solid #b3261e" }}
        >
          <div className="outcome-title">Traditional document-based process</div>
          <div className="outcome-value negative">{score.traditional_outcome}</div>
          <div style={{ fontSize: 12, color: "#888", marginTop: 4 }}>
            No financial documents available for NTC/NTB businesses
          </div>
        </div>
        <div
          className="outcome-box"
          style={{ borderTop: `3px solid ${band.color}` }}
        >
          <div className="outcome-title">Health Card alternate-data assessment</div>
          <div
            className="outcome-value"
            style={{ color: band.color }}
          >
            {score.health_card_outcome}
          </div>
          <div style={{ fontSize: 12, color: "#888", marginTop: 4 }}>
            Based on {Object.keys(score.sub_scores).length} alternate data sources
          </div>
        </div>
      </div>

      {/* Dimension cards — one per data source */}
      <div className="section-title">Dimension breakdown</div>
      <div style={{ fontSize: 13, color: "#888", marginBottom: 12 }}>
        Each card shows the score for one data source, what it means in plain
        language, and how much the trained model weighted it.
      </div>
      <DimensionCards
        subScores={score.sub_scores}
        learnedWeights={score.learned_weights}
      />

      {/* Bar chart — easy to read exact values */}
      <div className="section-title" style={{ marginTop: 32 }}>
        Dimension comparison (bar chart)
      </div>
      <div style={{ fontSize: 13, color: "#888", marginBottom: 12 }}>
        Which areas are strong and which need attention — red bars are below
        40, orange between 40-60, green above 60.
      </div>
      <ResponsiveContainer width="100%" height={240}>
        <BarChart
          data={barData}
          layout="vertical"
          margin={{ left: 140, right: 40, top: 8, bottom: 8 }}
        >
          <CartesianGrid strokeDasharray="3 3" horizontal={false} />
          <XAxis type="number" domain={[0, 100]} tickCount={6} />
          <YAxis
            type="category"
            dataKey="name"
            width={130}
            tick={{ fontSize: 13 }}
          />
          <Tooltip
            formatter={(value) => [
              `${value as number} / 100`,
              "Score",
            ]}
          />
          <ReferenceLine x={60} stroke="#1f6f54" strokeDasharray="4 4" label={{ value: "Good threshold", position: "top", fontSize: 11 }} />
          <ReferenceLine x={40} stroke="#e67e00" strokeDasharray="4 4" label={{ value: "Fair threshold", position: "insideTopLeft", fontSize: 11 }} />
          <Bar dataKey="score" radius={[0, 4, 4, 0]}>
            {barData.map((entry, index) => (
              <Cell key={index} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* Radar chart — kept as third layer for technical judges */}
      <div className="section-title" style={{ marginTop: 32 }}>
        Multidimensional profile (radar chart)
      </div>
      <div style={{ fontSize: 13, color: "#888", marginBottom: 12 }}>
        Shape of the business across all four dimensions together. A larger,
        rounder shape means balanced strength across all sources.
      </div>
      <ResponsiveContainer width="100%" height={300}>
        <RadarChart data={radarData}>
          <PolarGrid />
          <PolarAngleAxis dataKey="dimension" tick={{ fontSize: 12 }} />
          <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fontSize: 10 }} />
          <Radar
            name="Score"
            dataKey="score"
            stroke={band.color}
            fill={band.color}
            fillOpacity={0.35}
          />
        </RadarChart>
      </ResponsiveContainer>

      {/* Model weights — moved to bottom, collapsed to one line each */}
      <div className="weights-legend" style={{ marginTop: 24 }}>
        <div className="section-title" style={{ marginBottom: 8 }}>
          How the model weighted each dimension
        </div>
        <div style={{ fontSize: 13, color: "#888", marginBottom: 8 }}>
          These weights were learned by the scoring model from training data,
          not set manually.
        </div>
        <div className="weights-bar-list">
          {Object.entries(score.learned_weights).map(([key, value]) => (
            <div key={key} className="weight-bar-row">
              <span className="weight-bar-label">
                {DIMENSION_CONFIG[key].label}
              </span>
              <div className="weight-bar-track">
                <div
                  className="weight-bar-fill"
                  style={{ width: `${value * 2.5}%`, background: "#1f6f54" }}
                />
              </div>
              <span className="weight-bar-value">{value}%</span>
            </div>
          ))}
        </div>
      </div>

      <button
        onClick={() => navigate("/strengths-risks")}
        style={{ marginTop: 24, width: "100%", padding: "14px" }}
      >
        View AI-generated strengths and risks
      </button>
    </div>
  );
}
