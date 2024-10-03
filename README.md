# ubuntu-dev-ansible

I use this project to configure my ubuntu machine. That way I can wipe
and re-install with less effort.

## Getting Started

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/) with the command from the site.
2. `uv venv --python 3.12`
3. `source .venv/bin/activate`
4. `uv pip install ansible`
5. `ansible-playbook playbook.yml`

## Credits

Thank you Adam for you [macos-ansible project](https://github.com/adamchainz/mac-ansible) and [blog post](https://adamj.eu/tech/2019/03/20/how-i-provision-my-macbook-with-ansible/), this is heavily inspired by your project.
