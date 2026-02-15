# 🏗️ AI Website Builder

> **Multi-Agent AI system that builds production-ready landing pages in minutes.**

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40%2B-FF4B4B?logo=streamlit)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## ✨ What is this?

Describe your business in plain text → get a fully built, SEO-optimized landing page.  
8 specialized AI agents collaborate through an automated pipeline with quality assurance.

## 🧠 Architecture

```
Strategist  →  Copywriter + Art Director (parallel)  →  Developer  →  Reviewer ⟲ Auto-Fix  →  SEO Optimizer
```

| Agent | Role |
|---|---|
| 🧠 **Strategist** | Market research, target audience, brand voice |    
| ✍️ **Copywriter** | Conversion-optimized website copy |
| 🎨 **Art Director** | Visual identity — colors, fonts, gradients |
| 💻 **Developer** | Production HTML/CSS with Tailwind |
| 🔍 **Reviewer** | Quality audit (accessibility, performance, SEO) |
| 📈 **SEO Optimizer** | Meta tags, Schema.org, Open Graph |
| 💬 **Refinement** | Conversational iteration on the result |
| 🧪 **A/B Variant** | Alternative copy variations for testing |

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/neryangel/ai-website-builder.git
cd ai-website-builder

# 2. Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Configure API keys
cp .env.example .env
# Edit .env with your API keys (at minimum GOOGLE_API_KEY)

# 4. Run
streamlit run app.py
```

## 🎯 Features

- **6 Templates** — Landing Page, SaaS, Restaurant, Portfolio, E-commerce, Agency
- **3 AI Providers** — Google Gemini (free tier), OpenAI, Anthropic  
- **Auto-Fix Loop** — Reviewer catches issues, Developer fixes them automatically
- **Multi-format Export** — HTML, React Component, Next.js Page
- **One-click Deploy** — ZIP packages for Vercel, Netlify, GitHub Pages
- **A/B Testing** — Auto-generated copy variants
- **Project Management** — Save, load, version history
- **Conversational Refinement** — Chat to iterate on your website

## 📁 Project Structure

```
├── agents/           # 8 AI agents + base class
│   ├── base.py       # Abstract base with retry, parsing, cost tracking
│   ├── strategist.py
│   ├── copywriter.py
│   ├── art_director.py
│   ├── developer.py
│   ├── reviewer.py
│   ├── seo_optimizer.py
│   ├── refinement.py
│   └── ab_variant.py
├── orchestrator/     # Pipeline engine
│   └── pipeline.py   # 6-stage pipeline with parallel execution
├── providers/        # AI provider adapters
│   ├── gemini.py
│   ├── openai_provider.py
│   └── anthropic_provider.py
├── storage/          # Project persistence
├── ui/               # Streamlit UI components
├── utils/            # Components library, export, deploy
├── tests/            # Unit tests
├── app.py            # Entry point
└── config.py         # Configuration & model registry
```

## 🔑 API Keys

| Provider | Get Key | Free Tier |
|---|---|---|
| **Google Gemini** | [aistudio.google.com](https://aistudio.google.com) | ✅ Yes (gemini-2.0-flash) |
| **OpenAI** | [platform.openai.com](https://platform.openai.com) | ❌ Paid |
| **Anthropic** | [console.anthropic.com](https://console.anthropic.com) | ❌ Paid |

## 📄 License

MIT — use freely for personal and commercial projects.
