# Independent spec review — November 7, 2026

Reviewer: `/root/spec_review`, separate read-only agent session. Exact model not captured.
Result: **not ready for baseline approval**. No changes or approvals made by reviewer.

This saved report transcribes the findings from the reviewer's response. The full original
response remains in the parent chat's agent tool history. Sources: both course DOCX files
in full by XML extraction, grading workbook rows 4–10, and repository Markdown. Content
review, not visual QA. No reference implementation inspected.

| ID | Severity/type | Evidence and finding | Resolution requested |
|---|---|---|---|
| SPEC-001 | High/course | requirements.md leaves source review incomplete and omits rubric: architecture 20%, tools/safety 20%, identity/HITL 15%, memory 10%, prompts 15%, testing 10%, code/deployment 10%. Guide §9; workbook C4:C10. | Full source-to-requirement-to-acceptance-to-demo matrix; update stale source/deadline status. |
| SPEC-002 | High/course | design/README/tasks omit LangChain, langchain-openai, langgraph-supervisor, python-dotenv, Pydantic v2, pytest, app.py entrypoint, requirements.txt, working Dockerfile, model/API key/base URL/temperature settings. Guide §§7–8, 5.10. | Specify stack/artifacts and clean install, python app.py, Docker build/run and endpoint configuration acceptance. |
| SPEC-003 | High/source conflict | Design chooses disk read-only SQLite; guide §4/§7 and milestone 1 require cached SQL loaded into in-memory SQLite. Milestone 3 expects structured LLM identifier extraction and SystemMessage injection; current design excludes raw verification input from LLM. | Resolve course alignment explicitly; use query-only safeguards and deterministic customer ownership regardless. |
| SPEC-004 | High/course | Broad tools lack fuzzy matching, numeric-string parsing, success/empty/error JSON, total/sample limits, deterministic genre diversity, price descending and invoice-specific rep lookup. Guide §§5.2–5.3/5.7/5.9, milestones 1–2, workbook D5/D9. | Nine named tool contracts and executable acceptance cases; friendly errors inside valid JSON. |
| SPEC-005 | High/full credit | OR-02/HC-03 omit mixed-query order. Workbook D4 requires sequential invoice-first then music. | Specify trace order, interrupt/resume and grounded synthesis; off-topic directly rejected. |
| SPEC-006 | High/course | Grounding rules incomplete: tool-first, exact unrounded numbers, honest empty, scope/defer, no training-data answers, total-count/truncation transparency. Guide §5.6, FAQ, workbook D8. | Explicit prompt contract for all agents; synthesis adds no unsupported facts. |
| SPEC-007 | High/course | Suite size/coverage unspecified. Guide says 25+ in §5.9/§8 and 28+ in §11; milestones say 11+ DB and 17+ tool tests. | Target >=28 meaningful deterministic tests, map required found/not-found/error, JSON, DB utility, phone, ordering and genre cases; document inconsistency. |
| SPEC-008 | Medium/recommendation | HC-01 album-to-track flow lacks required tool; HC-05 rep tool is invoice-specific; HC-04 restart persistence exceeds FAQ minimum. | Adapt journeys or scope extensions; load preferences into catalog agent and preserve existing values on empty extraction. |

Strengths: business framing, trusted ownership boundaries, accurate identity-demo limitation,
separation of product/development agents, and fake-versus-live validation distinction.

## Snapshot

Uncommitted files. Reviewer supplied hashes of reviewed drafts; workflow/tasks were being
edited concurrently, so those findings apply to the captured versions rather than any
later regenerated packet. Core spec baseline hashes supplied by reviewer:

- specs/design.md: f8aa379532599929665b487b73cdd29f80292b4ee7916fc622b82e3c81b7ec58
- specs/requirements.md: 0b13fd5392ad85f13dc99ecc576cc15e0dcf86b17f12a38ebe613ce9defd003a
- specs/acceptance.md: 333139c9a578df7a5213de6a1132b4aec0de71f7b2ea10d9ad7b7d7c146ad3c6
- docs/business-use-cases.md: 5b752dec2ed4999f8730a2c2cf00e1ea2959794b91f6de458a780e6e87bab85c

These findings are not human-adopted findings or milestone approval.
