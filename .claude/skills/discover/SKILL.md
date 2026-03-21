---
name: discover
description: Use when performing monthly tool audit of ubuntu-dev-ansible, checking for deprecated or redundant developer tools, or discovering new CLI tools that fit the dev profile
---

# Tool Discovery

## Overview

Monthly audit and discovery sweep for the ubuntu-dev-ansible repo. Two phases: (1) audit installed tools for deprecation, redundancy, and suboptimal installs, (2) discover new tools matching the user's dev profile. Always complete audit before discovery — audit results inform what gaps exist.

## When to Use

- Monthly tool audit cycle
- Suspecting a tool is deprecated or superseded
- Looking for new CLI tools to add to the setup
- Checking for redundant installations across package managers (e.g. same tool in both brew and uv)

## User Profile

- Primary work: Python/Django web development
- Side work: Open-source maintenance & contributions (ruff, django, shellcheck, pre-commit ecosystem)
- Tool preferences: Rust-rewritten CLI tools, modern Python tooling, TUI interfaces, brew/uv/cargo-installable
- Setup: Ubuntu machines provisioned via this ansible repo

## Step 1 — Build Tool Inventory

Read these files to build a complete inventory of every tool currently installed:

- `roles/thibaut/vars/main.yml` — tool lists: `thibaut_apt_packages`, `thibaut_brew_packages`, `thibaut_uv_tools`, `thibaut_cargo_packages`, `thibaut_deb_packages`
- `roles/thibaut/tasks/packages/*.yml` — custom installer tasks (note: `docker.yml` and `act.yml` contain post-install side-effects only — the tools themselves are in the main vars)
- `roles/thibaut/tasks/llm.yml` — LLM-specific tools installed outside the main vars

Extract every tool name and its install method. Present a brief summary:

- Total tool count
- Breakdown by install method (apt: N, brew: N, uv: N, cargo: N, deb: N, custom: N)

## Step 2 — Audit Current Setup

Analyze the installed tools for issues. Use batched parallel WebSearch calls (issue multiple searches in one tool-call block).

**Search categories** (skip categories with no installed tools):

- CLI replacements & shell productivity
- Git & version control workflow
- Python/Django development
- Code quality & formatting
- Containers & DevOps
- Monitoring & debugging
- Security & networking
- AI/LLM tooling

**Budget:** ~2 searches per relevant category (~12-16 total).

**Example search queries:**

- "best modern CLI tools 2025 2026" (cross-reference what's installed)
- "deprecated python developer tools" (check for staleness)
- "[specific-tool] deprecated alternative replacement" (for tools that seem old)
- "duplicate overlapping CLI tools" (find redundancies)

**Flag these issue types:**

- **Deprecated:** tool is no longer maintained or archived
- **Superseded:** a clearly better tool now exists for the same purpose
- **Redundant:** two installed tools do the same thing (check both brew and uv lists for duplicates)
- **Suboptimal install:** tool is available via a simpler/faster package manager than currently used
- **Renamed/moved:** tool has changed names or repos

**For each finding, record:**

- Tool name
- Status (deprecated / superseded / redundant / suboptimal install / renamed)
- What's currently installed and how
- Recommendation
- Source link

**Calibration — the kind of findings you should catch:**

- lychee is installed via both brew AND uv (redundant — keep brew, remove from uv)
- typos-cli is installed via both brew AND uv (redundant — keep brew, remove from uv)
- `n` (Node version manager) may be superseded by `mise` (polyglot version manager)

These are real issues in the current config. Use them as a baseline for the level of analysis expected.

## Step 3 — Discover New Tools

Complete the audit phase fully before starting discovery, since audit results inform what to suggest — no point recommending a tool if the audit already flagged a better alternative in that space.

Search for new tools that fit the user profile but aren't installed. Use batched parallel WebSearch calls.

**Budget:** ~2 searches per category (~16 total). Prioritize categories where the current setup has fewer tools — that's where gaps are most likely.

**Example search queries:**

- "best new CLI tools 2025 2026"
- "trending rust CLI tools github"
- "new python developer tools 2025 2026"
- "modern git workflow tools"
- "django developer tools 2025 2026"
- "best terminal TUI tools"
- "new devops CLI tools"
- "AI coding tools CLI 2025 2026"

**Filter criteria — only suggest tools that:**

- Are NOT already installed (check against the inventory)
- Are actively maintained (recent commits, not archived)
- Match user style: Rust CLIs, modern Python tooling, TUI interfaces, installable via brew/uv/cargo
- Have reasonable maturity (not a weekend project — look for >500 GitHub stars or established reputation)
- Complement existing tools without significant overlap

**For each suggestion, record:**

- Tool name and one-line description
- Category
- Why it fits this specific setup (reference existing tools it complements)
- Install method (brew / uv / cargo / apt / custom)
- Popularity signal (GitHub stars, last release date)
- Link to repo or homepage

**Target:** 5-15 quality suggestions. Quality over quantity.

**Calibration — the kind of tools you should find:**

- zoxide (smart cd replacement) — complements fzf and atuin
- delta (syntax-highlighting git diff pager) — pairs with bat/ripgrep
- lazygit (git TUI) — sibling of lazydocker which is already installed

These are examples of real gaps in the current setup. Use them as a baseline for fit and quality.

## Step 4 — Present Merged Report

Combine audit and discovery results into a single report:

```
## Tool Discovery Report — [today's date]

### Summary
- Audit: N findings (N deprecated, N superseded, N redundant, N suboptimal, N renamed)
- New tools: N suggestions across N categories

---

### Audit Findings

#### [Issue Type]

##### [Tool Name]
- **Status:** ...
- **Current:** ...
- **Recommendation:** ...
- **Source:** ...

(group by issue type, only show sections with findings)

---

### New Discoveries

#### [Category Name]

##### [Tool Name] — one-line description
- **Why it fits you:** ...
- **Install method:** ...
- **Popularity:** ...
- **Link:** ...

(group by category, only show categories with suggestions)
```

**Handling sparse results:** If web searches return nothing useful for a category, skip that category in the report. If an entire phase produces no results, still present the other phase. Never fail silently — always present whatever you found.

After presenting the report, ask:

> "Which tools would you like me to add? Which audit recommendations should I act on? You can reference them by name or number."

## Step 5 — Implement Selected Changes

For each tool the user selects:

### Simple package additions (apt/brew/uv/cargo)

Add to the appropriate list in `roles/thibaut/vars/main.yml`:

- **apt:** Add to `thibaut_apt_packages` with a comment describing the tool
- **brew:** Add to `thibaut_brew_packages` with a comment describing the tool
- **uv:** Add to `thibaut_uv_tools` as `- name: toolname # description`
- **cargo:** Add to `thibaut_cargo_packages` with a comment

Maintain alphabetical order within each section. Match the existing comment style.

### Custom installers

Create a new file at `roles/thibaut/tasks/packages/<tool-name>.yml`. Two patterns exist — pick the simpler one that fits:

**Pattern A — self-updating tools:** Try upgrade first, install if not present. See `packages/opencode.yml`, `packages/dprint.yml`.

**Pattern B — GitHub release tracking:** Fetch latest version from GitHub API, compare with installed version, download if different, clean old versions. See `packages/podman-desktop.yml`, `packages/awscli_v2.yml`.

Always use `changed_when` to track actual changes.

Then add the include to `roles/thibaut/tasks/installs.yml`:

```yaml
- name: Install <tool-name>
  ansible.builtin.import_tasks: packages/<tool-name>.yml
  tags:
    - <tool-name>
```

### Dotfiles / config

If the tool needs configuration:

1. Create the config file in `roles/thibaut/files/dotfiles/<config-path>`
2. Add the directory to the dirs loop in `roles/thibaut/tasks/system/dotfiles.yml` (if needed)
3. Add the file to the copy loop in `roles/thibaut/tasks/system/dotfiles.yml`

### Removals (for redundancy fixes)

Remove the tool from the appropriate list in `roles/thibaut/vars/main.yml`.

### Bashrc updates

If the tool needs PATH or env var additions, edit the `block:` content of the existing `blockinfile` task in `roles/thibaut/tasks/system/dotfiles.yml` (marker: `# {mark} ANSIBLE MANAGED BLOCK: tools`). Do not add a second `blockinfile` task.

### Important

- Do NOT auto-commit. Leave all changes for the user to review.
- Do NOT run the ansible playbook.
- Present a summary of all changes made at the end.
