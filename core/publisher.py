"""
GitHub Publisher
=================
Push translated articles to a GitHub repository using PyGitHub.

Supports two strategies:
  - "direct": Push directly to the default branch
  - "pr": Create a branch, push, open a PR, and optionally merge
"""

import os
import base64
from typing import Optional

from github import Github, GithubException
from loguru import logger


class GitHubPublisher:
    """
    Manages pushing content to a GitHub repository.
    """

    def __init__(
        self,
        repository: str,
        default_branch: str = "main",
        push_strategy: str = "direct",
        commit_message_template: str = "feat: add translated article [{slug}]",
        token: Optional[str] = None,
    ):
        """
        Args:
            repository: "owner/repo" format
            default_branch: Branch to push to (or base for PR)
            push_strategy: "direct" or "pr"
            commit_message_template: Commit message with {slug} placeholder
            token: GitHub PAT (falls back to GITHUB_TOKEN env var)
        """
        self.repo_name = repository
        self.default_branch = default_branch
        self.push_strategy = push_strategy
        self.commit_template = commit_message_template

        token = token or os.getenv("GITHUB_TOKEN")
        if not token:
            raise ValueError(
                "GitHub token not provided. Set GITHUB_TOKEN env var "
                "or pass token= argument."
            )

        self.github = Github(token)
        self.repo = self.github.get_repo(self.repo_name)
        logger.info(f"Connected to GitHub repo: {self.repo_name}")

    def publish(
        self,
        file_path: str,
        content: str,
        slug: str,
    ) -> dict:
        """
        Push a file to the GitHub repository.

        Args:
            file_path: Path within the repo (e.g., "hugo_site/content/posts/article.md")
            content: File content (UTF-8 string)
            slug: Article slug (used in commit message and branch name)

        Returns:
            dict with keys: strategy, branch, commit_sha, url
        """
        commit_message = self.commit_template.format(slug=slug)

        if self.push_strategy == "pr":
            return self._publish_via_pr(file_path, content, slug, commit_message)
        else:
            return self._publish_direct(file_path, content, commit_message)

    # ── Direct push ──────────────────────────────────────────

    def _publish_direct(
        self,
        file_path: str,
        content: str,
        commit_message: str,
    ) -> dict:
        """Push a file directly to the default branch."""
        logger.info(
            f"Direct push to {self.default_branch}: {file_path}"
        )

        # Check if file already exists
        try:
            existing = self.repo.get_contents(
                file_path, ref=self.default_branch
            )
            # Update existing file
            result = self.repo.update_file(
                path=file_path,
                message=commit_message,
                content=content,
                sha=existing.sha,
                branch=self.default_branch,
            )
            logger.success(f"Updated existing file: {file_path}")
        except GithubException as e:
            if e.status == 404:
                # Create new file
                result = self.repo.create_file(
                    path=file_path,
                    message=commit_message,
                    content=content,
                    branch=self.default_branch,
                )
                logger.success(f"Created new file: {file_path}")
            else:
                raise

        commit_sha = result["commit"].sha
        html_url = result["content"].html_url

        return {
            "strategy": "direct",
            "branch": self.default_branch,
            "commit_sha": commit_sha,
            "url": html_url,
        }

    # ── PR-based push ────────────────────────────────────────

    def _publish_via_pr(
        self,
        file_path: str,
        content: str,
        slug: str,
        commit_message: str,
    ) -> dict:
        """Create a branch, push the file, and open a PR."""
        branch_name = f"article/{slug}"
        logger.info(f"PR strategy: creating branch {branch_name}")

        # Get the SHA of the default branch HEAD
        base_ref = self.repo.get_git_ref(
            f"heads/{self.default_branch}"
        )
        base_sha = base_ref.object.sha

        # Create the new branch
        try:
            self.repo.create_git_ref(
                ref=f"refs/heads/{branch_name}",
                sha=base_sha,
            )
            logger.debug(f"Created branch: {branch_name}")
        except GithubException as e:
            if e.status == 422:
                # Branch already exists — that's OK
                logger.debug(f"Branch {branch_name} already exists")
            else:
                raise

        # Create the file on the new branch
        try:
            existing = self.repo.get_contents(file_path, ref=branch_name)
            self.repo.update_file(
                path=file_path,
                message=commit_message,
                content=content,
                sha=existing.sha,
                branch=branch_name,
            )
        except GithubException as e:
            if e.status == 404:
                self.repo.create_file(
                    path=file_path,
                    message=commit_message,
                    content=content,
                    branch=branch_name,
                )
            else:
                raise

        # Create pull request
        pr = self.repo.create_pull(
            title=commit_message,
            body=f"Automated translation: `{slug}`\n\nGenerated by article-bot.",
            head=branch_name,
            base=self.default_branch,
        )
        logger.success(f"Created PR #{pr.number}: {pr.html_url}")

        return {
            "strategy": "pr",
            "branch": branch_name,
            "pr_number": pr.number,
            "pr_url": pr.html_url,
            "commit_sha": base_sha,
            "url": pr.html_url,
        }

    # ── Utilities ────────────────────────────────────────────

    def file_exists(self, file_path: str) -> bool:
        """Check if a file already exists in the repo."""
        try:
            self.repo.get_contents(file_path, ref=self.default_branch)
            return True
        except GithubException:
            return False
