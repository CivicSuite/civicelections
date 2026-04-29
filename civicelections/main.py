"""FastAPI runtime foundation for CivicElections."""
import os

from civiccore import __version__ as CIVICCORE_VERSION
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from civicelections import __version__
from civicelections.accessibility import review_accessible_material
from civicelections.ballot import draft_ballot_summary
from civicelections.candidate import build_candidate_filing_checklist
from civicelections.canvass import build_canvass_checklist
from civicelections.finance import summarize_campaign_finance
from civicelections.guidance import ElectionSource, answer_voter_question
from civicelections.persistence import (
    ElectionWorkpaperRepository,
    StoredCandidateFiling,
    StoredCanvassChecklist,
)
from civicelections.public_ui import render_public_lookup_page
from civicelections.training import answer_worker_training_question

app = FastAPI(title="CivicElections", version=__version__, description="Election administration support foundation for CivicSuite.")

_workpaper_repository: ElectionWorkpaperRepository | None = None
_workpaper_db_url: str | None = None

SOURCES = [ElectionSource("s1", "Polling place guide", "Where to vote and ballot information", "Election Guide 1")]

class QuestionRequest(BaseModel):
    question: str
class CandidateRequest(BaseModel):
    office: str
    requirements: list[str]
class BallotRequest(BaseModel):
    title: str
    facts: list[str]
class TrainingRequest(BaseModel):
    topic: str
    procedures: list[str]
class FinanceRequest(BaseModel):
    filer: str
    filings: list[str]
class CanvassRequest(BaseModel):
    election_name: str
    items: list[str]
class AccessibilityRequest(BaseModel):
    material_name: str
    languages: list[str]

@app.get("/")
def root() -> dict[str, str]:
    return {"name":"CivicElections","version":__version__,"status":"election administration foundation plus workpaper persistence","message":"CivicElections guidance, candidate filing checklists, worker training Q&A, ballot-summary drafts, campaign-finance summaries, canvass checklists, optional database-backed candidate/canvass workpapers, accessibility review, and public UI foundation are online; voter registration, ballot marking, tabulation, election conduct automation, official certification, live LLM calls, and election-system connector runtime are not implemented yet.","next_step":"Post-v0.1.1 roadmap: official source imports, clerk review queues, and CivicAccess handoffs"}

@app.get("/health")
def health() -> dict[str, str]:
    return {"status":"ok","service":"civicelections","version":__version__,"civiccore_version":CIVICCORE_VERSION}

@app.get("/civicelections", response_class=HTMLResponse)
def public_page() -> str:
    return render_public_lookup_page()

@app.post("/api/v1/civicelections/voter-guidance")
def voter_guidance(request: QuestionRequest) -> dict[str, object]:
    return answer_voter_question(request.question, SOURCES).__dict__

@app.post("/api/v1/civicelections/candidate-filing")
def candidate_filing(request: CandidateRequest) -> dict[str, object]:
    if _workpaper_database_url() is not None:
        stored = _get_workpaper_repository().create_candidate_filing(
            office=request.office,
            requirements=request.requirements,
        )
        return _stored_candidate_filing_response(stored)
    payload = build_candidate_filing_checklist(request.office, request.requirements).__dict__
    payload["filing_id"] = None
    return payload

@app.get("/api/v1/civicelections/candidate-filing/{filing_id}")
def get_candidate_filing(filing_id: str) -> dict[str, object]:
    if _workpaper_database_url() is None:
        raise HTTPException(status_code=503, detail={"message":"CivicElections workpaper persistence is not configured.","fix":"Set CIVICELECTIONS_WORKPAPER_DB_URL to retrieve persisted candidate filing checklists."})
    stored = _get_workpaper_repository().get_candidate_filing(filing_id)
    if stored is None:
        raise HTTPException(status_code=404, detail={"message":"Candidate filing checklist record not found.","fix":"Use a filing_id returned by POST /api/v1/civicelections/candidate-filing."})
    return _stored_candidate_filing_response(stored)

@app.post("/api/v1/civicelections/ballot-summary")
def ballot_summary(request: BallotRequest) -> dict[str, object]:
    return draft_ballot_summary(request.title, request.facts).__dict__

@app.post("/api/v1/civicelections/worker-training")
def worker_training(request: TrainingRequest) -> dict[str, object]:
    return answer_worker_training_question(request.topic, request.procedures).__dict__

@app.post("/api/v1/civicelections/campaign-finance-summary")
def campaign_finance(request: FinanceRequest) -> dict[str, object]:
    return summarize_campaign_finance(request.filer, request.filings).__dict__

@app.post("/api/v1/civicelections/canvass-checklist")
def canvass(request: CanvassRequest) -> dict[str, object]:
    if _workpaper_database_url() is not None:
        stored = _get_workpaper_repository().create_canvass_checklist(
            election_name=request.election_name,
            items=request.items,
        )
        return _stored_canvass_response(stored)
    payload = build_canvass_checklist(request.election_name, request.items).__dict__
    payload["canvass_id"] = None
    return payload

@app.get("/api/v1/civicelections/canvass-checklist/{canvass_id}")
def get_canvass(canvass_id: str) -> dict[str, object]:
    if _workpaper_database_url() is None:
        raise HTTPException(status_code=503, detail={"message":"CivicElections workpaper persistence is not configured.","fix":"Set CIVICELECTIONS_WORKPAPER_DB_URL to retrieve persisted canvass checklists."})
    stored = _get_workpaper_repository().get_canvass_checklist(canvass_id)
    if stored is None:
        raise HTTPException(status_code=404, detail={"message":"Canvass checklist record not found.","fix":"Use a canvass_id returned by POST /api/v1/civicelections/canvass-checklist."})
    return _stored_canvass_response(stored)

@app.post("/api/v1/civicelections/accessibility-review")
def accessibility(request: AccessibilityRequest) -> dict[str, object]:
    return review_accessible_material(request.material_name, request.languages).__dict__

@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> Response:
    """Return an empty favicon response so browser QA has a clean console."""

    return Response(status_code=204)

def _workpaper_database_url() -> str | None:
    return os.environ.get("CIVICELECTIONS_WORKPAPER_DB_URL")

def _get_workpaper_repository() -> ElectionWorkpaperRepository:
    global _workpaper_db_url, _workpaper_repository
    db_url = _workpaper_database_url()
    if db_url is None:
        raise RuntimeError("CIVICELECTIONS_WORKPAPER_DB_URL is not configured.")
    if _workpaper_repository is None or db_url != _workpaper_db_url:
        _dispose_workpaper_repository()
        _workpaper_db_url = db_url
        _workpaper_repository = ElectionWorkpaperRepository(db_url=db_url)
    return _workpaper_repository

def _dispose_workpaper_repository() -> None:
    global _workpaper_repository
    if _workpaper_repository is not None:
        _workpaper_repository.engine.dispose()
        _workpaper_repository = None

def _stored_candidate_filing_response(stored: StoredCandidateFiling) -> dict[str, object]:
    return {
        "filing_id": stored.filing_id,
        "office": stored.office,
        "items": list(stored.items),
        "filing_review_required": stored.filing_review_required,
        "created_at": stored.created_at.isoformat(),
    }

def _stored_canvass_response(stored: StoredCanvassChecklist) -> dict[str, object]:
    return {
        "canvass_id": stored.canvass_id,
        "election_name": stored.election_name,
        "items": list(stored.items),
        "certification_required_outside_module": stored.certification_required_outside_module,
        "created_at": stored.created_at.isoformat(),
    }
