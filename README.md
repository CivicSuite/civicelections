# CivicElections

CivicElections v0.1.1 ships election administration support foundations: cited voter guidance, candidate filing checklists, worker training Q&A, ballot-summary drafts, campaign-finance summaries, canvass checklists, accessibility review, FastAPI runtime, docs, tests, browser QA, and release gates.

It is not a voter registration system, ballot marking device, tabulator, election conduct automation system, campaign finance system of record, official certification workflow, live LLM runtime, or election-system connector.

Install:

```bash
python -m pip install -e ".[dev]"
python -m uvicorn civicelections.main:app --host 127.0.0.1 --port 8141
```

CivicElections v0.1.1 is pinned to `civiccore==0.3.0`.

Apache 2.0 code. CC BY 4.0 docs.
