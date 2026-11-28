# List all commands
_default:
    @just --list  --unsorted

# Run the playbook, extra args are forwarded (e.g. `just run --tags brew`)
run *args:
    uv run ansible-playbook --ask-become-pass playbook.yml {{ args }}

# Update dependencies and pre-commit hooks, then run all hooks
update: pin-installers
    uv sync --upgrade
    uv run ansible-galaxy collection install -r requirements.yml --upgrade
    uv run ansible-galaxy role install -r requirements.yml --force
    pre-commit autoupdate --freeze
    pre-commit run -a

# Re-pin each script installer's sha256 to what its url serves today
pin-installers:
    #!/usr/bin/env python3
    # The playbook only checks these on a fresh install, so drift goes unnoticed until then.
    import hashlib
    import pathlib
    import re
    import urllib.request
    path = pathlib.Path("roles/thibaut/vars/main.yml")
    def pin(match):
        # get_url's default user agent, to hash exactly what the playbook downloads.
        request = urllib.request.Request(match["url"], headers={"User-Agent": "ansible-httpget"})
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read()
        # Pinning an error or challenge page would break the next fresh install all the same.
        if not body.startswith(b"#!"):
            raise SystemExit(f"{match['url']} did not serve a shell script")
        sha256 = hashlib.sha256(body).hexdigest()
        if sha256 != match["sha256"]:
            print(f"re-pinned {match['url']}")
        return match["head"] + sha256
    text, pinned = re.subn(r"(?P<head>url: (?P<url>\S+)\n\s+sha256: )(?P<sha256>\S+)", pin, path.read_text())
    if pinned != text.count("sha256:"):
        raise SystemExit("each sha256 must sit on the line right below its url")
    path.write_text(text)
