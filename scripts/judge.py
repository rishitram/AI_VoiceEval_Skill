"""
Judge: sends each metric prompt to a locally-running Ollama model and parses
the structured JSON response.
"""

import json
import re
import requests

from prompts import ALL_METRICS
from schema import Transcript
from timing import score_pacing

OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "llama3.1:8b"


def _extract_json(raw: str) -> dict:
    raw = raw.strip()
    raw = re.sub(r"^```(json)?", "", raw).strip()
    raw = re.sub(r"```$", "", raw).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    raise ValueError(f"Could not parse JSON from model output:\n{raw}")


def call_ollama(prompt: str, model: str = DEFAULT_MODEL, temperature: float = 0.1) -> dict:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {"temperature": temperature},
    }
    resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
    resp.raise_for_status()
    content = resp.json()["message"]["content"]
    return _extract_json(content)


def run_metric(transcript: Transcript, metric_name: str, model: str = DEFAULT_MODEL,
                retries: int = 2) -> dict:
    prompt_fn = ALL_METRICS[metric_name]
    prompt = prompt_fn(transcript)
    last_err = None
    for _ in range(retries + 1):
        try:
            return call_ollama(prompt, model=model)
        except Exception as e:
            last_err = e
    return {"error": str(last_err), "score": None}


def evaluate_transcript(transcript: Transcript, model: str = DEFAULT_MODEL,
                         metrics: list[str] | None = None) -> dict:
    llm_metrics = metrics if metrics is not None else list(ALL_METRICS.keys())
    include_pacing = metrics is None or "pacing_timing" in metrics
    llm_metrics = [m for m in llm_metrics if m in ALL_METRICS]

    results = {}
    for name in llm_metrics:
        results[name] = run_metric(transcript, name, model=model)

    if include_pacing:
        results["pacing_timing"] = score_pacing(transcript)

    scores = [r["score"] for r in results.values() if isinstance(r.get("score"), (int, float))]
    results["_overall_score"] = round(sum(scores) / len(scores), 2) if scores else None
    return results
