"""Candidate filing checklist support."""
from dataclasses import dataclass


@dataclass(frozen=True)
class CandidateFilingChecklist:
    office: str
    items: tuple[str, ...]
    filing_review_required: bool


def build_candidate_filing_checklist(office: str, requirements: list[str]) -> CandidateFilingChecklist:
    items = tuple(r.strip() for r in requirements if r.strip()) or ("Add official candidate filing requirements.",)
    return CandidateFilingChecklist(office.strip(), ("Confirm filing calendar.", *items, "Clerk review required before publication."), True)
