# Voice Eval Submission

This repository is a compact evaluation package for the current AI voice challenge submission. It contains the transcript corpus, the evaluator, and the scored output from the current run.

## What is in this repo

- [transcripts](transcripts): the evaluated call transcripts used for this submission
- [scripts](scripts): the evaluator and scoring logic
- [results.json](results.json): the ranked evaluation output from the current run
- [references](references): short notes explaining the transcript format, metrics, and bug-report structure

## How to run the evaluation

From the repository root:

```powershell
python scripts/run_eval.py transcripts --out results.json --sort overall
```

That command reads every transcript in [transcripts](transcripts), scores the calls, and writes the ranked results to [results.json](results.json).

## How to read the results

Open [results.json](results.json) and start with the lowest-scoring calls. Those are the best candidates for inspection and bug reporting.

## Submission note

This repo is intentionally scoped to the evaluation portion of the submission. The primary artifact is the transcript corpus plus the scored evaluation output, so reviewers can inspect the calls and the findings without needing any extra setup beyond the evaluator.
