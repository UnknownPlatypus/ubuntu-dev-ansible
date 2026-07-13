# List all commands
_default:
    @just --list  --unsorted

# Update dependencies and pre-commit hooks, then run all hooks
update:
    uv sync --upgrade
    pre-commit autoupdate --freeze
    pre-commit run -a
