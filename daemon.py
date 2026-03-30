import sys
import time
from dotenv import load_dotenv
from loguru import logger
import schedule

from core.fetcher import fetch_from_rss, fetch_from_url
from core.history import HistoryManager
from vibe_publish import load_config, run_pipeline

def autonomous_loop():
    logger.info("Starting autonomous RSS extraction cycle...")
    config = load_config("config.yaml")
    
    # Setup History Tracker
    daemon_cfg = config.get("daemon", {})
    history_file = daemon_cfg.get("history_file", "history.json")
    history = HistoryManager(filepath=history_file)
    
    # Get configured feeds
    feeds = config.get("rss_feeds", [])
    if not feeds:
        logger.warning("No RSS feeds configured. Sleeping until next cycle.")
        return
        
    success_count = 0
    fail_count = 0
    skip_count = 0
    
    for feed_url in feeds:
        logger.info(f"Checking feed: {feed_url}")
        try:
            # We fetch up to 5 items per run per feed to avoid swamping local LLM
            articles_summary = fetch_from_rss(feed_url, limit=5)
            
            for article in articles_summary:
                if not article.source_url:
                    continue
                    
                if history.is_processed(article.source_url):
                    logger.debug(f"Already processed, skipping: {article.title}")
                    skip_count += 1
                    continue
                
                logger.info(f"\n🚀 New article found: {article.title}\n   URL: {article.source_url}")
                try:
                    # fetch_from_rss currently extracts summaries.
                    # We need the full text for the translation pipeline.
                    full_article = fetch_from_url(article.source_url)
                    
                    is_success = run_pipeline(full_article, config, dry_run=False)
                    if is_success:
                        history.mark_processed(article.source_url)
                        # We also mark the title in history under a different schema if needed,
                        # but URL is best source of truth.
                        success_count += 1
                    else:
                        fail_count += 1
                except Exception as e:
                    logger.error(f"Failed to pipeline '{article.title}': {e}")
                    fail_count += 1

        except Exception as e:
            logger.error(f"Failed to fetch feed {feed_url}: {e}")

    logger.info(
        f"\n{'━'*50}\n"
        f"Cycle Complete — Analyzed Feeds\n"
        f"  Successfully Processed & Pushed: {success_count}\n"
        f"  Failed: {fail_count}\n"
        f"  Skipped (Already in History): {skip_count}\n"
        f"{'━'*50}"
    )


def start_daemon():
    load_dotenv()
    
    config = load_config("config.yaml")
    daemon_cfg = config.get("daemon", {})
    interval_hours = daemon_cfg.get("schedule_hours", 6)
    
    logger.info(f"Starting Article Bot Daemon. Scheduled every {interval_hours} hours. Press Ctrl+C to stop.")
    
    # Initial run
    autonomous_loop()
    
    # Schedule future runs
    schedule.every(interval_hours).hours.do(autonomous_loop)
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check schedule every minute
        except KeyboardInterrupt:
            logger.info("Daemon gracefully stopped by user.")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Unexpected error in daemon sleep loop: {e}")
            time.sleep(60)

if __name__ == "__main__":
    start_daemon()
