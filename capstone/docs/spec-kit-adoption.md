# GitHub Spec Kit adoption

Initialized November 7, 2026 inside capstone/, not the weekly-course repository root.
CLI: specify-cli 1.3.2. Integration: Codex skills. Script type: Bash.

Installed: .specify/ templates, scripts, workflow, configuration and constitution;
.agents/skills/speckit-* (nine skills). No Git extension, extra framework, nested Git
repository or automatic commit was added. Existing draft files were preserved. A local
pre-initialization backup is in the chat workspace's work/pre-speckit-backup/.

## Repeatable CLI

The CLI currently runs through uv's isolated environment, rather than a global install:

```sh
uv --cache-dir /private/tmp/capstone-uv-cache run --with specify-cli==1.3.2 specify version
uv --cache-dir /private/tmp/capstone-uv-cache run --with specify-cli==1.3.2 specify check
```

Start an agent in capstone/ to discover the installed skills. From a parent-directory
chat they may not appear automatically; use their explicit paths or start in capstone/.

## Adoption sequence

1. Reconcile SPEC-001–008 against original course documents.
2. Create the authoritative feature spec from reconciled requirements/hero cases;
   preserve historical review evidence and mark superseded draft entry points.
3. Use clarify, plan, tasks and analyze for a consistent feature packet.
4. Send the recorded revision to a fresh reviewer; present findings and dispositions
   to Imran. Obtain spec/design approval before implement.
5. Maintain independent code/security/evaluation reviews and final human release sign-off.

Constitution is a draft reflecting established instructions; technical baseline approval
remains pending. Source documents and reviewers, not generic templates, determine actual
capstone requirements. Tooling initialization does not fix the eight findings.

[Official existing-project adoption guide](https://github.github.com/spec-kit/how-to/existing-projects.html)
