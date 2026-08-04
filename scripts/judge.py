"""
Judge: sends metric prompts to a locally-running Ollama model,
parses structured JSON responses, and combines results using
weighted scoring with critical failure overrides.
"""

import json
import re
import requests

from prompts import ALL_METRICS
from schema import Transcript
from timing import count_long_gaps, score_pacing


OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "llama3.1:8b"


# Metric importance weights
# Must sum to 1.0
METRIC_WEIGHTS = {
    "goal_completion": 0.30,
    "factual_accuracy": 0.25,
    "information_gathering": 0.15,
    "error_recovery": 0.10,
    "communication_quality": 0.05,
    "conversation_flow": 0.05,
    "pacing_timing": 0.10,
}


# Scores below this threshold fail automatically
FAIL_THRESHOLD = 5.0
BORDERLINE_THRESHOLD = 7.0


def _extract_json(raw: str) -> dict:
    """
    Extract JSON from model output.
    Handles markdown code blocks and extra text.
    """

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

    raise ValueError(
        f"Could not parse JSON from model output:\n{raw}"
    )


def call_ollama(
    prompt: str,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.1
) -> dict:
    """
    Send prompt to local Ollama model.
    """

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False,
        "options": {
            "temperature": temperature
        },
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=120
    )

    response.raise_for_status()

    content = response.json()["message"]["content"]

    return _extract_json(content)


def run_metric(
    transcript: Transcript,
    metric_name: str,
    model: str = DEFAULT_MODEL,
    retries: int = 2
) -> dict:
    """
    Run one LLM-based metric.
    """

    prompt_fn = ALL_METRICS[metric_name]

    prompt = prompt_fn(transcript)

    last_error = None

    for _ in range(retries + 1):
        try:
            return call_ollama(
                prompt,
                model=model
            )

        except Exception as e:
            last_error = e

    return {
        "error": str(last_error),
        "score": None,
        "critical_failure": False,
        "issues": []
    }


def calculate_weighted_score(results: dict) -> float | None:
    """
    Calculate weighted average score.

    Missing metrics are ignored.
    """

    total = 0
    weight_total = 0

    for metric, weight in METRIC_WEIGHTS.items():

        result = results.get(metric)

        if not result:
            continue

        score = result.get("score")

        if not isinstance(score, (int, float)):
            continue

        total += score * weight
        weight_total += weight

    if weight_total == 0:
        return None

    return round(total / weight_total, 2)


def find_critical_failures(results: dict) -> list:
    """
    Collect any critical failures detected by metrics.
    """

    failures = []

    for name, result in results.items():

        if not isinstance(result, dict):
            continue

        if result.get("critical_failure"):

            failures.append({
                "metric": name,
                "reason": result.get(
                    "critical_reason",
                    "Critical failure detected"
                )
            })

    return failures


def collect_issues(results: dict) -> list:
    """
    Merge issues from all metrics.
    """

    issues = []

    for metric, result in results.items():

        if not isinstance(result, dict):
            continue

        for issue in result.get("issues", []):

            issue["metric"] = metric

            issues.append(issue)

    severity_order = {
        "critical": 0,
        "major": 1,
        "minor": 2,
    }

    return sorted(
        issues,
        key=lambda x: severity_order.get(
            x.get("severity", "minor"),
            3
        )
    )


def determine_recommendation(
    score: float | None,
    critical_failures: list
) -> str:

    if critical_failures:
        return "FAIL"

    if score is None:
        return "UNKNOWN"

    if score < FAIL_THRESHOLD:
        return "FAIL"

    if score < BORDERLINE_THRESHOLD:
        return "BORDERLINE"

    return "PASS"


def evaluate_transcript(
    transcript: Transcript,
    model: str = DEFAULT_MODEL,
    metrics: list[str] | None = None
) -> dict:
    """
    Evaluate a transcript using LLM metrics and deterministic metrics.
    """

    requested_metrics = (
        metrics
        if metrics is not None
        else list(ALL_METRICS.keys())
    )

    results = {}

    # Run LLM metrics
    for metric in requested_metrics:

        if metric in ALL_METRICS:

            results[metric] = run_metric(
                transcript,
                metric,
                model=model
            )


    # Deterministic metrics
    if (
        metrics is None
        or "pacing_timing" in metrics
    ):

        results["pacing_timing"] = score_pacing(
            transcript
        )

        results["long_gap_count"] = count_long_gaps(
            transcript
        )


    # Weighted score
    overall_score = calculate_weighted_score(
        results
    )


    # Critical failures
    critical_failures = find_critical_failures(
        results
    )


    # Aggregate issues
    issues = collect_issues(
        results
    )


    results["_summary"] = {
        "overall_score": overall_score,
        "recommendation": determine_recommendation(
            overall_score,
            critical_failures
        ),
        "critical_failures": critical_failures,
        "issues": issues,
    }


    return results