"""
Tests for core.translator — Code-Aware Translation Engine
"""

import re
import pytest
from unittest.mock import MagicMock, patch

from core.translator import Translator, _FENCED_CODE_RE, _INLINE_CODE_RE


# ── Fixtures ─────────────────────────────────────────────────

@pytest.fixture
def mock_provider():
    """Create a mock LLM provider."""
    provider = MagicMock()
    provider.generate = MagicMock(return_value="Translated text")
    return provider


@pytest.fixture
def translator(mock_provider, tmp_path):
    """Create a Translator with a mock provider and temp prompt file."""
    prompt_file = tmp_path / "test_prompt.txt"
    prompt_file.write_text(
        "Translate from {source_language} to {target_language} "
        "at {target_level} level."
    )

    return Translator(
        provider=mock_provider,
        source_lang="Turkish",
        target_lang="English",
        prompt_template_path=str(prompt_file),
    )


# ── Regex Tests ──────────────────────────────────────────────

class TestCodeRegex:
    def test_fenced_code_matches(self):
        text = "Some text\n```python\nprint('hello')\n```\nMore text"
        matches = _FENCED_CODE_RE.findall(text)
        assert len(matches) == 1
        assert "print('hello')" in matches[0]

    def test_fenced_code_multiple(self):
        text = (
            "Start\n```bash\necho hi\n```\n"
            "Middle\n```yaml\nkey: value\n```\nEnd"
        )
        matches = _FENCED_CODE_RE.findall(text)
        assert len(matches) == 2

    def test_inline_code_matches(self):
        text = "Use `kubectl apply` to deploy the `nginx` pod."
        matches = _INLINE_CODE_RE.findall(text)
        assert len(matches) == 2
        assert "`kubectl apply`" in matches
        assert "`nginx`" in matches

    def test_inline_code_ignores_backtick_pairs_in_code_blocks(self):
        text = "Normal `inline` code"
        matches = _INLINE_CODE_RE.findall(text)
        assert len(matches) == 1


# ── Translator Tests ─────────────────────────────────────────

class TestTranslator:
    def test_prompt_template_loading(self, translator):
        assert "Translate from" in translator.prompt_template

    def test_build_system_prompt(self, translator):
        prompt = translator._build_system_prompt()
        assert "Turkish" in prompt
        assert "English" in prompt

    def test_translate_calls_provider(self, translator, mock_provider):
        article = "Bu bir test makalesidir."
        mock_provider.generate.return_value = "This is a test article."

        result = translator.translate(article)

        assert mock_provider.generate.called
        assert result == "This is a test article."

    def test_translate_preserves_code_blocks(self, translator, mock_provider):
        """When LLM preserves code blocks, no fallback should trigger."""
        article = "Metin\n```python\nprint('hello')\n```\nDaha fazla metin"
        translated = "Text\n```python\nprint('hello')\n```\nMore text"
        mock_provider.generate.return_value = translated

        result = translator.translate(article)

        # Should only call generate once (primary, no fallback)
        assert mock_provider.generate.call_count == 1
        assert "```python" in result
        assert "print('hello')" in result

    def test_translate_fallback_on_code_mismatch(self, translator, mock_provider):
        """When LLM modifies code blocks, the placeholder fallback should trigger."""
        article = "Metin\n```python\nprint('hello')\n```\nSon"

        # First call: LLM corrupts the code block
        # Second call (fallback): LLM returns with placeholder preserved
        mock_provider.generate.side_effect = [
            "Text\n```python\nprint('MODIFIED')\n```\nEnd",  # corrupted
            "Text\n⟦CODE_BLOCK_0⟧\nEnd",  # fallback with placeholder
        ]

        result = translator.translate(article)

        # Should call generate twice (primary + fallback)
        assert mock_provider.generate.call_count == 2
        # The original code block should be restored
        assert "print('hello')" in result


# ── Code Block Verification Tests ────────────────────────────

class TestVerification:
    def test_verify_identical_blocks(self):
        original = ["```python\ncode\n```"]
        translated = ["```python\ncode\n```"]
        assert Translator._verify_code_blocks(original, translated) is True

    def test_verify_different_count(self):
        assert Translator._verify_code_blocks(
            ["```a\n```"], ["```a\n```", "```b\n```"]
        ) is False

    def test_verify_content_mismatch(self):
        original = ["```python\noriginal\n```"]
        translated = ["```python\nmodified\n```"]
        assert Translator._verify_code_blocks(original, translated) is False

    def test_verify_empty_lists(self):
        assert Translator._verify_code_blocks([], []) is True


# ── Tag Generation Tests ────────────────────────────────────

class TestTagGeneration:
    def test_generate_tags_valid_json(self, translator, mock_provider):
        mock_provider.generate.return_value = '["python", "docker", "kubernetes"]'

        tags = translator.generate_tags("Article about Python and Docker")

        assert tags == ["python", "docker", "kubernetes"]

    def test_generate_tags_with_markdown_wrapper(self, translator, mock_provider):
        mock_provider.generate.return_value = '```json\n["python", "devops"]\n```'

        tags = translator.generate_tags("Article text")

        assert tags == ["python", "devops"]

    def test_generate_tags_fallback_on_invalid_json(self, translator, mock_provider):
        mock_provider.generate.return_value = "not valid json"

        tags = translator.generate_tags(
            "Use `Python` and `Docker` for `deployment`."
        )

        # Should fall back to regex extraction
        assert isinstance(tags, list)

    def test_generate_tags_max_limit(self, translator, mock_provider):
        mock_provider.generate.return_value = (
            '["a","b","c","d","e","f","g","h","i","j"]'
        )

        tags = translator.generate_tags("text", max_tags=3)

        assert len(tags) <= 3

    def test_fallback_tag_extraction(self):
        text = "Using `Flask` and `SQLAlchemy` with `PostgreSQL`."
        tags = Translator._extract_tags_fallback(text, max_tags=5)
        assert "flask" in tags
        assert "sqlalchemy" in tags
        assert "postgresql" in tags
