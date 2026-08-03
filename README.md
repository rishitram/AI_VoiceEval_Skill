# Voice Eval Skill

This repo is a sharp, reusable evaluation skill for voice-agent systems. It is built to help you test whether a bot can actually hold a real conversation, follow the task, recover from mistakes, and avoid obvious quality failures.

The value here is simple: instead of relying on gut feel or scattered notes, you get a structured way to score calls, rank weak spots, and turn them into actionable bug reports. I tested this skill with OpenClaw using the llama3.1:8b model as the judge, and used it as a repeatable harness-friendly workflow: feed it transcripts, run the evaluation, inspect the weakest calls, and build a clear record of what needs to improve.

## Why this skill stands out

A good voice agent is not just one that sounds polished. It has to be accurate, efficient, resilient, and easy to reason about when things go wrong. This repo gives you a practical system for evaluating that.

It helps you:

- score conversations against a clear rubric
- catch issues like hallucinated information, weak recovery, bad pacing, and wasted turns
- surface the weakest calls first so your review time is spent where it matters most
- turn transcript analysis into a repeatable bug-reporting workflow

## What is in this repo

- [transcripts](transcripts): a corpus of call transcripts ready for evaluation
- [scripts](scripts): the evaluator, scoring logic, prompts, and schema that power the workflow
- [results.json](results.json): the ranked output from the latest evaluation run
- [references](references): notes on transcript format, metrics, and bug-report structure

## Why this repo is useful

- It gives you a repeatable evaluation loop instead of one-off impressions.
- It helps you focus on the most important problems quickly.
- It turns transcript review into something actionable: score, inspect, report, and improve.
- It is reusable. The same skill can be run against new batches of calls over and over as your system evolves.

## How to run the evaluation

From the repository root:

```powershell
python scripts/run_eval.py transcripts --out results.json --sort overall
```

That command reads every transcript in [transcripts](transcripts), scores the calls, and writes the ranked results to [results.json](results.json).

## How to read the results

Open [results.json](results.json) and start with the lowest-scoring calls. Those are the best candidates for deeper inspection and bug reporting.

## Why this repo is worth keeping

This is more than a one-off artifact. It is a reusable evaluation package for testing voice-agent behavior end to end: from transcript collection and scoring to bug finding and improvement. That is what makes it genuinely useful.
