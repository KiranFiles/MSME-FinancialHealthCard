import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import SearchMSME from "./pages/SearchMSME";
import Consent from "./pages/Consent";
import HealthCard from "./pages/HealthCard";
import StrengthsRisks from "./pages/StrengthsRisks";
import LenderPortfolio from "./pages/LenderPortfolio";
import "./App.css";

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <nav className="top-nav">
          <Link to="/" className="nav-brand">MSME Financial Health Card</Link>
          <div className="nav-links">
            <Link to="/">Search</Link>
            <Link to="/portfolio">Portfolio</Link>
          </div>
        </nav>
        <main>
          <Routes>
            <Route path="/" element={<SearchMSME />} />
            <Route path="/consent" element={<Consent />} />
            <Route path="/health-card" element={<HealthCard />} />
            <Route path="/strengths-risks" element={<StrengthsRisks />} />
            <Route path="/portfolio" element={<LenderPortfolio />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
