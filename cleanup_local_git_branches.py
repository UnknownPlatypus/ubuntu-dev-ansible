#!/usr/bin/env python3
"""Cleanup local git branches that have been merged via GitHub PRs."""

import argparse
import concurrent.futures
import json
import logging
import subprocess

logger = logging.getLogger(__name__)


def run_cmd(command_args: list[str]) -> str:
    result = subprocess.run(command_args, capture_output=True, text=True, check=False)
    return result.stdout


def get_local_branches() -> set[str]:
    return {
        branch.removeprefix("*").strip()
        for branch in run_cmd(["git", "branch"]).splitlines()
    }


def _check_branch_merged(branch: str) -> str | None:
    """Return the branch name if it has a merged PR, else None."""
    logger.debug(f"Checking PR status for branch: {branch}")
    result = run_cmd(
        [
            "gh",
            "pr",
            "list",
            "--head",
            branch,
            "--state",
            "merged",
            "--json",
            "number",
            "--limit",
            "1",
        ]
    )
    prs = json.loads(result) if result.strip() else []
    if prs:
        logger.debug(f"  -> merged (PR #{prs[0]['number']})")
        return branch
    logger.debug(f"  -> not merged")
    return None


def get_merged_branches(local_branches: set[str]) -> set[str]:
    """Check which local branches have merged PRs using gh CLI."""
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(_check_branch_merged, local_branches)
    return {branch for branch in results if branch is not None}


def cleanup_local_git_branches(
    protected_branches: set[str] | None = None,
    dry_run: bool = False,
) -> None:
    if protected_branches is None:
        protected_branches = {"master", "main"}

    local_branches = get_local_branches() - protected_branches
    logger.debug(f"Local branches (excluding protected): {sorted(local_branches)}")

    branches_to_delete = get_merged_branches(local_branches)

    if not branches_to_delete:
        logger.info("No branches to cleanup!")
        return

    logger.info("Merged branches:")
    for branch in sorted(branches_to_delete):
        logger.info(f"  - {branch}")

    if dry_run:
        logger.info("\nDry run, no branches deleted.")
        return

    if input("\nDelete these branches? (y/n) ").strip().lower() == "y":
        subprocess.run(["git", "branch", "-D", *branches_to_delete])
        logger.info("Done!")
    else:
        logger.info("Aborted.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--protected",
        nargs="*",
        default=["master", "main"],
        help="Branches to never delete (default: master main)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show branches without deleting"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable debug logging"
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="[%(levelname)s] %(message)s",
    )

    cleanup_local_git_branches(
        protected_branches=set(args.protected),
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
