"""Campaign finance publication summary support."""
from dataclasses import dataclass


@dataclass(frozen=True)
class CampaignFinanceSummary:
    filer: str
    summary_points: tuple[str, ...]
    not_system_of_record: bool


def summarize_campaign_finance(filer: str, filings: list[str]) -> CampaignFinanceSummary:
    points = tuple(filing.strip() for filing in filings if filing.strip()) or ("No filing details supplied.",)
    return CampaignFinanceSummary(filer.strip(), points, True)
