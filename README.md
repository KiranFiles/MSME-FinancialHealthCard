# MSME Financial Health Card

AI/ML-driven MSME Financial Health Card built for IDBI Innovate 2026, Track 03
(Financial Inclusion, Digital Lending, Credit Decisioning).

This solution aggregates alternate data (GST, UPI, Account Aggregator, EPFO)
for New-to-Credit and New-to-Bank MSMEs, computes a unified financial health
score using a trained scoring model, visualizes strengths and risks, and
gives lenders a portfolio-level view for credit decisioning.

## What is in this project

```
msme-health-card/
  backend/        FastAPI service: scoring engine, LLM narrative, API routes
  frontend/       React + TypeScript + Vite app: the 5-screen user flow
  scripts/        synthetic data generator and model trainer
```

The 5-screen flow: Search MSME -> Consent -> Health Card -> Strengths and
Risks -> Lender Portfolio.

## Prerequisites

Install these before starting, then verify each with the version command
shown.

| Tool | Minimum version | Check with |
|------|------------------|------------|
| Node.js | 18.x | `node --version` |
| npm | 9.x (comes with Node) | `npm --version` |
| Python | 3.10 | `python --version` |
| VS Code | any recent version | - |

Recommended VS Code extensions: Python (Microsoft), Pylance, ESLint, and the
official Tailwind/React extensions if you have them, though none are
required for the app to run.

If `python --version` fails on Windows, reinstall Python from python.org and
check the box "Add python.exe to PATH" during setup, then restart VS Code.

## Step 1: Open the project in VS Code

Extract the zip, then in VS Code: File -> Open Folder -> select the
`msme-health-card` folder. This opens both `backend` and `frontend` as
subfolders in one workspace, which is the easiest way to work with both at
once.

Open a terminal inside VS Code with View -> Terminal, or Ctrl+` . You will
run backend and frontend in two separate terminal tabs, both inside VS Code.

## Step 2: Backend setup

In a VS Code terminal:

```
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

On Windows, if `venv\Scripts\activate` is blocked by execution policy, run
this once in an Administrator PowerShell, then retry:

```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Once activated, your terminal prompt should show `(venv)` at the start of
the line. Keep this terminal tab active for the backend.

## Step 3: Generate synthetic data

Still inside `backend`, with the venv active, move back to the project root
to run the generator script:

```
cd ..
python scripts\generate_synthetic_data.py
```

Expected output:

```
Generated 30 MSME records across GST, UPI, AA, EPFO sources.
Files written to backend/data/
```

This creates five JSON files inside `backend\data\`: synthetic_msmes.json,
synthetic_gst.json, synthetic_upi.json, synthetic_aa.json,
synthetic_epfo.json.

## Step 4: Train the scoring model

```
python scripts\train_scoring_model.py
```

Expected output looks like:

```
Training accuracy: 0.930
Learned coefficients (compliance, cash_flow, digital, workforce): [...]
Intercept: ...
Model saved to .../backend/ml/scoring_model.pkl
```

This must be run after Step 3, and must be re-run any time you regenerate
the synthetic data, since the model is trained against whatever is currently
in `backend\data\`.

## Step 5: Gemini API key (optional)

The narrative screen works without this, using a rule-based fallback summary
so the app never breaks during a demo. To use the real Gemini LLM:

1. Get a free API key at https://aistudio.google.com/apikey
2. In `backend`, copy the example env file:

```
cd backend
copy .env.example .env
```

3. Open `.env` in VS Code and replace the placeholder with your real key.
4. Before starting the backend server, set the key as an environment
   variable in the same terminal:

```
set GEMINI_API_KEY=your_actual_key_here
```

You need to set this every time you open a fresh terminal, unless you wire
it through `python-dotenv` or a similar loader.

## Step 6: Run the backend server

From inside `backend`, with the venv still active:

```
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Leave this terminal running. Confirm it works by opening
`http://127.0.0.1:8000/health` in a browser, you should see:

```
{"status":"healthy"}
```

You can also open `http://127.0.0.1:8000/docs` for the interactive Swagger
API explorer, useful for testing endpoints directly without the frontend.

## Step 7: Frontend setup

Open a second VS Code terminal tab (the backend terminal must keep running
in the first tab). In the new tab:

```
cd frontend
npm install
```

This installs React, TypeScript, Vite, React Router, Recharts, and Zustand.

## Step 8: Set the frontend API URL

```
copy .env.example .env
```

The default value inside `.env` is already `http://127.0.0.1:8000`, which
matches the local backend from Step 6. No edit needed unless you later
deploy the backend somewhere else.

## Step 9: Run the frontend

```
npm run dev
```

Expected output includes a local URL, normally:

```
Local:   http://localhost:5173/
```

Open that URL in your browser.

## Step 10: Test the full flow

With both terminals running (backend on port 8000, frontend on port 5173):

1. On the Search screen, click one of the sample ID buttons (MSME1000,
   MSME1001, MSME1002, MSME1003), or type an ID manually.
2. On the Consent screen, leave all four sources checked and continue.
3. View the Health Card: composite score, radar chart, and the
   traditional-vs-health-card outcome comparison.
4. View Strengths and Risks: the generated narrative.
5. View Lender Portfolio: the full sorted list with portfolio stats, and try
   the "Simulate new data" button on any row to see a live score refresh.

If any screen shows a network error, check that the backend terminal is
still running and that `frontend/.env` points to the correct backend URL.

## Running both servers together going forward

Each time you come back to work on this:

```
# Terminal 1
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Terminal 2
cd frontend
npm run dev
```

You do not need to repeat Steps 3 and 4 (data generation and model
training) unless you intentionally want to regenerate the synthetic dataset.

## Common issues

| Symptom | Likely cause | Fix |
|---|---|---|
| `uvicorn: command not found` | venv not activated | Run `venv\Scripts\activate` again in that terminal |
| Frontend shows "Failed to fetch" on search | Backend not running, or wrong port | Confirm Step 6 terminal is active and `http://127.0.0.1:8000/health` loads |
| `ModuleNotFoundError: No module named 'sklearn'` | Dependencies not installed in the active venv | Re-run `pip install -r requirements.txt` with the venv active |
| PowerShell blocks venv activation | Execution policy restriction | Run the `Set-ExecutionPolicy` command from Step 2 once, as Administrator |
| Narrative screen shows a generic fallback even with `GEMINI_API_KEY` set | Key not set in the same terminal session running uvicorn | Re-run `set GEMINI_API_KEY=...` in that terminal, then restart uvicorn |
| Portfolio scores look unrealistically high or all identical | Stale `scoring_model.pkl` from before a rules.py edit | Re-run `python scripts\train_scoring_model.py` |

## What is real versus simulated in this build

This distinction is worth stating explicitly in any pitch or demo, since it
shows a clear line between what is built now and what would be built during
an actual sandbox PoC phase.

| Component | Status |
|---|---|
| GST, UPI, AA, EPFO data | Synthetic, generated locally, realistically shaped |
| GSTIN/PAN identity lookup | Synthetic registry, not a live government API |
| Sub-scoring rules (Layer A) | Real, deterministic logic |
| Composite scoring model (Layer B) | Real, trained with scikit-learn on synthetic labels |
| LLM narrative | Real API call to Gemini when a key is configured, fallback otherwise |
| ULI/OCEN/AA ecosystem integration | Architecture concept only, not built |
| Near real-time score refresh | Simulated trigger button, not true event streaming |

## Tech stack summary

- Frontend: React, TypeScript, Vite, React Router, Recharts, Zustand
- Backend: FastAPI, scikit-learn, numpy
- Data: synthetic JSON files generated locally, no external database required
- Deployment target (not required for local development): frontend to
  Vercel, backend to Render or Railway
