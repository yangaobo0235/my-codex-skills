# Codex Skills Backup

This repository contains the portable, user-maintained Codex skills.

## Included skills

- `backend-interview-simulator`
- `kwai`
- `run-interview-note-defense`
- `write-engineering-resume`
- `write-interview-notes`

## Restore after reinstalling Codex

Install each skill from the repository using the Codex skill installer:

```powershell
python <skill-installer>/scripts/install-skill-from-github.py `
  --repo <owner>/codex-skills `
  --path skills/backend-interview-simulator `
  --path skills/kwai `
  --path skills/run-interview-note-defense `
  --path skills/write-engineering-resume `
  --path skills/write-interview-notes
```

For a private repository, authenticate GitHub first with existing Git credentials,
`gh auth login`, or `GITHUB_TOKEN`/`GH_TOKEN`. Never commit a token to this repository.

The `.system` skills and plugin-provided document/PDF/presentation/spreadsheet skills
are managed by Codex and are intentionally not copied here.
