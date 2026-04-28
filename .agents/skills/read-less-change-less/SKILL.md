---
name: read-less-change-less
description: Use this when modifying code in an existing repository and the task seems local or well-scoped. Prefer minimal file reading, minimal patches, and avoid broad refactors.
---

# Read less, change less

When working on a coding task in this repository:

- Read only the files that are directly relevant to the requested change.
- Do not scan the whole repository unless the dependency chain is genuinely unclear.
- Before editing, identify the smallest set of files that must be changed.
- Prefer narrow patches over broad rewrites.
- Do not refactor unrelated code.
- Do not rename files, symbols, or functions unless required by the task.
- Preserve existing interfaces, output formats, and project conventions unless the user explicitly asks to change them.

## Operating rule
For each task:
1. Infer the likely entrypoint and affected files.
2. Read only those files first.
3. Make the smallest viable patch.
4. Verify only the impacted paths and invariants.

## Default bias
- Minimize token usage.
- Minimize touched files.
- Minimize explanation length.
- Minimize risk of regressions from unnecessary edits.