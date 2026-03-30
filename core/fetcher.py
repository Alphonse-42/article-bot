"""
Article Fetcher
================
Fetch articles from multiple sources:
  - Direct text/markdown input
  - URL (HTML → Markdown extraction)
  - RSS feed
"""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from loguru import logger

try:
    import feedparser
except ImportError:
    feedparser = None


@dataclass
class Article:
    """Represents a fetched article ready for translation."""
    title: str
    body: str
    source_url: Optional[str] = None
    fetched_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    content_hash: str = ""

    def __post_init__(self):
        if not self.content_hash:
            self.content_hash = hashlib.sha256(
                self.body.encode("utf-8")
            ).hexdigest()[:12]


# ─────────────────────────────────────────────────────────────
# Fetchers
# ─────────────────────────────────────────────────────────────

def fetch_from_text(text: str, title: str = "Untitled Article") -> Article:
    """
    Create an Article from raw text/markdown content.
    Used for direct input and testing.
    """
    logger.info(f"Fetching from direct text input ({len(text)} chars)")

    # Try to extract title from first markdown heading
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("# ") and not stripped.startswith("## "):
            title = stripped.lstrip("# ").strip()
            break

    return Article(title=title, body=text.strip())


def fetch_from_file(filepath: str) -> Article:
    """Read an article from a local markdown/text file."""
    logger.info(f"Fetching from file: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    return fetch_from_text(content)


def fetch_from_url(url: str) -> Article:
    """
    Fetch an article from a URL.
    Extracts the main content as Markdown using BeautifulSoup + markdownify.
    """
    logger.info(f"Fetching from URL: {url}")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding or "utf-8"

    soup = BeautifulSoup(resp.text, "html.parser")

    # Extract title
    title = "Untitled"
    if soup.title and soup.title.string:
        title = soup.title.string.strip()

    # Try to find main content area
    content_el = (
        soup.find("article")
        or soup.find("main")
        or soup.find("div", class_="post-content")
        or soup.find("div", class_="entry-content")
        or soup.find("div", class_="content")
        or soup.find("div", class_="markdown-body")
        or soup.body
    )

    if content_el is None:
        raise ValueError(f"Could not extract content from {url}")

    # Remove unwanted elements
    for tag in content_el.find_all(["nav", "footer", "header", "aside",
                                     "script", "style", "noscript"]):
        tag.decompose()

    # Convert to Markdown
    body = md(
        str(content_el),
        heading_style="ATX",
        code_language_callback=lambda el: el.get("class", [""])[0].replace("language-", "")
        if el.get("class") else "",
    )

    # Clean up excessive whitespace
    lines = body.split("\n")
    cleaned = []
    blank_count = 0
    for line in lines:
        if line.strip() == "":
            blank_count += 1
            if blank_count <= 2:
                cleaned.append("")
        else:
            blank_count = 0
            cleaned.append(line)
    body = "\n".join(cleaned).strip()

    logger.success(f"Extracted '{title}' ({len(body)} chars)")
    return Article(title=title, body=body, source_url=url)


def fetch_from_rss(feed_url: str, limit: int = 10) -> list[Article]:
    """
    Fetch articles from an RSS/Atom feed.
    Returns a list of Article objects (bodies contain summaries;
    use fetch_from_url on each entry's link for full content).
    """
    if feedparser is None:
        raise ImportError("pip install feedparser")

    logger.info(f"Fetching RSS feed: {feed_url}")
    feed = feedparser.parse(feed_url)

    if feed.bozo and not feed.entries:
        raise ValueError(f"Failed to parse feed: {feed.bozo_exception}")

    articles = []
    for entry in feed.entries[:limit]:
        title = entry.get("title", "Untitled")
        link = entry.get("link", "")
        summary = entry.get("summary", entry.get("description", ""))

        # Convert HTML summary to Markdown
        if "<" in summary:
            summary = md(summary, heading_style="ATX")

        articles.append(Article(
            title=title,
            body=summary.strip(),
            source_url=link,
        ))

    logger.success(f"Found {len(articles)} articles in feed")
    return articles
