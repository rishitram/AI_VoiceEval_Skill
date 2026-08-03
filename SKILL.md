---
name: voice-eval
description: >-
  Evaluate voice-agent transcripts for the Pretty Good AI engineering
  challenge. Use this skill to score calls, rank issues, and turn weak
  transcripts into a clear bug report for submission.
metadata:
  {
    "openclaw":
      {
        "emoji": "📞",
        "requires": { "bins": ["python3"] },
      },
  }
---

# Voice Eval

This skill is for scoring patient ↔ receptionist call transcripts for the
Pretty Good AI engineering challenge, but it can be used by anyone. It is intentionally lightweight: keep
all transcripts in one folder, run the evaluator, and inspect the lowest-scoring
calls.

## What this skill is for

- Score transcripts from your bot calling +1-805-439-8008
- Check goal completion, factual accuracy, efficiency, turn economy, error
  recovery, tone, and pacing
- Rank the worst calls first and turn them into useful bug reports

## Recommended repo layout

```
{baseDir}/
├── SKILL.md
├── README.md
├── scripts/
│   ├── run_eval.py
│   ├── judge.py
│   ├── prompts.py
│   ├── schema.py
│   ├── timing.py
│   └── requirements.txt
└── transcripts/
    ├── good_reschedule.json
    ├── repetition_bug.json
    └── ...
```

The old references folder is optional and not required for the evaluation flow.
For submission, the important part is the transcript corpus and the eval output.

## Prerequisites

1. Ollama running locally with a model pulled:
   ```bash
   ollama pull llama3.1:8b
   ```
2. Python dependencies:
   ```bash
   pip install -r {baseDir}/scripts/requirements.txt
   ```

## Workflow

### 1. Put transcripts in one folder

All transcript JSON files should live in {baseDir}/transcripts/. Each file
should contain one full conversation with turn-level timestamps.

### 2. Run the evaluator

```bash
python3 {baseDir}/scripts/run_eval.py {baseDir}/transcripts/ --out results.json --sort overall
```

Useful options:
- `--metrics goal_completion factual_accuracy` for a smaller run
- `--model mistral:7b` if you want a different Ollama model
- `--sort overall` to rank the weakest calls first

For a single transcript:
```bash
python3 {baseDir}/scripts/run_eval.py {baseDir}/transcripts/repetition_bug.json
```

### 3. Review the weakest calls

Open the lowest-scoring files from results.json and inspect the transcript at the
flagged turn before writing a bug report. Small local judges can be noisy, so
use them as a triage tool rather than a final source of truth.

### 4. Write your bug report

For each confirmed issue, include:
1. the call id
2. the turn index
3. what the agent said
4. why it is a problem
5. what the correct behavior should have been

## Transcript tips

- Use one JSON file per call
- Keep all files in the transcripts/ folder for simple submission and review
- Prefer longer, more realistic conversations over short one-shot tests
- Replace synthetic examples with real calls before submission when possible

## Challenge context

The goal is not to over-engineer this. For the submission, the winning
combination is a clear eval pipeline, a solid transcript corpus, and a handful
of well-explained bugs.
