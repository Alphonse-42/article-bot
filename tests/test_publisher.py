"""
Tests for core.publisher — GitHub Publisher
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock

from core.publisher import GitHubPublisher


# ── Fixtures ─────────────────────────────────────────────────

@pytest.fixture
def mock_github(monkeypatch):
    """Patch Github class to avoid real API calls."""
    mock_repo = MagicMock()
    mock_repo.full_name = "user/article-bot"

    mock_gh = MagicMock()
    mock_gh.get_repo.return_value = mock_repo

    with patch("core.publisher.Github", return_value=mock_gh):
        monkeypatch.setenv("GITHUB_TOKEN", "fake-token-123")
        yield mock_repo


@pytest.fixture
def publisher(mock_github):
    """Create a GitHubPublisher with mocked GitHub."""
    return GitHubPublisher(
        repository="user/article-bot",
        default_branch="main",
        push_strategy="direct",
        commit_message_template="feat: add [{slug}]",
    )


# ── Initialization Tests ────────────────────────────────────

class TestPublisherInit:
    def test_init_with_env_token(self, mock_github):
        pub = GitHubPublisher(
            repository="user/article-bot",
        )
        assert pub.repo_name == "user/article-bot"
        assert pub.default_branch == "main"
        assert pub.push_strategy == "direct"

    def test_init_with_explicit_token(self, monkeypatch):
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        with patch("core.publisher.Github") as mock_gh:
            mock_gh.return_value.get_repo.return_value = MagicMock()
            pub = GitHubPublisher(
                repository="user/repo",
                token="explicit-token",
            )
            mock_gh.assert_called_once_with("explicit-token")

    def test_init_no_token_raises(self, monkeypatch):
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        with patch("core.publisher.Github"):
            with pytest.raises(ValueError, match="GitHub token"):
                GitHubPublisher(repository="user/repo")


# ── Direct Push Tests ───────────────────────────────────────

class TestDirectPush:
    def test_create_new_file(self, publisher, mock_github):
        """When file doesn't exist, create_file should be called."""
        from github import GithubException

        mock_github.get_contents.side_effect = GithubException(
            404, {"message": "Not Found"}, None
        )
        mock_github.create_file.return_value = {
            "commit": MagicMock(sha="abc123"),
            "content": MagicMock(html_url="https://github.com/..."),
        }

        result = publisher.publish(
            file_path="content/posts/test.md",
            content="# Test Article",
            slug="test",
        )

        mock_github.create_file.assert_called_once()
        assert result["strategy"] == "direct"
        assert result["commit_sha"] == "abc123"

    def test_update_existing_file(self, publisher, mock_github):
        """When file exists, update_file should be called."""
        existing = MagicMock(sha="old-sha")
        mock_github.get_contents.return_value = existing
        mock_github.update_file.return_value = {
            "commit": MagicMock(sha="new-sha"),
            "content": MagicMock(html_url="https://github.com/..."),
        }

        result = publisher.publish(
            file_path="content/posts/test.md",
            content="# Updated",
            slug="test",
        )

        mock_github.update_file.assert_called_once()
        assert result["commit_sha"] == "new-sha"

    def test_commit_message_template(self, publisher, mock_github):
        from github import GithubException

        mock_github.get_contents.side_effect = GithubException(
            404, {"message": "Not Found"}, None
        )
        mock_github.create_file.return_value = {
            "commit": MagicMock(sha="sha"),
            "content": MagicMock(html_url="url"),
        }

        publisher.publish(
            file_path="test.md",
            content="body",
            slug="my-article",
        )

        call_kwargs = mock_github.create_file.call_args
        assert "my-article" in call_kwargs.kwargs.get(
            "message", call_kwargs[1].get("message", "")
        )


# ── PR Push Tests ────────────────────────────────────────────

class TestPRPush:
    def test_pr_creates_branch_and_pr(self, mock_github, monkeypatch):
        monkeypatch.setenv("GITHUB_TOKEN", "fake-token")

        with patch("core.publisher.Github") as mock_gh_cls:
            mock_gh_cls.return_value.get_repo.return_value = mock_github

            pub = GitHubPublisher(
                repository="user/repo",
                push_strategy="pr",
            )

        # Set up mocks for PR flow
        base_ref = MagicMock()
        base_ref.object.sha = "base-sha"
        mock_github.get_git_ref.return_value = base_ref

        from github import GithubException
        mock_github.get_contents.side_effect = GithubException(
            404, {"message": "Not Found"}, None
        )
        mock_github.create_file.return_value = {
            "commit": MagicMock(sha="pr-sha"),
            "content": MagicMock(html_url="url"),
        }

        pr_mock = MagicMock()
        pr_mock.number = 42
        pr_mock.html_url = "https://github.com/user/repo/pull/42"
        mock_github.create_pull.return_value = pr_mock

        result = pub.publish(
            file_path="content/posts/test.md",
            content="# Test",
            slug="test-article",
        )

        assert result["strategy"] == "pr"
        assert result["pr_number"] == 42
        mock_github.create_git_ref.assert_called_once()
        mock_github.create_pull.assert_called_once()


# ── Utility Tests ────────────────────────────────────────────

class TestFileExists:
    def test_file_exists_true(self, publisher, mock_github):
        mock_github.get_contents.return_value = MagicMock()
        assert publisher.file_exists("path/to/file.md") is True

    def test_file_exists_false(self, publisher, mock_github):
        from github import GithubException
        mock_github.get_contents.side_effect = GithubException(
            404, {"message": "Not Found"}, None
        )
        assert publisher.file_exists("nonexistent.md") is False
