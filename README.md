# 📈 Trading School

A friendly, beginner-first web app that teaches you how to read **stock charts,
candlestick patterns, and technical indicators in plain English** — no jargon,
no assumptions, lots of everyday analogies (volume = crowd size, stop-loss =
safety net).

> ⚠️ **Educational tool only — not financial advice.** Patterns and indicators
> are hints, never guarantees. Always verify the live price and volume yourself.

---

## What it does — the four tabs

| Tab | What you get |
| --- | --- |
| **📊 Chart Trainer** | Type a ticker (e.g. `NVDA`). It pulls **live data**, and — before anything else — shows the **current price, % change, volume vs its 20-day average, and RSI**. Then an interactive candlestick chart with toggleable overlays (Fibonacci levels with the 61.8% "golden" level highlighted, 20- & 50-day moving averages, auto-detected candle patterns), plus a **"What this chart is telling you"** read-out in plain English. |
| **📚 Pattern Library** | A filterable visual dictionary of candlestick & chart patterns. Each one has a simple sketch, a plain-English meaning, and an **honest reliability note**. |
| **🎯 Quiz Mode** | Identify a pattern from multiple choice. It tells you if you're right **and why**, and tracks your score for the session. |
| **📖 Glossary** | Searchable definitions. **Simple explanation first**, technical version underneath for when you're ready. |

---

## The files (in plain English)

- **`app.py`** — the app itself: the four tabs, the live-data fetching, the
  maths (RSI, moving averages, Fibonacci, pattern detection), and the charts.
- **`content.py`** — the **single source of truth** for all the *words*: every
  glossary definition and every pattern description lives here, exactly once.
  Fix a definition here and it updates everywhere. (It has no internet code, so
  the Glossary, Pattern Library and Quiz keep working even if data fetching is
  down.)
- **`requirements.txt`** — the list of free libraries the app needs. Streamlit
  Cloud installs these for you.
- **`README.md`** — this file.

---

## Run it on your own computer

You need **Python 3.13 or newer**. Check with `python --version`.

```bash
# 1. (Optional but recommended) create a clean "virtual environment"
python -m venv .venv
source .venv/bin/activate        # on Windows: .venv\Scripts\activate

# 2. Install the libraries
pip install -r requirements.txt

# 3. Launch the app
streamlit run app.py
```

Your browser opens automatically at `http://localhost:8501`. Press `Ctrl+C` in
the terminal to stop it.

---

## Deploy it FREE on Streamlit Community Cloud

This puts your app on the public internet with a shareable link — no servers, no
cost. Two parts: **(A) put the code on GitHub**, then **(B) point Streamlit at
it**.

### A. Put the code on GitHub

1. Make a free account at <https://github.com> if you don't have one.
2. Click the **＋** (top-right) → **New repository**.
3. Name it (e.g. `trading-school`), keep it **Public**, click **Create
   repository**.
4. Upload your files. The easiest no-terminal way:
   - On the new repo page, click **uploading an existing file**.
   - Drag in `app.py`, `content.py`, `requirements.txt`, and `README.md`.
   - Click **Commit changes**.

   *(Or, if you use git on the command line:)*
   ```bash
   git init
   git add app.py content.py requirements.txt README.md
   git commit -m "Trading School app"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/trading-school.git
   git push -u origin main
   ```

### B. Deploy on Streamlit Community Cloud

1. Go to <https://share.streamlit.io> and **sign in with GitHub** (allow access
   when asked).
2. Click **Create app** → **Deploy a public app from GitHub**.
3. Fill in:
   - **Repository:** `YOUR-USERNAME/trading-school`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. Click **Deploy**. The first build takes a minute or two while it installs the
   libraries.
5. You'll get a public URL like `https://your-app-name.streamlit.app` — share
   it with anyone! 🎉

**Updating later:** any time you change a file on GitHub, Streamlit Cloud
automatically rebuilds and redeploys. No extra steps.

---

## Troubleshooting

- **"Couldn't get enough data"** in Chart Trainer → check the ticker symbol is
  right (use `NVDA`, not `Nvidia`), or wait a moment — the free data source
  (Yahoo Finance via `yfinance`) occasionally rate-limits or hiccups. The other
  three tabs always work regardless.
- **Build fails on Streamlit Cloud** → make sure `requirements.txt` is in the
  repository root next to `app.py`.

---

*Built as a learning project. Stay curious, manage your risk, and never trade
money you can't afford to lose.*
