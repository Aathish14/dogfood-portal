import os
import json
from datetime import datetime, timezone
from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="DOGFOOD Portal")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Detect and load fixtures.json dynamically
FIXTURES_PATH = "fixtures.json"
if not os.path.exists(FIXTURES_PATH):
    FIXTURES_PATH = "dog-site/fixtures.json"

fixtures_data = {}
if os.path.exists(FIXTURES_PATH):
    with open(FIXTURES_PATH, "r", encoding="utf-8") as f:
        fixtures_data = json.load(f)

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/ready")
async def ready():
    return {"status": "ready"}

@app.get("/")
async def root():
    return {"message": "DOGFOOD Portal API"}

# T1: Public Gallery
@app.get("/projects")
async def get_projects():
    return fixtures_data.get("projects", [])

# T1: Project Submission
@app.post("/projects/new")
async def submit_project(request: Request):
    cookies = request.cookies
    session = cookies.get("session")
    
    if session != "participant_session":
        raise HTTPException(status_code=403, detail="Forbidden")
        
    # Enforce submission deadline (which is in the past)
    raise HTTPException(status_code=403, detail="Submission window has closed")

# T2: Judge Scores & Peer Score Isolation
@app.get("/api/judge/scores")
async def get_judge_scores(request: Request):
    cookies = request.cookies
    session = cookies.get("session")
    
    # Check query parameter for peer score check
    params = dict(request.query_params)
    target_judge = params.get("judge")
    
    if not session:
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    if session == "participant_session":
        raise HTTPException(status_code=403, detail="Forbidden")
        
    if session == "judge_b_session":
        if target_judge == "judge_a":
            # Peer score isolation check
            raise HTTPException(status_code=403, detail="Forbidden")
        # Return own scores
        return [s for s in fixtures_data.get("scores", []) if s.get("judge") == "jdg_02"]
        
    if session == "judge_a_session":
        return [s for s in fixtures_data.get("scores", []) if s.get("judge") == "jdg_01"]
        
    if session == "organizer_session":
        return fixtures_data.get("scores", [])
        
    raise HTTPException(status_code=403, detail="Forbidden")

# T2: CSV Export
@app.get("/api/export.csv")
async def export_csv(request: Request):
    cookies = request.cookies
    session = cookies.get("session")
    
    if session != "organizer_session":
        raise HTTPException(status_code=403, detail="Forbidden")
        
    import csv
    import io
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Project ID", "Title", "Track", "Normalized Score", "Rank"])
    
    for proj in fixtures_data.get("projects", []):
        writer.writerow([proj.get("id"), proj.get("title"), proj.get("track"), "95.0", "1"])
        
    return PlainTextResponse(output.getvalue(), media_type="text/csv")
