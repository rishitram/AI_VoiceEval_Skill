# Voice Eval Skill

This repo is a reusable evaluation harness for voice-agent systems. The idea is to move transcript review away from impressions and into a consistent, repeatable scoring process.

It is designed around a simple flow:

1. load transcripts that describe a caller, a goal, and the full exchange between caller and a voice agent
2. run a set of metrics against each transcript
3. combine those metric results into a single overall score
4. sort the calls so the worst-performing interactions are easy to inspect

## How the grading works

The evaluation is a mix of model-driven judgment and deterministic timing checks.

- `scripts/judge.py` is the core grader. For each transcript it runs one or more metric prompts, parses the JSON response from the local model, and then combines the results.
- Each metric is scored on a 0-10 scale.
- The final score is a weighted average of the selected metrics.
- If any metric reports a `critical_failure`, the call is marked as a hard fail.
- The overall recommendation is:
  - `FAIL` for critical failures or weighted score under 5
  - `BORDERLINE` for weighted score between 5 and 7
  - `PASS` for weighted score 7 and above

The main metrics are:

- `goal_completion`: did the call actually deliver the requested outcome, not just sound polite?
- `factual_accuracy`: did the agent stick to known facts and avoid contradictions or bad policy claims?
- `error_recovery`: did the agent recover cleanly when it misunderstood or went off track?
- `efficiency`: did the patient have to repeat themselves because the agent missed or ignored information?
- `turn_economy`: was the conversation concise, or did the agent use too many unnecessary turns?
- `tone_empathy`: was the agent respectful and appropriately warm for a medical office context?
- `pacing_timing`: a deterministic check of response latency, slow gaps, and agent/patient overlap based on timestamps.

That means this skill does more than just count errors: it looks at whether the call achieved the goal, whether the agent stayed factual, how well it recovered from mistakes, and whether it kept the conversation moving.

## What each file does

- `scripts/run_eval.py`
  - entry point for the evaluation workflow
  - loads transcript JSON files from a directory or a single file
  - calls `judge.evaluate_transcript` for each transcript
  - prints a summary table of metric scores and overall score
  - optionally saves the full detailed results to `results.json`

- `scripts/judge.py`
  - orchestrates metric evaluation and scoring
  - sends prompt text to a local Ollama model at `http://localhost:11434/api/chat`
  - parses the model output as JSON and normalizes the result
  - computes the weighted overall score via `METRIC_WEIGHTS`
  - detects critical failures and collects issue details across metrics
  - returns a structured result object with scores, issues, and recommendation

- `scripts/prompts.py`
  - defines the actual prompt templates used by the judge
  - every prompt asks the model to return a strict JSON object only
  - includes prompt functions for goals like:
    - `goal_completion`
    - `factual_accuracy`
    - `error_recovery`
    - `efficiency` and `turn_economy`
    - `tone_empathy`
  - these templates shape what the model looks for in the transcript

- `scripts/schema.py`
  - defines the transcript data model using `dataclasses`
  - `Transcript.from_dict` builds a typed object from JSON
  - `Transcript.as_text` formats the transcript for prompt injection
  - `Scenario` captures the caller's goal, known facts, and whether interruptions are expected

- `scripts/timing.py`
  - computes deterministic pacing and latency metrics from timestamps
  - measures agent response gaps, slow turns, and overlaps
  - returns a pacing score and list of problematic gaps
  - this is useful when you want a concrete score for responsiveness, not just language judgment

- `scripts/validate_transcripts.py`
  - checks transcript files against the expected schema
  - verifies top-level fields, turn structure, speaker labels, and consistent turn indices
  - helps catch malformed transcripts before evaluation

- `scripts/generate_transcripts.py`
  - builds the sample transcript corpus under `transcripts/`
  - contains helper functions for writing consistent call records
  - gives you examples of what the evaluation format looks like in practice

## What the repo contains

- `transcripts/`
  - ready-to-evaluate call transcripts in JSON format
  - each file has `call_id`, `scenario`, and `turns`
  - `scenario` includes a description, concrete goal, known facts, and an interruption flag

- `results.json`
  - the output from the latest run if you save it with `--out`
  - contains detailed metric results, issue lists, and overall recommendations

- `references/`
  - documentation and reference notes for transcript formatting, metrics, and bug reporting

## Running the evaluation

From the repository root:

```powershell
python scripts/run_eval.py transcripts --out results.json --sort overall
```

This reads everything under `transcripts/`, evaluates each call, and writes the full results to `results.json`.

## Reading the output

- The summary table shows each call's metric scores and overall score.
- Lower overall scores are the most important ones to review first.
- The saved JSON includes the individual metric responses, any issues found, and whether the call passed, failed, or is borderline.

## Why this is useful

This repo turns conversational evaluation into a repeatable process. Instead of guessing which calls were bad, you get a clear grading system that identifies failures, surfaces weak spots, and makes it easier to improve the voice agent over time.
