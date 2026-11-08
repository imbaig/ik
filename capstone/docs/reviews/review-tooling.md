# Review tooling shortlist — researched November 7, 2026

## Recommended minimal stack

- Spec/design review: separate Codex reviewer session plus the versioned project-specific
  reviewer brief, source documents and immutable input manifest. A skill is a reusable
  instruction package; the harness is the runner/context/tools/artifact workflow around it.
- Code review: separate reviewer with diff, approved spec and tests. Superpowers offers
  requesting-code-review and receiving-code-review workflows; adapt only after inspecting
  instructions. Imran's mandatory-finding policy takes precedence over author pushback.
- Security: OpenAI security-best-practices (Python support) and security-threat-model are
  candidates for code/trust-boundary review. Neither alone covers course/spec correctness.
- Application evaluation: local pytest with SQL-truth and isolation assertions first;
  optional LangSmith dataset/trace evaluation for live multi-turn runs. Agent review and
  application evaluation serve different purposes; a model judge cannot replace exact
  ownership or invoice-total checks.
- Reviewer-quality evaluation: seed a copied spec with known omissions/contradictions,
  run the reviewer, measure detected known defects, unsupported findings and instruction
  compliance. Preserve clean originals. This harness is proposed, not implemented.

## Sources

- [Codex skill authoring](https://learn.chatgpt.com/docs/build-skills)
- [Systematically evaluating skills](https://developers.openai.com/blog/eval-skills)
- [Superpowers requesting review](https://github.com/obra/superpowers/blob/main/skills/requesting-code-review/SKILL.md)
- [Superpowers receiving review](https://github.com/obra/superpowers/blob/main/skills/receiving-code-review/SKILL.md)
- [OpenAI security review](https://github.com/openai/skills/blob/main/skills/.curated/security-best-practices/SKILL.md)
- [OpenAI threat modeling](https://github.com/openai/skills/blob/main/skills/.curated/security-threat-model/SKILL.md)
- [LangSmith evaluation](https://www.langchain.com/langsmith/evaluation)

No third-party skill/plugin has been installed. No hosted evaluation service is enabled.
The first spec review uses the explicit project brief in its assignment rather than a
newly installed skill. Reusable skill packaging can follow once the workflow is validated.

## Additional official implementation references

- [LangGraph test patterns](https://docs.langchain.com/oss/python/langgraph/test)
- [LangSmith pytest integration](https://docs.langchain.com/langsmith/pytest)
- [Ruff](https://docs.astral.sh/ruff/) — mechanical lint/format checks, not sign-off.

Research was performed in a separate read-only agent session,
`/root/review_harness_research`. The initial spec reviewer is `/root/spec_review`.
A repo-local capstone-specific skill is recommended for later packaging; currently the
versioned reviewer brief is the active review instruction.
