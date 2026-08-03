"""
CLI: evaluate one or more transcripts and print/save a summary.

Usage:
    python run_eval.py ../transcripts/
    python run_eval.py ../transcripts/good_reschedule.json --out results.json
    python run_eval.py ../transcripts/ --metrics goal_completion factual_accuracy
"""

import argparse
import json
import sys
from pathlib import Path

from judge import evaluate_transcript, DEFAULT_MODEL
from schema import Transcript


def load_transcript(path: Path) -> Transcript:
    with open(path, encoding="utf-8") as f:
        return Transcript.from_dict(json.load(f))


def collect_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    return sorted(p for p in target.rglob("*.json") if p.is_file())


def print_summary_table(all_results: dict[str, dict]):
    metric_names = None
    header = ["call_id"]
    rows = []
    for call_id, results in all_results.items():
        if metric_names is None:
            metric_names = [k for k in results.keys() if not k.startswith("_")]
            header += metric_names + ["overall"]
        row = [call_id]
        for m in metric_names:
            score = results[m].get("score")
            row.append(str(score) if score is not None else "ERR")
        row.append(str(results.get("_overall_score", "N/A")))
        rows.append(row)

    widths = [max(len(str(r[i])) for r in ([header] + rows)) for i in range(len(header))]

    def fmt_row(r):
        return " | ".join(str(c).ljust(widths[i]) for i, c in enumerate(r))

    print(fmt_row(header))
    print("-+-".join("-" * w for w in widths))
    for r in rows:
        print(fmt_row(r))


def main():
    parser = argparse.ArgumentParser(description="Evaluate call transcripts with a local Llama judge.")
    parser.add_argument("target", help="Path to a transcript .json file or a folder of them")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Ollama model name")
    parser.add_argument("--metrics", nargs="*", default=None,
                         help="Subset of metrics to run (default: all)")
    parser.add_argument("--out", default=None, help="Optional path to save full JSON results")
    parser.add_argument("--sort", choices=["call_id", "overall"], default="overall",
                         help="Sort summary table by call_id or overall score (ascending)")
    args = parser.parse_args()

    target = Path(args.target)
    files = collect_files(target)
    if not files:
        print(f"No transcript files found at {target}", file=sys.stderr)
        sys.exit(1)

    all_results = {}
    for f in files:
        transcript = load_transcript(f)
        print(f"Evaluating {transcript.call_id} ({f.name})...", file=sys.stderr)
        all_results[transcript.call_id] = evaluate_transcript(
            transcript, model=args.model, metrics=args.metrics
        )

    print()
    if args.sort == "overall":
        sorted_items = sorted(
            all_results.items(),
            key=lambda kv: kv[1].get("_overall_score") if kv[1].get("_overall_score") is not None else 999,
        )
        all_results = dict(sorted_items)

    print_summary_table(all_results)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(all_results, f, indent=2)
        print(f"\nFull results written to {args.out}")


if __name__ == "__main__":
    main()
