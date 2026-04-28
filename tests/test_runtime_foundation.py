from fastapi.testclient import TestClient

from civicelections import __version__
from civicelections.main import app

client = TestClient(app)


def test_root_reports_honest_current_state():
    payload = client.get("/").json()
    assert payload["name"] == "CivicElections"
    assert payload["version"] == __version__
    assert "voter registration" in payload["message"]
    assert "not implemented yet" in payload["message"]


def test_health_reports_civiccore_pin():
    assert client.get("/health").json() == {"status":"ok","service":"civicelections","version":"0.1.1","civiccore_version":"0.3.0"}


def test_public_ui_contains_version_boundaries_and_dependency():
    text = client.get("/civicelections").text
    assert "CivicElections v0.1.1" in text
    assert "No voter registration" in text
    assert "civiccore==0.3.0" in text


def test_api_endpoints_return_deterministic_payloads():
    assert client.post("/api/v1/civicelections/voter-guidance", json={"question":"where vote"}).status_code == 200
    assert client.post("/api/v1/civicelections/candidate-filing", json={"office":"Mayor","requirements":["Petition"]}).status_code == 200
    assert client.post("/api/v1/civicelections/ballot-summary", json={"title":"Tax","facts":["Parks"]}).json()["not_ballot_language"] is True
    assert client.post("/api/v1/civicelections/worker-training", json={"topic":"check-in","procedures":["Verify"]}).status_code == 200
    assert client.post("/api/v1/civicelections/campaign-finance-summary", json={"filer":"Committee","filings":["Report"]}).status_code == 200
    assert client.post("/api/v1/civicelections/canvass-checklist", json={"election_name":"2027","items":["Reconcile"]}).status_code == 200
    assert client.post("/api/v1/civicelections/accessibility-review", json={"material_name":"guide","languages":["Spanish"]}).status_code == 200
