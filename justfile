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

# Free disk space with each tool's own cache clean command
gc:
    pre-commit gc
    prek cache gc
    uv cache prune
    npm cache clean --force
    pnpm store prune
    bun pm cache rm
    deno clean
    brew cleanup --prune=all
    docker image prune --all --force
    docker builder prune --all --force
    sudo apt-get clean
