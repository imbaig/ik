"""Labeled extraction evaluator. Guardrail probes are not live LLM quality evidence."""

import argparse
import hashlib
import json
from pathlib import Path

from music_store.memory import supported_preferences
from music_store.model import MEMORY_PROMPT_VERSION


def evaluate(cases, *, extractor=None):
    """If extractor is absent, feed adversarial candidate probes to the evidence filter."""
    rows, tp, fp, fn = [], 0, 0, 0
    failures = 0
    for case in cases:
        try:
            candidates = (
                case["candidate_probe"]
                if extractor is None
                else extractor.extract([case["text"]]).music_preferences
            )
            actual = set(supported_preferences(candidates, [case["text"]]))
            error = False
        except Exception:
            actual, error = set(), True
            failures += 1
        expected = {value.strip().casefold() for value in case["expected"]}
        tp += len(actual & expected)
        fp += len(actual - expected)
        fn += len(expected - actual)
        rows.append(
            {
                "id": case["id"],
                "expected": sorted(expected),
                "actual": sorted(actual),
                "exact_match": actual == expected and not error,
                "extraction_error": error,
            }
        )
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None
    return {
        "mode": "guardrail_probe" if extractor is None else "live_extractor",
        "live_model_quality_validated": False,
        "live_calls_executed": extractor is not None,
        "evaluation_completed": True,
        "prompt_version": MEMORY_PROMPT_VERSION,
        "case_count": len(cases),
        "true_positive": tp,
        "false_positive": fp,
        "false_negative": fn,
        "precision": precision,
        "recall": recall,
        "extraction_failures": failures,
        "target_met": len(cases) >= 30
        and extractor is not None
        and failures == 0
        and precision is not None
        and recall is not None
        and precision >= 0.95
        and recall >= 0.90,
        "cases": rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["guardrail", "live"], default="guardrail")
    parser.add_argument("--cases", type=Path, default=Path("evals/preference-cases.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    extractor = None
    settings = None
    if args.mode == "live":
        from music_store.config import load_settings
        from music_store.model import LLMPreferenceExtractor

        settings = load_settings()
        if not settings.openai_api_key.get_secret_value().strip():
            report = {
                "mode": "live_extractor",
                "status": "blocked_missing_api_key",
                "live_model_quality_validated": False,
                "target_met": False,
                "attempted_cases": 0,
                "planned_cases": len(json.loads(args.cases.read_text())),
                "cases_sha256": hashlib.sha256(args.cases.read_bytes()).hexdigest(),
            }
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(report, indent=2) + "\n")
            print(json.dumps(report))
            return 1
        extractor = LLMPreferenceExtractor(settings)
    report = evaluate(json.loads(args.cases.read_text()), extractor=extractor)
    if settings is not None:
        report["model"] = settings.model_name
        report["temperature"] = settings.temperature
    report["cases_sha256"] = hashlib.sha256(args.cases.read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({key: value for key, value in report.items() if key != "cases"}))

    return 0 if args.mode == "guardrail" or report["target_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
