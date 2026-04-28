---
name: no-rewrite-known-context
description: Use this when the repository and project context are already established. Avoid repeating known project background, architecture summaries, and previously agreed assumptions.
---

# No rewrite of known context

Assume the main project context is already known unless the current task truly requires restating it.

## Rules
- Do not repeat the full project description.
- Do not restate the architecture unless it is needed to justify a code decision.
- Do not re-explain known domain concepts already established in the repository context.
- Do not summarize previously known files unless the summary is necessary for the current change.
- Use short confirmations instead of long recaps.
- Focus on the delta: what changed, why, and where.

## Response style
Prefer:
- concise file-level reasoning
- short implementation notes
- direct patches

Avoid:
- long project summaries
- repeated explanations of known workflow
- repeated explanations of standard concepts unless explicitly requested

## Exception
Restate context only if one of these is true:
- the current task depends on a subtle architectural constraint
- the user asks for an explanation
- the earlier context appears inconsistent with the current code