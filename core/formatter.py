"""
Hugo Markdown Formatter
========================
Wraps translated articles in Hugo-compatible frontmatter (YAML)
and writes them to the content/posts/ directory.
"""

import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from loguru import logger


def slugify(text: str) -> str:
    """
    Convert a title string to a URL-safe slug.
    Example: "Deploying Docker on AWS" → "deploying-docker-on-aws"
    """
    # Normalize unicode
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    # Lowercase and replace non-alphanumeric chars with hyphens
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[-\s]+", "-", text).strip("-")
    # Limit length
    return text[:80].rstrip("-")


def generate_frontmatter(
    title: str,
    slug: str,
    tags: list[str],
    categories: Optional[list[str]] = None,
    original_url: Optional[str] = None,
    date: Optional[str] = None,
) -> str:
    """
    Generate Hugo YAML frontmatter.
    """
    if date is None:
        date = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")

    if categories is None:
        categories = ["translated-articles"]

    lines = [
        "---",
        f'title: "{_escape_yaml_string(title)}"',
        f"date: {date}",
        f'slug: "{slug}"',
        f"draft: false",
    ]

    # Tags
    if tags:
        lines.append("tags:")
        for tag in tags:
            lines.append(f'  - "{tag}"')

    # Categories
    lines.append("categories:")
    for cat in categories:
        lines.append(f'  - "{cat}"')

    # Original URL
    if original_url:
        lines.append(f'original_url: "{original_url}"')

    lines.append("---")
    return "\n".join(lines)


def _escape_yaml_string(s: str) -> str:
    """Escape quotes in a YAML string value."""
    return s.replace('"', '\\"')


def format_article(
    title: str,
    translated_body: str,
    tags: list[str],
    original_url: Optional[str] = None,
    date: Optional[str] = None,
) -> tuple[str, str]:
    """
    Format a translated article into a complete Hugo Markdown file.

    Returns:
        (filename, full_content) — the filename and the complete Markdown
        including frontmatter.
    """
    slug = slugify(title)
    date_str = date or datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%S+00:00"
    )
    date_prefix = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    filename = f"{date_prefix}-{slug}.md"

    frontmatter = generate_frontmatter(
        title=title,
        slug=slug,
        tags=tags,
        original_url=original_url,
        date=date_str,
    )

    full_content = f"{frontmatter}\n\n{translated_body.strip()}\n"

    logger.info(f"Formatted article: {filename} ({len(full_content)} chars)")
    return filename, full_content


def write_to_hugo(
    filename: str,
    content: str,
    hugo_site_dir: str = "hugo_site",
    content_subdir: str = "content/posts",
) -> Path:
    """
    Write a formatted Markdown article to the Hugo content directory.

    Returns the absolute path to the written file.
    """
    posts_dir = Path(hugo_site_dir) / content_subdir
    posts_dir.mkdir(parents=True, exist_ok=True)

    filepath = posts_dir / filename
    filepath.write_text(content, encoding="utf-8")

    logger.success(f"Article written to: {filepath}")
    return filepath
