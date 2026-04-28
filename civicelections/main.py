"""FastAPI runtime foundation for CivicElections."""
from civiccore import __version__ as CIVICCORE_VERSION
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from civicelections import __version__
from civicelections.accessibility import review_accessible_material
from civicelections.ballot import draft_ballot_summary
from civicelections.candidate import build_candidate_filing_checklist
from civicelections.canvass import build_canvass_checklist
from civicelections.finance import summarize_campaign_finance
from civicelections.guidance import ElectionSource, answer_voter_question
from civicelections.public_ui import render_public_lookup_page
from civicelections.training import answer_worker_training_question

app = FastAPI(title="CivicElections", version=__version__, description="Election administration support foundation for CivicSuite.")

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
    return {"name":"CivicElections","version":__version__,"status":"election administration foundation","message":"CivicElections guidance, candidate filing checklists, worker training Q&A, ballot-summary drafts, campaign-finance summaries, canvass checklists, accessibility review, and public UI foundation are online; voter registration, ballot marking, tabulation, election conduct automation, official certification, live LLM calls, and election-system connector runtime are not implemented yet.","next_step":"Post-v0.1.1 roadmap: official source imports, clerk review queues, and CivicAccess handoffs"}

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
    return build_candidate_filing_checklist(request.office, request.requirements).__dict__

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
    return build_canvass_checklist(request.election_name, request.items).__dict__

@app.post("/api/v1/civicelections/accessibility-review")
def accessibility(request: AccessibilityRequest) -> dict[str, object]:
    return review_accessible_material(request.material_name, request.languages).__dict__

@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> Response:
    """Return an empty favicon response so browser QA has a clean console."""

    return Response(status_code=204)
