"""Pure legacy record formatting, shared temporarily during boundary extraction.

No new fact presentation, markup or model-authored prose. Runtime still invokes this
compatibility function while retaining recorded facts, grounding and execution guards.
"""

import json


def render_records(records):
    """Never expose a model-authored store claim; compose actual tool envelopes verbatim."""
    sections = []
    for record in records:
        result = record["result"]
        title = record["tool"].replace("_", " ")
        if result["status"] != "ok":
            sections.append(title + ": " + result["message"])
            continue
        header = title + ": " + str(result["returned_count"]) + " of " + str(result["total_count"])
        if result["truncated"]:
            header += " (sample; more results exist)"
        sections.append(
            header + "\n" + "\n".join(json.dumps(row, ensure_ascii=False) for row in result["data"])
        )
    return "\n\n".join(sections)
