# List all commands
_default:
    @just --list  --unsorted

# Run the playbook, extra args are forwarded (e.g. `just run --tags llm`)
run *args:
    uv run ansible-playbook --ask-become-pass playbook.yml {{ args }}

# Update dependencies and pre-commit hooks, then run all hooks
update:
    uv sync --upgrade
    uv run ansible-galaxy collection install -r requirements.yml --upgrade
    uv run ansible-galaxy role install -r requirements.yml --force
    pre-commit autoupdate --freeze
    pre-commit run -a
