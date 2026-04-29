from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy import Engine, create_engine

from civicelections.candidate import build_candidate_filing_checklist
from civicelections.canvass import build_canvass_checklist


metadata = sa.MetaData()

candidate_filing_records = sa.Table(
    "candidate_filing_records",
    metadata,
    sa.Column("filing_id", sa.String(36), primary_key=True),
    sa.Column("office", sa.String(255), nullable=False),
    sa.Column("items", sa.JSON(), nullable=False),
    sa.Column("filing_review_required", sa.Boolean(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    schema="civicelections",
)

canvass_checklist_records = sa.Table(
    "canvass_checklist_records",
    metadata,
    sa.Column("canvass_id", sa.String(36), primary_key=True),
    sa.Column("election_name", sa.String(255), nullable=False),
    sa.Column("items", sa.JSON(), nullable=False),
    sa.Column("certification_required_outside_module", sa.Boolean(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    schema="civicelections",
)


@dataclass(frozen=True)
class StoredCandidateFiling:
    filing_id: str
    office: str
    items: tuple[str, ...]
    filing_review_required: bool
    created_at: datetime


@dataclass(frozen=True)
class StoredCanvassChecklist:
    canvass_id: str
    election_name: str
    items: tuple[str, ...]
    certification_required_outside_module: bool
    created_at: datetime


class ElectionWorkpaperRepository:
    """SQLAlchemy-backed candidate filing and canvass checklist workpapers."""

    def __init__(self, *, db_url: str | None = None, engine: Engine | None = None) -> None:
        base_engine = engine or create_engine(db_url or "sqlite+pysqlite:///:memory:", future=True)
        if base_engine.dialect.name == "sqlite":
            self.engine = base_engine.execution_options(schema_translate_map={"civicelections": None})
        else:
            self.engine = base_engine
            with self.engine.begin() as connection:
                connection.execute(sa.text("CREATE SCHEMA IF NOT EXISTS civicelections"))
        metadata.create_all(self.engine)

    def create_candidate_filing(
        self, *, office: str, requirements: list[str]
    ) -> StoredCandidateFiling:
        checklist = build_candidate_filing_checklist(office, requirements)
        stored = StoredCandidateFiling(
            filing_id=str(uuid4()),
            office=checklist.office,
            items=checklist.items,
            filing_review_required=checklist.filing_review_required,
            created_at=datetime.now(UTC),
        )
        with self.engine.begin() as connection:
            connection.execute(
                candidate_filing_records.insert().values(
                    filing_id=stored.filing_id,
                    office=stored.office,
                    items=list(stored.items),
                    filing_review_required=stored.filing_review_required,
                    created_at=stored.created_at,
                )
            )
        return stored

    def get_candidate_filing(self, filing_id: str) -> StoredCandidateFiling | None:
        with self.engine.begin() as connection:
            row = connection.execute(
                sa.select(candidate_filing_records).where(
                    candidate_filing_records.c.filing_id == filing_id
                )
            ).mappings().first()
        if row is None:
            return None
        data = dict(row)
        return StoredCandidateFiling(
            filing_id=data["filing_id"],
            office=data["office"],
            items=tuple(data["items"]),
            filing_review_required=data["filing_review_required"],
            created_at=data["created_at"],
        )

    def create_canvass_checklist(
        self, *, election_name: str, items: list[str]
    ) -> StoredCanvassChecklist:
        checklist = build_canvass_checklist(election_name, items)
        stored = StoredCanvassChecklist(
            canvass_id=str(uuid4()),
            election_name=checklist.election_name,
            items=checklist.items,
            certification_required_outside_module=checklist.certification_required_outside_module,
            created_at=datetime.now(UTC),
        )
        with self.engine.begin() as connection:
            connection.execute(
                canvass_checklist_records.insert().values(
                    canvass_id=stored.canvass_id,
                    election_name=stored.election_name,
                    items=list(stored.items),
                    certification_required_outside_module=(
                        stored.certification_required_outside_module
                    ),
                    created_at=stored.created_at,
                )
            )
        return stored

    def get_canvass_checklist(self, canvass_id: str) -> StoredCanvassChecklist | None:
        with self.engine.begin() as connection:
            row = connection.execute(
                sa.select(canvass_checklist_records).where(
                    canvass_checklist_records.c.canvass_id == canvass_id
                )
            ).mappings().first()
        if row is None:
            return None
        data = dict(row)
        return StoredCanvassChecklist(
            canvass_id=data["canvass_id"],
            election_name=data["election_name"],
            items=tuple(data["items"]),
            certification_required_outside_module=data["certification_required_outside_module"],
            created_at=data["created_at"],
        )
