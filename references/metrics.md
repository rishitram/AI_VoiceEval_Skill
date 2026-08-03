# Metrics reference

The evaluator produces a score for each call across the following dimensions:

- `goal_completion`: did the patient’s request actually get resolved?
- `efficiency`: did the patient need to repeat themselves because the agent failed to register information?
- `turn_economy`: was the call unnecessarily long?
- `factual_accuracy`: did the agent contradict known facts or itself?
- `error_recovery`: did the agent recover gracefully after confusion?
- `tone_empathy`: was the tone appropriate for a healthcare setting?
- `pacing_timing`: was the response timing reasonable?

## How to use these scores

- Start with the lowest overall scores in [results.json](../results.json).
- Open the corresponding transcript in [transcripts](../transcripts).
- Use the metric evidence to explain the issue, not just the score.

## Severity guide

- High: goal not met, policy or factual mistake, safety issue
- Medium: repeated confusion, poor recovery, avoidable loop
- Low: tone issue or minor friction
