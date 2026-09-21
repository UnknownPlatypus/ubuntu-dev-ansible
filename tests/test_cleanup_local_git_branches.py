from __future__ import annotations

import importlib.util
import pathlib
import sys
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


class MergedPrsTests(unittest.TestCase):
    def test_fetches_merged_prs_once_per_repo(self) -> None:
        repos = [
            cleanup.Repo("me/fork", "main"),
            cleanup.Repo("upstream/project", "main"),
        ]
        outputs = iter(
            [
                '[{"number": 1, "headRefName": "from-fork"}]',
                '[{"number": 2, "headRefName": "from-upstream"}]',
            ]
        )

        with patch.object(cleanup, "run_cmd", side_effect=outputs) as run_cmd:
            self.assertEqual(
                cleanup.merged_prs(repos),
                {"from-fork": "me/fork#1", "from-upstream": "upstream/project#2"},
            )

        self.assertEqual(run_cmd.call_count, 2)
        self.assertTrue(
            all("--head" not in call.args[0] for call in run_cmd.call_args_list)
        )


class ClassificationTests(unittest.TestCase):
    def test_gone_upstream_requires_review_even_if_pr_was_merged(self) -> None:
        branch = cleanup.Branch("feature", "origin/feature", gone=True)
        with (
            patch.object(cleanup, "run_ok", return_value=False),
            patch.object(cleanup, "_is_rebased_into", return_value=False),
        ):
            verdict = cleanup.classify_branch(
                branch,
                "origin/main",
                {"feature": "me/project#42"},
                {"main"},
            )

        self.assertEqual(
            verdict,
            cleanup.Verdict(
                "merged PR me/project#42; upstream origin/feature deleted",
                force=True,
                review=True,
            ),
        )

    def test_rebased_branch_is_safe_without_a_github_pr_lookup(self) -> None:
        branch = cleanup.Branch("feature", "origin/feature", gone=False)
        with (
            patch.object(cleanup, "run_ok", return_value=False),
            patch.object(cleanup, "_is_rebased_into", return_value=True),
        ):
            verdict = cleanup.classify_branch(branch, "origin/main", {}, {"main"})

        self.assertEqual(
            verdict, cleanup.Verdict("rebased into origin/main", force=True)
        )


if __name__ == "__main__":
    unittest.main()
