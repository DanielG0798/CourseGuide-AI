# Contributing to CourseGuide AI

## Branching

- `main` is the working branch for the team.
- Create a feature branch for each milestone task: `git checkout -b m2/readme-update`.
- Open a pull request into `main` when ready. Another teammate should review before merging.

## Commits

- Write clear commit messages: `Add course policy loader` not `update`.
- Both technical and business teammates should commit code, docs, tests, or reports.

## Before committing

```bash
source .venv/bin/activate
bash scripts/run_tests.sh
```

## Environment variables

- Copy `.env.example` to `.env` and fill in real keys.
- Never commit `.env` or API keys.

## Where to put files

- Agent code: `src/m2/`, `src/m3/`, `src/m4/`
- Shared helpers: `src/shared/`
- MCP servers: `mcp_servers/`
- Tests: `tests/m2/`, `tests/m3/`, `tests/m4/`
- Reports: `docs/milestone_01/`, `docs/milestone_02/`, etc.
