import { create } from "zustand";
import type { Business, ScoreResponse } from "../api/client";

interface AppState {
  selectedBusiness: Business | null;
  consentedSources: string[];
  currentScore: ScoreResponse | null;
  setSelectedBusiness: (b: Business | null) => void;
  setConsentedSources: (sources: string[]) => void;
  setCurrentScore: (s: ScoreResponse | null) => void;
}

export const useAppStore = create<AppState>((set) => ({
  selectedBusiness: null,
  consentedSources: [],
  currentScore: null,
  setSelectedBusiness: (b) => set({ selectedBusiness: b }),
  setConsentedSources: (sources) => set({ consentedSources: sources }),
  setCurrentScore: (s) => set({ currentScore: s }),
}));
