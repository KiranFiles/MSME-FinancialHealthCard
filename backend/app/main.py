from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import search, consent, score, narrative, portfolio

app = FastAPI(title="MSME Financial Health Card API")

# Allow local dev and Vercel frontend origin. Replace the vercel.app URL
# with your actual deployed frontend domain once you have it.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://*.vercel.app",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router, tags=["search"])
app.include_router(consent.router, tags=["consent"])
app.include_router(score.router, tags=["score"])
app.include_router(narrative.router, tags=["narrative"])
app.include_router(portfolio.router, tags=["portfolio"])


@app.get("/")
def root():
    return {"status": "ok", "service": "MSME Financial Health Card API is running successfully"}


@app.get("/health")
def health():
    return {"status": "API is healthy"}
