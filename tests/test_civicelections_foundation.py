from civicelections import __version__
from civicelections.accessibility import review_accessible_material
from civicelections.ballot import draft_ballot_summary
from civicelections.candidate import build_candidate_filing_checklist
from civicelections.canvass import build_canvass_checklist
from civicelections.finance import summarize_campaign_finance
from civicelections.guidance import ElectionSource, answer_voter_question
from civicelections.training import answer_worker_training_question


def test_version_is_release_version():
    assert __version__ == "0.1.0"


def test_voter_guidance_is_cited_and_not_registration():
    result = answer_voter_question("where vote", [ElectionSource("s1", "Vote guide", "where to vote", "Guide 1")])
    assert result.citations == ("Guide 1",)
    assert "not a voter registration system" in result.boundary


def test_candidate_filing_requires_clerk_review():
    assert build_candidate_filing_checklist("Mayor", ["Petition"]).filing_review_required is True


def test_ballot_summary_is_not_official_language():
    draft = draft_ballot_summary("Tax question", ["Funds parks"])
    assert draft.clerk_approval_required is True
    assert draft.not_ballot_language is True


def test_worker_training_requires_supervisor_review():
    assert answer_worker_training_question("check-in", ["Verify ID per manual"]).supervisor_review_required is True


def test_campaign_finance_is_not_system_of_record():
    assert summarize_campaign_finance("Committee", ["Filed report"]).not_system_of_record is True


def test_canvass_certification_outside_module():
    assert build_canvass_checklist("2027", ["Reconcile ballots"]).certification_required_outside_module is True


def test_accessibility_review_recommends_civicaccess_handoff():
    assert review_accessible_material("ballot guide", ["Spanish"]).civicaccess_handoff_recommended is True
