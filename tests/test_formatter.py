"""
Tests for core.formatter — Hugo Markdown Formatter
"""

import pytest
from datetime import datetime, timezone

from core.formatter import (
    slugify,
    generate_frontmatter,
    format_article,
    write_to_hugo,
    _escape_yaml_string,
)


# ── Slugify Tests ────────────────────────────────────────────

class TestSlugify:
    def test_basic_slug(self):
        assert slugify("Hello World") == "hello-world"

    def test_special_characters(self):
        assert slugify("Deploying Docker on AWS!") == "deploying-docker-on-aws"

    def test_unicode_characters(self):
        """Turkish characters should be normalized to ASCII equivalents."""
        slug = slugify("Türkçe Başlık Örneği")
        # Turkish ı (dotless i) has no ASCII mapping and gets stripped
        assert slug == "turkce-baslk-ornegi"

    def test_multiple_spaces_and_dashes(self):
        assert slugify("Hello   ---   World") == "hello-world"

    def test_max_length(self):
        long_title = "a" * 200
        assert len(slugify(long_title)) <= 80

    def test_empty_string(self):
        assert slugify("") == ""

    def test_only_special_chars(self):
        assert slugify("!@#$%") == ""

    def test_trailing_dashes(self):
        assert not slugify("test-article-").endswith("-")


# ── YAML Escaping ────────────────────────────────────────────

class TestEscapeYaml:
    def test_escape_quotes(self):
        assert _escape_yaml_string('Title with "quotes"') == 'Title with \\"quotes\\"'

    def test_no_escape_needed(self):
        assert _escape_yaml_string("Simple Title") == "Simple Title"


# ── Frontmatter Generation ──────────────────────────────────

class TestGenerateFrontmatter:
    def test_basic_frontmatter(self):
        fm = generate_frontmatter(
            title="Test Article",
            slug="test-article",
            tags=["python", "docker"],
            date="2026-01-15T12:00:00+00:00",
        )
        assert fm.startswith("---")
        assert fm.endswith("---")
        assert 'title: "Test Article"' in fm
        assert 'slug: "test-article"' in fm
        assert "draft: false" in fm
        assert '- "python"' in fm
        assert '- "docker"' in fm

    def test_frontmatter_with_original_url(self):
        fm = generate_frontmatter(
            title="Test",
            slug="test",
            tags=[],
            original_url="https://example.com/article",
        )
        assert 'original_url: "https://example.com/article"' in fm

    def test_frontmatter_default_categories(self):
        fm = generate_frontmatter(title="Test", slug="test", tags=[])
        assert '- "translated-articles"' in fm

    def test_frontmatter_custom_categories(self):
        fm = generate_frontmatter(
            title="Test", slug="test", tags=[],
            categories=["security", "devops"],
        )
        assert '- "security"' in fm
        assert '- "devops"' in fm

    def test_frontmatter_auto_date(self):
        """If no date provided, should use current UTC time."""
        fm = generate_frontmatter(title="Test", slug="test", tags=[])
        assert "date:" in fm
        # Should contain a valid ISO-like date
        assert "T" in fm.split("date:")[1].split("\n")[0]


# ── Full Article Formatting ─────────────────────────────────

class TestFormatArticle:
    def test_format_returns_filename_and_content(self):
        filename, content = format_article(
            title="My Test Article",
            translated_body="This is the article body.",
            tags=["python"],
        )
        assert filename.endswith(".md")
        assert "my-test-article" in filename
        assert content.startswith("---")
        assert "This is the article body." in content

    def test_filename_format(self):
        filename, _ = format_article(
            title="Docker Guide",
            translated_body="Body text",
            tags=[],
        )
        # Should match YYYY-MM-DD-slug.md
        parts = filename.split("-", 3)
        assert len(parts) >= 4  # year, month, day, rest
        assert parts[0].isdigit() and len(parts[0]) == 4  # year
        assert filename.endswith(".md")

    def test_format_with_original_url(self):
        _, content = format_article(
            title="Test",
            translated_body="Body",
            tags=[],
            original_url="https://example.com",
        )
        assert "original_url" in content


# ── Write to Hugo ────────────────────────────────────────────

class TestWriteToHugo:
    def test_write_creates_file(self, tmp_path):
        filepath = write_to_hugo(
            filename="2026-01-15-test.md",
            content="---\ntitle: Test\n---\n\nBody",
            hugo_site_dir=str(tmp_path),
            content_subdir="content/posts",
        )
        assert filepath.exists()
        assert filepath.read_text(encoding="utf-8") == "---\ntitle: Test\n---\n\nBody"

    def test_write_creates_directories(self, tmp_path):
        target = tmp_path / "new_site"
        filepath = write_to_hugo(
            filename="test.md",
            content="content",
            hugo_site_dir=str(target),
            content_subdir="content/posts",
        )
        assert (target / "content" / "posts").is_dir()
        assert filepath.exists()

    def test_write_overwrites_existing(self, tmp_path):
        filepath = write_to_hugo(
            filename="existing.md",
            content="version 1",
            hugo_site_dir=str(tmp_path),
            content_subdir="content/posts",
        )
        filepath2 = write_to_hugo(
            filename="existing.md",
            content="version 2",
            hugo_site_dir=str(tmp_path),
            content_subdir="content/posts",
        )
        assert filepath2.read_text(encoding="utf-8") == "version 2"
