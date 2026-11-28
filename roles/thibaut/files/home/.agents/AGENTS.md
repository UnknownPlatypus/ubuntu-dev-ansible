# Commit messages

- Don't use conventional commits (no `feat:`, `fix:`, `refactor:`, etc. prefixes)
- Keep commit messages to a single summary line; only use the description body when it adds essential context

# Code Conventions

- **Fix the code, not the comment**: if you need a paragraph-long comment to justify why the workaround is OK, the code is wrong — fix the code.
- **Concise comments, explain the "why"**: keep them short; break comment lines only after a `.` or `,`, never mid-sentence. Only add comments that records non-obvious decisions or trade-offs
- **Tests must earn their cost**: Each test adds maintenance: don't duplicate coverage of code paths already tested, don't re-test the framework/stdlib, and don't couple to internals (over-mocking, implementation details). See /write-python-tests.
- **Never suppress linters or type checkers**: generated code must not add `# noqa`, `# type: ignore`, or equivalent suppressions — fix the underlying issue instead. The only exception is a genuine tool false positive, and it must be paired with a comment linking to the relevant issue.

# lint / test / validation

Most project use [`just`](https://just.systems/) as task runner.
Run `just` first to list all recipes; prefer an existing recipe over raw commands, fall back only when none fits.
