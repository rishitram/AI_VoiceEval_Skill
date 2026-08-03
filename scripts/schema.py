"""
Data schema for call transcripts fed into the eval harness.

A transcript is just JSON. No special libraries required to produce one --
your voice bot can write this format directly after each call, or you can
hand-write synthetic ones to test the evaluator itself.

Example file: transcripts/good_reschedule.json
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Turn:
    speaker: str            # "patient" or "agent"
    text: str
    turn_index: int
    timestamp: float        # seconds since call start when this turn began
    duration: Optional[float] = None   # seconds this turn took to speak, if known


@dataclass
class Scenario:
    description: str            # what the simulated patient was trying to do
    goal: str                   # the concrete, checkable end-state that counts as "success"
    known_facts: dict = field(default_factory=dict)   # ground truth the agent should respect
    expects_interruptions: bool = False


@dataclass
class Transcript:
    call_id: str
    scenario: Scenario
    turns: list[Turn]

    @staticmethod
    def from_dict(d: dict) -> "Transcript":
        scenario = Scenario(**d["scenario"])
        turns = [Turn(**t) for t in d["turns"]]
        return Transcript(call_id=d["call_id"], scenario=scenario, turns=turns)

    def as_text(self) -> str:
        lines = []
        for t in self.turns:
            label = "PATIENT" if t.speaker == "patient" else "AGENT"
            lines.append(f"[{t.turn_index}] (t={t.timestamp:.1f}s) {label}: {t.text}")
        return "\n".join(lines)

    def total_duration(self) -> Optional[float]:
        if not self.turns:
            return None
        last = self.turns[-1]
        return round(last.timestamp + (last.duration or 0.0), 2)
