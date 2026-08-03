# Transcript format

Each transcript in [transcripts](../transcripts) is a single JSON file representing one call.

```json
{
  "call_id": "example_call",
  "scenario": {
    "description": "What the patient was trying to do",
    "goal": "The outcome that counts as success",
    "known_facts": {
      "office_hours": "Mon-Fri 8am-5pm, closed weekends"
    },
    "expects_interruptions": false
  },
  "turns": [
    {"speaker": "patient", "turn_index": 0, "timestamp": 0.0, "duration": 2.5, "text": "..."},
    {"speaker": "agent", "turn_index": 1, "timestamp": 3.0, "duration": 2.0, "text": "..."}
  ]
}
```

## Required fields

- `call_id`: unique name for the transcript
- `scenario.description`: short summary of the scenario
- `scenario.goal`: the intended outcome for the call
- `scenario.known_facts`: ground-truth facts used by the factual-accuracy metric
- `turns`: an ordered list of patient and agent turns

## Turn fields

Each turn should include:
- `speaker`: either `patient` or `agent`
- `turn_index`: increasing index for the full conversation
- `timestamp`: seconds since the call started
- `duration`: optional but recommended for pacing analysis
- `text`: the spoken content

This is the format used by the current evaluation run and by [results.json](../results.json).
