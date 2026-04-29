# Changelog

## [0.1.1] - 2026-04-28

### Added

- Optional SQLAlchemy-backed candidate filing and canvass checklist workpaper records via `CIVICELECTIONS_WORKPAPER_DB_URL`.
- Candidate filing and canvass checklist retrieval endpoints for persisted records.

### Changed

- Dependency-alignment release: moved CivicElections to `civiccore==0.3.0` while preserving the existing v0.1.0 runtime foundation behavior.
- Updated CI, verification gates, package metadata, docs, runtime tests, landing page, and public UI labels for the v0.1.1 release.

## [0.1.0] - 2026-04-27

### Added

- CivicElections package, FastAPI runtime, voter guidance, candidate filing checklists, worker training Q&A, ballot-summary drafts, campaign-finance summaries, canvass checklists, accessibility review, docs, tests, browser QA, and release gates.

### Not Shipped

- Voter registration, ballot marking, tabulation, election conduct automation, campaign finance system of record, official certification, live LLM calls, or election-system connector runtime.
