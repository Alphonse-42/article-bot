"""
Code-Aware Translator
======================
Translates technical articles while preserving code blocks, inline code,
file paths, terminal commands, and all Markdown formatting.

Uses a two-pass strategy:
  1. Primary: Send full article with code-aware system prompt
  2. Fallback: Replace code blocks with placeholders, translate, re-inject
"""

import re
import os
from pathlib import Path
from typing import Optional

from loguru import logger

from core.llm_providers import BaseLLMProvider


# ── Regex patterns ───────────────────────────────────────────
# Matches fenced code blocks: ```lang\n...\n```
_FENCED_CODE_RE = re.compile(
    r"(```[\w\-]*\s*\n.*?\n```)", re.DOTALL
)

# Matches inline code: `...`
_INLINE_CODE_RE = re.compile(r"(`[^`\n]+?`)")


class Translator:
    """
    Translates technical articles using an LLM provider
    with code-aware preservation.
    """

    def __init__(
        self,
        provider: BaseLLMProvider,
        source_lang: str = "Turkish",
        target_lang: str = "English",
        target_level: str = "C1 (professional technical)",
        prompt_template_path: str = "prompts/code_aware_translate.txt",
    ):
        self.provider = provider
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.target_level = target_level
        self._load_prompt_template(prompt_template_path)

    def _load_prompt_template(self, path: str) -> None:
        """Load the system prompt template from disk."""
        resolved = Path(path)
        if not resolved.exists():
            # Try relative to project root
            project_root = Path(__file__).parent.parent
            resolved = project_root / path
        if not resolved.exists():
            raise FileNotFoundError(
                f"Prompt template not found: {path}"
            )

        self.prompt_template = resolved.read_text(encoding="utf-8")
        logger.debug(f"Loaded prompt template from {resolved}")

    def _build_system_prompt(self) -> str:
        """Fill in the prompt template with translation settings."""
        return self.prompt_template.format(
            source_language=self.source_lang,
            target_language=self.target_lang,
            target_level=self.target_level,
        )

    # ── Primary translation ──────────────────────────────────

    def translate(self, article_body: str) -> str:
        """
        Translate an article body with code-aware preservation.

        Strategy:
        1. Try direct translation with the code-aware prompt
        2. Verify code blocks are preserved
        3. If verification fails, fall back to placeholder strategy
        """
        logger.info(
            f"Translating article ({len(article_body)} chars) "
            f"[{self.source_lang} → {self.target_lang}]"
        )

        system_prompt = self._build_system_prompt()

        # Extract original code blocks for verification
        original_blocks = _FENCED_CODE_RE.findall(article_body)
        logger.debug(f"Found {len(original_blocks)} fenced code blocks")

        # Primary attempt: direct translation
        translated = self.provider.generate(system_prompt, article_body)

        # Verify code blocks were preserved
        translated_blocks = _FENCED_CODE_RE.findall(translated)

        if self._verify_code_blocks(original_blocks, translated_blocks):
            logger.success("Code blocks preserved — primary translation OK")
            return translated.strip()

        # Fallback: placeholder strategy
        logger.warning(
            "Code block mismatch detected — using placeholder fallback"
        )
        return self._translate_with_placeholders(
            article_body, system_prompt
        )

    # ── Fallback: placeholder strategy ───────────────────────

    def _translate_with_placeholders(
        self, article_body: str, system_prompt: str
    ) -> str:
        """
        Replace code blocks with placeholders, translate the prose,
        then re-inject the original code blocks.
        """
        # Extract and replace fenced code blocks
        code_blocks: list[str] = []
        placeholder_map: dict[str, str] = {}

        def _replace_fenced(match: re.Match) -> str:
            block = match.group(1)
            idx = len(code_blocks)
            placeholder = f"⟦CODE_BLOCK_{idx}⟧"
            code_blocks.append(block)
            placeholder_map[placeholder] = block
            return placeholder

        body_with_placeholders = _FENCED_CODE_RE.sub(
            _replace_fenced, article_body
        )

        # Also protect inline code
        inline_codes: list[str] = []

        def _replace_inline(match: re.Match) -> str:
            code = match.group(1)
            idx = len(inline_codes)
            placeholder = f"⟦INLINE_{idx}⟧"
            inline_codes.append(code)
            return placeholder

        body_with_placeholders = _INLINE_CODE_RE.sub(
            _replace_inline, body_with_placeholders
        )

        logger.debug(
            f"Replaced {len(code_blocks)} fenced + "
            f"{len(inline_codes)} inline code segments"
        )

        # Translate the placeholder version
        extra_instruction = (
            "\n\nIMPORTANT: The text contains placeholders like "
            "⟦CODE_BLOCK_0⟧ and ⟦INLINE_0⟧. "
            "Keep these placeholders EXACTLY as they are. "
            "Do NOT translate or modify them."
        )

        translated = self.provider.generate(
            system_prompt + extra_instruction,
            body_with_placeholders,
        )

        # Re-inject code blocks
        for placeholder, original in placeholder_map.items():
            translated = translated.replace(placeholder, original)

        # Re-inject inline code
        for idx, code in enumerate(inline_codes):
            placeholder = f"⟦INLINE_{idx}⟧"
            translated = translated.replace(placeholder, code)

        return translated.strip()

    # ── Verification ─────────────────────────────────────────

    @staticmethod
    def _verify_code_blocks(
        original: list[str], translated: list[str]
    ) -> bool:
        """
        Check if code blocks were preserved during translation.
        Returns True if all original code blocks appear in the output.
        """
        if len(original) != len(translated):
            logger.debug(
                f"Block count mismatch: {len(original)} vs {len(translated)}"
            )
            return False

        for i, (orig, trans) in enumerate(zip(original, translated)):
            # Normalize whitespace for comparison
            orig_normalized = orig.strip()
            trans_normalized = trans.strip()
            if orig_normalized != trans_normalized:
                logger.debug(f"Block {i} content mismatch")
                return False

        return True

    # ── Tag generation ───────────────────────────────────────

    def generate_tags(
        self, translated_body: str, max_tags: int = 8
    ) -> list[str]:
        """
        Use the LLM to generate relevant tags from translated content.
        Returns a list of lowercase tag strings.
        """
        logger.info("Generating tags from translated content...")

        system_prompt = (
            "You are a technical content tagger. "
            "Given a technical article, extract the most relevant tags. "
            "Return ONLY a JSON array of lowercase strings, nothing else. "
            "Focus on technologies, tools, concepts, and techniques mentioned. "
            f"Return at most {max_tags} tags."
        )

        # Send only the first 2000 chars to save tokens
        snippet = translated_body[:2000]

        result = self.provider.generate(system_prompt, snippet)

        # Parse the JSON array
        try:
            # Strip any markdown formatting the LLM might add
            result = result.strip()
            if result.startswith("```"):
                result = re.sub(r"```\w*\n?", "", result).strip()

            import json
            tags = json.loads(result)

            if isinstance(tags, list):
                tags = [
                    str(t).lower().strip()
                    for t in tags
                    if isinstance(t, str) and t.strip()
                ][:max_tags]
                logger.success(f"Generated tags: {tags}")
                return tags
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse LLM tag output: {e}")

        # Fallback: extract simple tags from common patterns
        logger.info("Falling back to regex-based tag extraction")
        return self._extract_tags_fallback(translated_body, max_tags)

    @staticmethod
    def _extract_tags_fallback(text: str, max_tags: int) -> list[str]:
        """Simple regex-based tag extraction as a fallback."""
        # Look for technology names in inline code
        inline_matches = re.findall(r"`([a-zA-Z][\w\-\.]*)`", text)
        # Deduplicate and take top entries
        seen = set()
        tags = []
        for match in inline_matches:
            lower = match.lower()
            if lower not in seen and len(lower) > 2:
                seen.add(lower)
                tags.append(lower)
                if len(tags) >= max_tags:
                    break
        return tags
