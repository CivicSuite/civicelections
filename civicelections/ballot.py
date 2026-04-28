"""Ballot question plain-language summary drafts."""
from dataclasses import dataclass


@dataclass(frozen=True)
class BallotSummaryDraft:
    title: str
    summary_points: tuple[str, ...]
    clerk_approval_required: bool
    not_ballot_language: bool


def draft_ballot_summary(title: str, facts: list[str]) -> BallotSummaryDraft:
    points = tuple(fact.strip() for fact in facts if fact.strip()) or ("Add official ballot facts.",)
    return BallotSummaryDraft(title.strip(), points, True, True)
