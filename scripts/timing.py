"""
Pacing/latency metric -- computed deterministically from turn timestamps.
"""

from schema import Transcript

SLOW_RESPONSE_THRESHOLD = 3.0
VERY_SLOW_RESPONSE_THRESHOLD = 6.0
OVERLAP_TOLERANCE = 0.15


def compute_gaps(transcript: Transcript) -> list[dict]:
    gaps = []
    turns = transcript.turns
    for i, t in enumerate(turns):
        if t.speaker != "agent" or i == 0:
            continue
        prev = turns[i - 1]
        prev_end = prev.timestamp + (prev.duration or 0.0)
        gap = round(t.timestamp - prev_end, 2)
        gaps.append({"turn_index": t.turn_index, "gap_seconds": gap})
    return gaps


def score_pacing(transcript: Transcript) -> dict:
    gaps = compute_gaps(transcript)
    if not gaps:
        return {
            "score": None,
            "reasoning": "No agent turns with timing data to evaluate.",
            "gaps": [],
        }

    gap_values = [g["gap_seconds"] for g in gaps]
    avg_gap = round(sum(gap_values) / len(gap_values), 2)
    max_gap = max(gap_values)

    slow = [g for g in gaps if g["gap_seconds"] > SLOW_RESPONSE_THRESHOLD]
    very_slow = [g for g in gaps if g["gap_seconds"] > VERY_SLOW_RESPONSE_THRESHOLD]

    overlaps = [g for g in gaps if g["gap_seconds"] < -OVERLAP_TOLERANCE]
    unexpected_overlaps = overlaps if not transcript.scenario.expects_interruptions else []

    if avg_gap <= 1.5:
        score = 10
    elif avg_gap <= 2.5:
        score = 8
    elif avg_gap <= 4.0:
        score = 6
    elif avg_gap <= 6.0:
        score = 3
    else:
        score = 1

    score -= len(very_slow) * 2
    score -= len(slow) * 1
    score -= len(unexpected_overlaps) * 1
    score = max(0, min(10, score))

    reasoning_parts = [f"avg response gap {avg_gap}s across {len(gaps)} agent turns"]
    if very_slow:
        reasoning_parts.append(
            f"{len(very_slow)} turn(s) over {VERY_SLOW_RESPONSE_THRESHOLD}s (severe latency)"
        )
    elif slow:
        reasoning_parts.append(
            f"{len(slow)} turn(s) over {SLOW_RESPONSE_THRESHOLD}s (noticeable delay)"
        )
    if unexpected_overlaps:
        reasoning_parts.append(
            f"{len(unexpected_overlaps)} unexpected overlap(s) "
            f"(agent talking over the patient outside a barge-in test)"
        )

    return {
        "score": score,
        "avg_gap_seconds": avg_gap,
        "max_gap_seconds": max_gap,
        "slow_turns": slow,
        "very_slow_turns": very_slow,
        "unexpected_overlaps": unexpected_overlaps,
        "total_call_duration_seconds": transcript.total_duration(),
        "reasoning": "; ".join(reasoning_parts),
    }
