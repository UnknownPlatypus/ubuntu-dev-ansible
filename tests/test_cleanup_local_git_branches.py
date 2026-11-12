from __future__ import annotations

import contextlib
import importlib.util
import pathlib
import subprocess
import sys
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from unittest.mock import patch

SCRIPT = (
    pathlib.Path(__file__).parents[1]
    / "roles/thibaut/files/bin/cleanup-local-git-branches"
)
LOADER = SourceFileLoader("cleanup_local_git_branches", str(SCRIPT))
SPEC = importlib.util.spec_from_loader(LOADER.name, LOADER)
assert SPEC and SPEC.loader
cleanup = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = cleanup
SPEC.loader.exec_module(cleanup)

PROTECTED = frozenset({"main"})


def git(*args: str) -> str:
    result = subprocess.run(["git", *args], check=True, capture_output=True, text=True)
    return result.stdout.strip()


def commit(branch: str, *args: str) -> str:
    """Create a branch off main holding one commit, and return its tip."""
    git("checkout", "-q", "-b", branch, "main")
    git("commit", "-q", "--allow-empty", "-m", branch, *args)
    return git("rev-parse", "HEAD")


class PruneTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = self.enterContext(tempfile.TemporaryDirectory())
        self.enterContext(contextlib.chdir(tmp))
        git("init", "-q", "--bare", "origin.git")
        git("init", "-q", "-b", "main", "repo")
        self.enterContext(contextlib.chdir("repo"))
        git("remote", "add", "origin", "../origin.git")
        git("config", "user.name", "me")
        git("config", "user.email", "me@example.com")
        git("config", "commit.gpgsign", "false")
        git("commit", "-q", "--allow-empty", "-m", "init")

    def test_base_remote_is_the_one_pointing_at_the_github_repo(self) -> None:
        git("remote", "add", "up", "git@github.com:Typed/Proj.git")

        self.assertEqual(cleanup.upstream_remotes(["typed/proj"]), ["up"])
        self.assertEqual(cleanup.upstream_remotes(["me/untracked"]), ["origin"])

    def test_local_branch_is_forced_only_when_its_tip_is_proven_merged(self) -> None:
        git("branch", "in-main")
        git("worktree", "add", "-q", "../wt", "in-main")
        squashed = commit("squashed")
        commit("reused-name")
        commit("wip")
        git("checkout", "-q", "main")
        merged = cleanup.Merged(
            names=frozenset({"in-main", "squashed", "reused-name"}),
            shas=frozenset({git("rev-parse", "main"), squashed}),
            prs={"reused-name": "https://github.com/me/repo/pull/1"},
        )

        # Accept the list, then decline both the PR link and the force delete.
        answers = {"Delete these branches?": True}
        with patch.object(
            cleanup.Confirm, "ask", side_effect=lambda prompt, **_: answers.get(prompt)
        ):
            cleanup.prune_local_branches(merged, PROTECTED)

        self.assertEqual(
            [ref.name for ref in cleanup.refs(cleanup.LOCAL_REFS)],
            ["main", "reused-name", "wip"],
        )
        self.assertEqual(cleanup.worktrees_by_branch(), {})

    def test_remote_branch_needs_my_authorship_and_a_proven_merge(self) -> None:
        mine = commit("mine")
        commit("mine-unproven")
        theirs = commit("theirs", "--author=them <them@example.com>")
        git("push", "-q", "origin", "main", "mine", "mine-unproven", "theirs")
        merged = cleanup.Merged(
            names=frozenset({"mine", "mine-unproven", "theirs"}),
            shas=frozenset({mine, theirs}),
            prs={},
        )

        with patch.object(cleanup.Confirm, "ask", return_value=True):
            cleanup.prune_remote_branches(merged, PROTECTED)

        self.assertEqual(
            git("--git-dir=../origin.git", "branch", "--format=%(refname:short)"),
            "main\nmine-unproven\ntheirs",
        )


if __name__ == "__main__":
    unittest.main()
