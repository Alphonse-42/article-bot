import json
import threading
from pathlib import Path
from loguru import logger

class HistoryManager:
    """
    Manages state for the article daemon to ensure articles aren't processed twice.
    Backed by a simple JSON file. Thread-safe for any future concurrent usage.
    """
    def __init__(self, filepath: str = "history.json"):
        self.filepath = Path(filepath)
        self.lock = threading.Lock()
        self._history = set()
        self._load()

    def _load(self):
        if self.filepath.exists():
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Support old string arrays or new objects if schema changes,
                    # but for now we expect a simple JSON array of strings
                    self._history = set(data)
                logger.info(f"Loaded {len(self._history)} processed items from {self.filepath}")
            except Exception as e:
                logger.error(f"Failed to load history file {self.filepath}: {e}")
                self._history = set()

    def _save(self):
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(list(self._history), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save history file {self.filepath}: {e}")

    def is_processed(self, url: str) -> bool:
        """Check if an article URL has already been processed."""
        if not url:
            return False
        with self.lock:
            return url in self._history

    def mark_processed(self, url: str):
        """Mark an article URL as processed and save to disk."""
        if not url:
            return
        with self.lock:
            if url not in self._history:
                self._history.add(url)
                self._save()
                logger.debug(f"Marked as processed: {url}")
