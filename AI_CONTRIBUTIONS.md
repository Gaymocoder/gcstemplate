# AI contributions

The template is produced with use of AI "Claude" (Anthropic, via Claude Code).

## As partner / mentor
### Project itself
The design and code of the template, as well as its architecture decisions, are created and made by my hand. Claude AI is used for design and architecture reviews, discussions and explanations of tools' features, like a mentor.

### Commits and releases
All commits and releases are drafted by Claude AI and reviewed by me.

## As self-sufficient coworker
Documentation (`README.md` and `docs/`) is written and managed entirely by Claude AI without my direct participation.

## Exceptions
- `cmake/gcst/warnings.cmake` is written entirely by Claude AI;
- `AI_CONTRIBUTIONS.md` is written by me, because his dumbass just can't understand my style wishes (no offense, Claude);
- Other work done entirely by Claude is marked as such in the relevant commits.

## Marking

| Where | Mark |
|---|---|
| Commits | author `Claude Opus 5.5`, subject ends with `\| Vibe-coded` |
| New code files | first line `# Written by Claude (vibe-coded)` |

```sh
git log --author=Claude
```

Claude's work is marked since 2026-10-25. Docs and code edits made earlier aren't marked.
