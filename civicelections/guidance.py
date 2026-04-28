"""Source-cited election guidance helpers."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ElectionSource:
    source_id: str
    title: str
    text: str
    citation: str
    public: bool = True


@dataclass(frozen=True)
class GuidanceAnswer:
    question: str
    citations: tuple[str, ...]
    answer_outline: tuple[str, ...]
    clerk_review_required: bool
    boundary: str


def answer_voter_question(question: str, sources: list[ElectionSource]) -> GuidanceAnswer:
    terms = [term.lower() for term in question.split() if term.strip()]
    matches = [s for s in sources if s.public and any(term in f"{s.title} {s.text}".lower() for term in terms)]
    citations = tuple(source.citation for source in matches)
    return GuidanceAnswer(
        question.strip(),
        citations,
        ("Use official election-office source text.", "Confirm dates, places, and eligibility with the clerk."),
        True,
        "CivicElections provides cited guidance only; it is not a voter registration system.",
    )
