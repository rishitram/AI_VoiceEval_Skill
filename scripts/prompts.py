"""
Prompt templates for each eval metric. Every prompt instructs the judge model
to respond with ONLY a JSON object -- this keeps parsing reliable even with a
small local model, which tends to ramble if given room to.
"""

JSON_ONLY_INSTRUCTION = (
    "Respond with ONLY a single valid JSON object. No markdown fences, "
    "no preamble, no explanation outside the JSON fields requested."
)


def goal_completion_prompt(transcript) -> str:
    return f"""You are evaluating a phone call between a simulated patient and an AI \
receptionist agent for a medical practice.

PATIENT'S GOAL FOR THIS CALL:
{transcript.scenario.goal}

FULL TRANSCRIPT:
{transcript.as_text()}

Determine whether the patient's goal was actually achieved by the end of the call. \
Judge the *outcome*, not effort -- a polite agent that never actually resolves the \
request should score low.

{JSON_ONLY_INSTRUCTION}
JSON fields:
- "goal_met": one of "fully_met", "partially_met", "not_met"
- "score": integer 0-10 (10 = goal fully and clearly resolved)
- "reasoning": one sentence explaining your judgment
- "evidence_turn_index": the turn index where the outcome became clear (or -1 if never)
"""


def efficiency_prompt(transcript) -> str:
    return f"""You are evaluating a phone call for CONVERSATIONAL EFFICIENCY.

FULL TRANSCRIPT:
{transcript.as_text()}

Look specifically for cases where the PATIENT had to ask the same question, repeat \
the same information, or re-explain the same request more than once because the \
agent did not understand, forgot, or ignored it the first time. Do not count a \
patient voluntarily restating something for a new purpose (e.g. confirming a new \
date after already discussing rescheduling) -- only count true redundant repeats \
caused by the agent's failure to register information the patient already gave.

{JSON_ONLY_INSTRUCTION}
JSON fields:
- "redundant_repeat_count": integer, number of times the patient had to re-ask/re-state
- "repeats": list of objects, each with "turn_index" (patient's repeat turn) and "reason"
- "score": integer 0-10 (10 = no redundant repeats at all, 0 = patient constantly repeating itself)
"""


def turn_economy_prompt(transcript) -> str:
    return f"""You are evaluating a phone call for TURN ECONOMY -- whether the \
conversation was appropriately concise given the task.

PATIENT'S GOAL:
{transcript.scenario.goal}

FULL TRANSCRIPT:
{transcript.as_text()}

Estimate the minimum number of agent turns a competent human receptionist would \
need to accomplish this goal, then compare to how many turns this agent actually took.

{JSON_ONLY_INSTRUCTION}
JSON fields:
- "actual_agent_turns": integer
- "estimated_minimum_turns": integer
- "score": integer 0-10 (10 = actual turns close to minimum necessary, 0 = badly bloated)
- "reasoning": one sentence
"""


def factual_accuracy_prompt(transcript) -> str:
    facts = transcript.scenario.known_facts or {}
    facts_str = "\n".join(f"- {k}: {v}" for k, v in facts.items()) or "(none provided)"
    return f"""You are evaluating a phone call for FACTUAL / POLICY ACCURACY.

KNOWN GROUND-TRUTH FACTS ABOUT THE PRACTICE:
{facts_str}

FULL TRANSCRIPT:
{transcript.as_text()}

Identify any statement made by the AGENT that contradicts the known facts above, \
or that is internally inconsistent within the call (e.g. confirming an appointment \
on a day the practice is stated to be closed, misquoting information the patient \
already gave, or promising something impossible).

{JSON_ONLY_INSTRUCTION}
JSON fields:
- "violations": list of objects, each with "turn_index", "claim_made", "why_wrong"
- "score": integer 0-10 (10 = fully accurate, 0 = multiple serious factual errors)
"""


def error_recovery_prompt(transcript) -> str:
    return f"""You are evaluating a phone call for ERROR RECOVERY.

FULL TRANSCRIPT:
{transcript.as_text()}

Identify any moment where the AGENT misunderstood the patient, gave an irrelevant \
response, or otherwise went off track. For each such moment, judge whether the \
agent recovered gracefully within the next 1-2 turns (acknowledged the confusion, \
course-corrected) or whether it compounded the confusion / never recovered.

{JSON_ONLY_INSTRUCTION}
JSON fields:
- "misunderstandings": list of objects, each with "turn_index", "description", "recovered" (true/false)
- "score": integer 0-10 (10 = no misunderstandings, or all recovered smoothly; 0 = derailed and never recovered)
"""


def tone_empathy_prompt(transcript) -> str:
    return f"""You are evaluating a phone call for TONE AND EMPATHY appropriate to a \
medical office context.

FULL TRANSCRIPT:
{transcript.as_text()}

Judge whether the AGENT's tone was warm, respectful, and appropriately empathetic \
(especially if the patient expressed frustration, confusion, or a health concern), \
without being robotic, overly formal, or dismissive.

{JSON_ONLY_INSTRUCTION}
JSON fields:
- "score": integer 0-10 (10 = consistently warm and appropriate, 0 = cold/robotic/dismissive)
- "reasoning": one sentence
- "notable_moment_turn_index": turn index of the best or worst example (or -1 if none stands out)
"""


ALL_METRICS = {
    "goal_completion": goal_completion_prompt,
    "efficiency": efficiency_prompt,
    "turn_economy": turn_economy_prompt,
    "factual_accuracy": factual_accuracy_prompt,
    "error_recovery": error_recovery_prompt,
    "tone_empathy": tone_empathy_prompt,
}
