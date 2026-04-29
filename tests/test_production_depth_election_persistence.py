from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from civicelections.main import app, _dispose_workpaper_repository
from civicelections.persistence import ElectionWorkpaperRepository


client = TestClient(app)


def test_repository_persists_candidate_filing_and_canvass(tmp_path: Path) -> None:
    db_path = tmp_path / "civicelections.db"
    db_url = f"sqlite+pysqlite:///{db_path.as_posix()}"

    repository = ElectionWorkpaperRepository(db_url=db_url)
    filing = repository.create_candidate_filing(office="Mayor", requirements=["Petition"])
    canvass = repository.create_canvass_checklist(election_name="2027", items=["Reconcile"])
    repository.engine.dispose()

    reloaded = ElectionWorkpaperRepository(db_url=db_url)
    stored_filing = reloaded.get_candidate_filing(filing.filing_id)
    stored_canvass = reloaded.get_canvass_checklist(canvass.canvass_id)
    reloaded.engine.dispose()

    assert stored_filing is not None
    assert stored_filing.office == "Mayor"
    assert stored_filing.filing_review_required is True
    assert stored_canvass is not None
    assert stored_canvass.certification_required_outside_module is True
    assert "Reconcile" in stored_canvass.items
    db_path.unlink()


def test_election_persistence_api_round_trip(monkeypatch, tmp_path: Path) -> None:
    db_path = tmp_path / "civicelections-api.db"
    monkeypatch.setenv("CIVICELECTIONS_WORKPAPER_DB_URL", f"sqlite+pysqlite:///{db_path.as_posix()}")
    _dispose_workpaper_repository()

    created_filing = client.post(
        "/api/v1/civicelections/candidate-filing",
        json={"office": "Mayor", "requirements": ["Petition"]},
    )
    filing_id = created_filing.json()["filing_id"]
    fetched_filing = client.get(f"/api/v1/civicelections/candidate-filing/{filing_id}")
    created_canvass = client.post(
        "/api/v1/civicelections/canvass-checklist",
        json={"election_name": "2027", "items": ["Reconcile"]},
    )
    canvass_id = created_canvass.json()["canvass_id"]
    fetched_canvass = client.get(f"/api/v1/civicelections/canvass-checklist/{canvass_id}")

    _dispose_workpaper_repository()
    monkeypatch.delenv("CIVICELECTIONS_WORKPAPER_DB_URL")

    assert created_filing.status_code == 200
    assert filing_id
    assert fetched_filing.status_code == 200
    assert fetched_filing.json()["filing_review_required"] is True
    assert created_canvass.status_code == 200
    assert canvass_id
    assert fetched_canvass.status_code == 200
    assert fetched_canvass.json()["certification_required_outside_module"] is True
    db_path.unlink()


def test_get_candidate_filing_without_persistence_returns_actionable_503(monkeypatch) -> None:
    monkeypatch.delenv("CIVICELECTIONS_WORKPAPER_DB_URL", raising=False)
    _dispose_workpaper_repository()

    response = client.get("/api/v1/civicelections/candidate-filing/example")

    assert response.status_code == 503
    detail = response.json()["detail"]
    assert detail["message"] == "CivicElections workpaper persistence is not configured."
    assert "Set CIVICELECTIONS_WORKPAPER_DB_URL" in detail["fix"]


def test_get_canvass_missing_id_returns_actionable_404(monkeypatch, tmp_path: Path) -> None:
    db_path = tmp_path / "civicelections-missing.db"
    monkeypatch.setenv("CIVICELECTIONS_WORKPAPER_DB_URL", f"sqlite+pysqlite:///{db_path.as_posix()}")
    _dispose_workpaper_repository()

    response = client.get("/api/v1/civicelections/canvass-checklist/missing")

    _dispose_workpaper_repository()
    monkeypatch.delenv("CIVICELECTIONS_WORKPAPER_DB_URL")

    assert response.status_code == 404
    detail = response.json()["detail"]
    assert detail["message"] == "Canvass checklist record not found."
    assert "POST /api/v1/civicelections/canvass-checklist" in detail["fix"]
    db_path.unlink()
