# ubuntu-dev-ansible

I use this project to configure my ubuntu machine. That way I can wipe
and re-install with less effort.

## Getting Started

1. `sudo apt install curl`
2. `curl -LsSf https://astral.sh/uv/install.sh | sh`
3. `uv sync -p 3.12 && . .venv/bin/activate`
4. `ansible-galaxy role install markosamuli.linuxbrew hurricanehrndz.rustup`
5. `ansible-playbook --ask-become-pass playbook.yml`

## Credits

Thank you, Adam, for your [macos-ansible project](https://github.com/adamchainz/mac-ansible) and [blog post](https://adamj.eu/tech/2019/03/20/how-i-provision-my-macbook-with-ansible/), that inspired this project.
