# Production Depth: Election Workpaper Persistence

## Summary

CivicElections now supports optional SQLAlchemy-backed candidate filing and canvass checklist workpaper records through `CIVICELECTIONS_WORKPAPER_DB_URL`.

## Shipped

- `ElectionWorkpaperRepository` with schema-aware SQLAlchemy tables.
- Persisted candidate filing checklist records with `filing_id`.
- Persisted canvass checklist records with `canvass_id`.
- Retrieval endpoints:
  - `GET /api/v1/civicelections/candidate-filing/{filing_id}`
  - `GET /api/v1/civicelections/canvass-checklist/{canvass_id}`
- Actionable `503` guidance when persistence is not configured.
- Regression tests for repository reload, API round trip, missing-record `404`, no-config `503`, and stateless fallback behavior.

## Still Not Shipped

- Voter registration.
- Ballot marking or tabulation.
- Election conduct automation.
- Official certification.
- Live LLM calls.
- Election-system connectors.
