# Article Bot 🤖⚡

**Automated technical article translation & publication pipeline.**

Fetches articles from URLs, RSS feeds, or local files → translates them with a code-aware LLM → formats as Hugo Markdown → pushes to GitHub → deploys to Cloudflare Pages.

---

## ✨ Features

- **Multi-source fetching** — URL scraping, RSS feeds, local files, or direct text input
- **Code-aware translation** — Preserves code blocks, inline code, paths, commands, and URLs during translation
- **Dual translation strategy** — Primary LLM call + automatic placeholder-based fallback if code blocks are corrupted
- **LLM-generated tags** — Auto-generates relevant tags from translated content
- **Hugo-ready output** — Proper YAML frontmatter, slugified filenames, organized content/posts/ directory
- **GitHub publishing** — Direct push or PR workflow via PyGitHub
- **Multi-LLM support** — Ollama (local), OpenAI, Anthropic, Google Gemini
- **CI/CD included** — GitHub Actions → Hugo build → Cloudflare Pages deployment
- **Beautiful dark theme** — Custom Hugo site with Inter/JetBrains Mono fonts, responsive design

---

## 🏗 Architecture

```
article-bot/
├── vibe_publish.py              # CLI orchestrator (entry point)
├── config.yaml                  # Central configuration
├── core/                        # Pipeline modules
│   ├── fetcher.py               # Article input (URL, RSS, text, file)
│   ├── translator.py            # Code-aware LLM translation
│   ├── formatter.py             # Hugo Markdown formatting
│   ├── publisher.py             # GitHub push (direct / PR)
│   └── llm_providers.py         # Unified LLM abstraction
├── prompts/
│   └── code_aware_translate.txt # Translation system prompt
├── hugo_site/                   # Hugo static site
│   ├── hugo.toml
│   ├── layouts/                 # Custom dark theme
│   └── static/css/style.css
├── tests/                       # Pytest suite
└── .github/workflows/deploy.yml # CI/CD
```

---

## 🚀 Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/YOUR_USER/article-bot.git
cd article-bot
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate # Linux/macOS
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env with your API keys
```

Edit `config.yaml` to set your LLM provider, GitHub repo, and deployment settings.

### 3. Run

```bash
# Translate an article from URL
python vibe_publish.py --url https://example.com/article

# From a local file
python vibe_publish.py --file article.md

# From direct text
python vibe_publish.py --text "Article content here..."

# From RSS feed (batch)
python vibe_publish.py --rss https://blog.example.com/feed.xml --rss-limit 5

# Dry run (no GitHub push)
python vibe_publish.py --url https://example.com/article --dry-run
```

---

## ⚙️ Configuration

### config.yaml

| Section       | Key               | Description                              |
|---------------|-------------------|------------------------------------------|
| `llm`         | `provider`        | `ollama`, `openai`, `anthropic`, `google`|
| `llm`         | `model`           | Model name (e.g., `qwen2.5:14b`)        |
| `llm`         | `base_url`        | Ollama endpoint (default: localhost)     |
| `translation` | `source_language`  | Source language (default: Turkish)       |
| `translation` | `target_language`  | Target language (default: English)       |
| `tags`        | `enabled`         | Auto-generate tags via LLM              |
| `hugo`        | `site_dir`        | Hugo site directory                      |
| `github`      | `repository`      | `owner/repo` format                     |
| `github`      | `push_strategy`   | `direct` or `pr`                        |
| `deployment`  | `platform`        | `cloudflare` or `vercel`                |

### Environment Variables (.env)

```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AI...
GITHUB_TOKEN=ghp_...
CLOUDFLARE_API_TOKEN=...
CLOUDFLARE_ACCOUNT_ID=...
OLLAMA_BASE_URL=http://localhost:11434
```

---

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_translator.py -v

# With coverage
python -m pytest tests/ -v --cov=core
```

---

## 🔄 CI/CD (GitHub Actions → Cloudflare Pages)

The included workflow (`.github/workflows/deploy.yml`) automatically:

1. Builds the Hugo site on every push to `main`
2. Deploys to Cloudflare Pages

**Required GitHub Secrets:**
- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`

---

## 📝 How It Works

1. **Fetch** — Article is scraped from URL, parsed from RSS, read from file, or taken as direct text
2. **Translate** — The LLM translates the article using a specialized code-aware prompt that preserves all code blocks, inline code, paths, and commands
3. **Verify** — Code blocks in the output are compared to the original. If corruption is detected, a placeholder-based fallback strategy kicks in automatically
4. **Tag** — The LLM generates relevant tags from the translated content
5. **Format** — The article is wrapped in Hugo YAML frontmatter with slug, tags, date, and original URL
6. **Publish** — The formatted Markdown is pushed to GitHub (direct or via PR)
7. **Deploy** — GitHub Actions builds Hugo and deploys to Cloudflare Pages

---

## 📄 License

MIT
