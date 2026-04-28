"""Canvass and results publication checklist support."""
from dataclasses import dataclass


@dataclass(frozen=True)
class CanvassChecklist:
    election_name: str
    items: tuple[str, ...]
    certification_required_outside_module: bool


def build_canvass_checklist(election_name: str, items: list[str]) -> CanvassChecklist:
    checklist = tuple(item.strip() for item in items if item.strip()) or ("Add official canvass steps.",)
    return CanvassChecklist(election_name.strip(), ("Verify unofficial/official status.", *checklist, "Election official certification happens outside CivicElections."), True)
