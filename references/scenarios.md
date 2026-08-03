# Scenario notes

This folder contains the transcript corpus used for the current evaluation run. Each file is a single call scenario that can be scored and inspected.

## Coverage in the current corpus

The included transcripts cover several practical categories:

- scheduling and rescheduling
- cancellations
- medication refills
- insurance and billing questions
- office hours and location questions
- edge cases such as interruptions, confusion, and repeated requests

## How to use this folder

1. Start with [results.json](../results.json) to find the weakest calls.
2. Open the corresponding transcript file in [transcripts](../transcripts).
3. Use the transcript and the metric output to write a short bug note.

This repo is meant to be a clear evaluation package for the current submission, not a general-purpose production framework.
