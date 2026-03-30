#!/usr/bin/env python3
"""
vibe_publish — Article Bot CLI
================================
End-to-end pipeline: fetch → translate → format → publish.

Usage:
    python vibe_publish.py --url https://example.com/article
    python vibe_publish.py --file article.md
    python vibe_publish.py --text "Raw article text..."
    python vibe_publish.py --rss https://example.com/feed.xml
    python vibe_publish.py --url https://example.com/article --dry-run
"""

import argparse
import sys
from pathlib import Path

import yaml
from dotenv import load_dotenv
from loguru import logger

from core.fetcher import (
    Article,
    fetch_from_text,
    fetch_from_file,
    fetch_from_url,
    fetch_from_rss,
)
from core.translator import Translator
from core.formatter import format_article, write_to_hugo, slugify
from core.publisher import GitHubPublisher
from core.llm_providers import get_provider


# ── Configure logging ────────────────────────────────────────
logger.remove()
logger.add(
    sys.stderr,
    format=(
        "<green>{time:HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{function}</cyan> — {message}"
    ),
    level="INFO",
    colorize=True,
)
logger.add(
    "article_bot.log",
    rotation="5 MB",
    retention="7 days",
    level="DEBUG",
)


def load_config(config_path: str = "config.yaml") -> dict:
    """Load and return the YAML configuration."""
    path = Path(config_path)
    if not path.exists():
        logger.error(f"Config file not found: {config_path}")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    logger.info(f"Loaded config from {config_path}")
    return config


def run_pipeline(article: Article, config: dict, dry_run: bool = False) -> None:
    """
    Execute the full translation → format → publish pipeline
    for a single article.
    """
    # ── Step 1: Initialize LLM provider ──────────────────────
    provider = get_provider(config)

    # ── Step 2: Initialize translator ────────────────────────
    trans_cfg = config.get("translation", {})
    translator = Translator(
        provider=provider,
        source_lang=trans_cfg.get("source_language", "Turkish"),
        target_lang=trans_cfg.get("target_language", "English"),
        target_level=trans_cfg.get("target_level", "C1 (professional technical)"),
        prompt_template_path=trans_cfg.get(
            "prompt_template", "prompts/code_aware_translate.txt"
        ),
    )

    # ── Step 3: Translate ────────────────────────────────────
    logger.info(f"Translating: {article.title}")
    translated_body = translator.translate(article.body)

    # ── Step 4: Generate tags ────────────────────────────────
    tags_cfg = config.get("tags", {})
    tags = []
    if tags_cfg.get("enabled", True):
        tags = translator.generate_tags(
            translated_body,
            max_tags=tags_cfg.get("max_tags", 8),
        )

    # ── Step 5: Format for Hugo ──────────────────────────────
    filename, full_content = format_article(
        title=article.title,
        translated_body=translated_body,
        tags=tags,
        original_url=article.source_url,
    )

    slug = slugify(article.title)

    # ── Step 6: Write to Hugo site locally ───────────────────
    hugo_cfg = config.get("hugo", {})
    filepath = write_to_hugo(
        filename=filename,
        content=full_content,
        hugo_site_dir=hugo_cfg.get("site_dir", "hugo_site"),
        content_subdir=hugo_cfg.get("content_dir", "content/posts"),
    )

    logger.success(f"Local file written: {filepath}")

    if dry_run:
        logger.info("── DRY RUN — Skipping GitHub push ──")
        logger.info(f"Article: {article.title}")
        logger.info(f"Slug: {slug}")
        logger.info(f"Tags: {tags}")
        logger.info(f"File: {filepath}")
        logger.info(f"Content length: {len(full_content)} chars")
        return

    # ── Step 7: Push to GitHub ───────────────────────────────
    gh_cfg = config.get("github", {})
    repo = gh_cfg.get("repository", "")

    if not repo:
        logger.warning(
            "No GitHub repository configured in config.yaml — "
            "skipping publish step. Set github.repository to enable."
        )
        return

    publisher = GitHubPublisher(
        repository=repo,
        default_branch=gh_cfg.get("default_branch", "main"),
        push_strategy=gh_cfg.get("push_strategy", "direct"),
        commit_message_template=gh_cfg.get(
            "commit_message", "feat: add translated article [{slug}]"
        ),
    )

    # File path within the repo
    content_dir = hugo_cfg.get("content_dir", "content/posts")
    repo_file_path = f"{hugo_cfg.get('site_dir', 'hugo_site')}/{content_dir}/{filename}"

    result = publisher.publish(
        file_path=repo_file_path,
        content=full_content,
        slug=slug,
    )

    logger.success(
        f"Published to GitHub!\n"
        f"  Strategy: {result['strategy']}\n"
        f"  Branch:   {result['branch']}\n"
        f"  URL:      {result.get('url', 'N/A')}"
    )


def main():
    parser = argparse.ArgumentParser(
        prog="vibe_publish",
        description="Article Bot — Fetch, translate, and publish technical articles",
    )

    # Input sources (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--url",
        help="Fetch article from a URL",
    )
    input_group.add_argument(
        "--file",
        help="Read article from a local file",
    )
    input_group.add_argument(
        "--text",
        help="Provide article text directly",
    )
    input_group.add_argument(
        "--rss",
        help="Fetch articles from an RSS feed URL",
    )

    # Options
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to config file (default: config.yaml)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run pipeline without pushing to GitHub",
    )
    parser.add_argument(
        "--rss-limit",
        type=int,
        default=5,
        help="Max articles to process from RSS (default: 5)",
    )

    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    # Load configuration
    config = load_config(args.config)

    # ── Fetch articles ───────────────────────────────────────
    try:
        if args.url:
            articles = [fetch_from_url(args.url)]
        elif args.file:
            articles = [fetch_from_file(args.file)]
        elif args.text:
            articles = [fetch_from_text(args.text)]
        elif args.rss:
            rss_articles = fetch_from_rss(args.rss, limit=args.rss_limit)
            # For RSS, fetch full content from each article's URL
            articles = []
            for rss_entry in rss_articles:
                if rss_entry.source_url:
                    try:
                        full_article = fetch_from_url(rss_entry.source_url)
                        articles.append(full_article)
                    except Exception as e:
                        logger.error(
                            f"Failed to fetch {rss_entry.source_url}: {e}"
                        )
                else:
                    articles.append(rss_entry)
        else:
            parser.print_help()
            sys.exit(1)

    except Exception as e:
        logger.error(f"Failed to fetch article(s): {e}")
        sys.exit(1)

    # ── Process each article ─────────────────────────────────
    success_count = 0
    fail_count = 0

    for i, article in enumerate(articles, 1):
        logger.info(
            f"\n{'═' * 60}\n"
            f"  Processing article {i}/{len(articles)}: {article.title}\n"
            f"{'═' * 60}"
        )
        try:
            run_pipeline(article, config, dry_run=args.dry_run)
            success_count += 1
        except Exception as e:
            logger.error(f"Pipeline failed for '{article.title}': {e}")
            fail_count += 1

    # ── Summary ──────────────────────────────────────────────
    logger.info(
        f"\n{'═' * 60}\n"
        f"  Pipeline complete: {success_count} succeeded, {fail_count} failed\n"
        f"{'═' * 60}"
    )

    sys.exit(1 if fail_count > 0 else 0)


if __name__ == "__main__":
    main()
