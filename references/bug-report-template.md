# Bug report template.

Use this format when turning eval findings into submission-ready notes.

```markdown
## Bug: [short title]

**Severity:** High | Medium | Low
**Call:** [call_id]
**Turn:** [turn_index]
**Metric:** [metric name]

**Details:** Describe what happened, quote the agent’s response if useful, and explain what should have happened instead.

**Why it matters:** Explain the impact on the patient experience, trust, or safety.
```

## Example

```markdown
## Bug: Agent confirms a weekend appointment despite closed office hours

**Severity:** High
**Call:** longer_office_hours_conflict
**Turn:** 1
**Metric:** factual_accuracy

**Details:** The agent said the office was open on Saturday morning, but the known facts say the office is closed on weekends.

**Why it matters:** This can mislead the patient and cause a failed or confusing booking attempt.
```

## Good bug-report habits

- Keep it specific and grounded in the transcript.
- Cite the turn and the metric that flagged the issue.
- Focus on outcomes that matter to a patient, not minor wording details.
- Prefer a few strong, clear issues over a long list of weak nitpicks.
