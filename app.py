"""
app.py — "Trading School"
=========================

A friendly Streamlit web app that teaches a complete beginner how to read
stock charts, candlestick patterns, and technical indicators in PLAIN ENGLISH.

It has four tabs:
    1. Chart Trainer  -> live data, interactive chart, plain-English read-out.
    2. Pattern Library-> a visual dictionary of patterns.
    3. Quiz Mode      -> test yourself, with explanations and a running score.
    4. Glossary       -> searchable definitions, simple-first.

HOW TO READ THIS FILE (for a non-coder):
    - "import" lines at the top just borrow tools other people wrote.
    - We define small helper FUNCTIONS (reusable mini-machines) for the maths.
    - Then each tab is built by its own function (render_chart_trainer, etc.).
    - At the very bottom, main() wires the tabs together.
    - All the WORDS (definitions, patterns) live in content.py, not here.

To run it locally:   streamlit run app.py
"""

# ---------------------------------------------------------------------------
# IMPORTS — borrowing tools written by others.
# ---------------------------------------------------------------------------
import streamlit as st          # builds the whole web interface
import pandas as pd             # tables of data (rows/columns), like a spreadsheet
import numpy as np              # fast maths on lots of numbers at once
import plotly.graph_objects as go   # interactive charts

# We import yfinance DEFENSIVELY. yfinance fetches live stock data from the
# internet. If it's missing or the install is broken, we DON'T want the whole
# app to crash — the Glossary, Pattern Library and Quiz should still work.
# So we "try" to import it; if that fails we just remember it's unavailable.
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except Exception:               # noqa: BLE001 — we genuinely want to catch all
    YFINANCE_AVAILABLE = False

# Our own content file — the single source of truth for all the text.
import content


# ---------------------------------------------------------------------------
# PAGE CONFIG — the browser tab title, icon, and wide layout.
# This must be the FIRST Streamlit command that runs.
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Trading School",
    page_icon="📈",
    layout="wide",
)


# ===========================================================================
#  PART A: THE MATHS HELPERS
#  Small, well-named functions so the tab code reads like plain English.
# ===========================================================================

def compute_rsi(close_prices: pd.Series, period: int = 14) -> pd.Series:
    """Calculate the RSI (the 0–100 'speedometer') for a price series.

    Plain English: RSI compares the size of recent UP moves to recent DOWN
    moves. Lots of up moves -> high RSI (overbought). Lots of down moves ->
    low RSI (oversold).

    Args:
        close_prices: the daily closing prices.
        period: how many days to look back (14 is the classic default).

    Returns:
        A series of RSI values lined up with the dates.
    """
    # Day-to-day price change (today's close minus yesterday's).
    delta = close_prices.diff()

    # Split those changes into gains (ups) and losses (downs as positive nums).
    gains = delta.clip(lower=0)          # negatives become 0
    losses = -delta.clip(upper=0)        # positives become 0, then flip sign

    # Average gain / average loss over the lookback window. We use an
    # exponential-style smoothing (Wilder's method) via .ewm for a standard RSI.
    avg_gain = gains.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = losses.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()

    # RS = relative strength = average gain / average loss.
    # We guard against dividing by zero (no losses at all) using a tiny number.
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))

    # If there were no losses, RSI is effectively 100 (pure strength).
    rsi = rsi.fillna(100)
    return rsi


def compute_moving_average(close_prices: pd.Series, window: int) -> pd.Series:
    """Average price over a rolling window (smooths out the daily jitters)."""
    return close_prices.rolling(window=window).mean()


def compute_fibonacci_levels(high: float, low: float) -> dict[str, float]:
    """Work out the Fibonacci retracement price levels for a swing.

    Plain English: given the highest and lowest price of the recent move, this
    returns the popular 'pullback floors' where price often pauses.

    Returns a dictionary like {"61.8%": 142.30, ...}.
    """
    span = high - low                     # total size of the move
    ratios = {
        "0% (high)": 0.0,
        "23.6%": 0.236,
        "38.2%": 0.382,
        "50%": 0.5,
        "61.8%": 0.618,                   # the famous 'golden' level
        "78.6%": 0.786,
        "100% (low)": 1.0,
    }
    # Each level = high minus a fraction of the move (measuring down from top).
    return {label: high - span * ratio for label, ratio in ratios.items()}


def detect_candlestick_patterns(data: pd.DataFrame) -> list[dict]:
    """Scan the recent candles and flag simple, well-known patterns.

    This is intentionally a LIGHTWEIGHT, transparent detector (no black-box
    library) so a learner can understand exactly why each flag appears. It
    looks at the most recent ~60 candles and returns a list of hits.

    Each hit is a dict: {"date", "price", "name", "bias"}.
    """
    hits: list[dict] = []

    # We need open/high/low/close columns. Work on a recent slice for speed.
    recent = data.tail(60)

    # .itertuples gives us each row; we also need the PREVIOUS row for two-candle
    # patterns, so we track it as we go.
    prev = None
    for row in recent.itertuples():
        o, h, l, c = row.Open, row.High, row.Low, row.Close  # noqa: E741
        body = abs(c - o)
        candle_range = h - l
        # Avoid division by zero on a flat candle.
        if candle_range == 0:
            prev = row
            continue

        upper_wick = h - max(o, c)
        lower_wick = min(o, c) - l

        # --- Doji: open and close almost equal (tiny body vs the full range).
        if body <= 0.1 * candle_range:
            hits.append({"date": row.Index, "price": h,
                         "name": "Doji", "bias": "Neutral"})

        # --- Hammer: small body up top, long lower wick, little upper wick.
        elif (lower_wick >= 2 * body) and (upper_wick <= body):
            hits.append({"date": row.Index, "price": l,
                         "name": "Hammer", "bias": "Bullish"})

        # --- Shooting Star: small body at bottom, long upper wick.
        elif (upper_wick >= 2 * body) and (lower_wick <= body):
            hits.append({"date": row.Index, "price": h,
                         "name": "Shooting Star", "bias": "Bearish"})

        # --- Two-candle patterns need the previous candle.
        if prev is not None:
            p_o, p_c = prev.Open, prev.Close
            # Bullish engulfing: prev red, today green, today's body engulfs it.
            if (p_c < p_o) and (c > o) and (c >= p_o) and (o <= p_c):
                hits.append({"date": row.Index, "price": l,
                             "name": "Bullish Engulfing", "bias": "Bullish"})
            # Bearish engulfing: prev green, today red, today's body engulfs it.
            elif (p_c > p_o) and (c < o) and (o >= p_c) and (c <= p_o):
                hits.append({"date": row.Index, "price": h,
                             "name": "Bearish Engulfing", "bias": "Bearish"})

        prev = row

    return hits


# ===========================================================================
#  PART B: LIVE DATA (cached so we don't hammer the data source)
# ===========================================================================

# @st.cache_data tells Streamlit: "remember the result of this function for a
# while". ttl=300 means 300 seconds = 5 minutes. So if 50 people look up NVDA
# in 5 minutes, we only actually call the internet once. Friendly to the
# free data source, and faster for everyone.
@st.cache_data(ttl=300, show_spinner=False)
def fetch_stock_data(ticker: str, period: str = "6mo") -> pd.DataFrame | None:
    """Download recent daily price data for a ticker.

    Returns a clean DataFrame (Open/High/Low/Close/Volume) or None if anything
    goes wrong (bad ticker, no internet, service down). Returning None instead
    of crashing lets the caller show a friendly message.
    """
    if not YFINANCE_AVAILABLE:
        return None

    try:
        # auto_adjust=True gives split/dividend-adjusted prices (cleaner charts).
        raw = yf.download(
            ticker,
            period=period,
            interval="1d",
            auto_adjust=True,
            progress=False,
        )
    except Exception:               # noqa: BLE001 — any network/parse error
        return None

    # An empty result means the ticker was invalid or no data came back.
    if raw is None or raw.empty:
        return None

    # Newer yfinance can return "multi-level" columns (a tuple per column) when
    # given one ticker. Flatten that so we have plain 'Open', 'Close', etc.
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)

    # Keep only the columns we need and drop any rows with missing values.
    needed = ["Open", "High", "Low", "Close", "Volume"]
    raw = raw[[col for col in needed if col in raw.columns]].dropna()

    if raw.empty:
        return None
    return raw


# ===========================================================================
#  PART C: TAB 1 — CHART TRAINER
# ===========================================================================

def render_chart_trainer() -> None:
    """Build the Chart Trainer tab: live stats, chart, and a plain read-out."""
    st.header("📊 Chart Trainer")
    st.write(
        "Type a ticker symbol (the short code for a company) and we'll pull "
        "**live data**, show you the chart, and explain what it's telling you "
        "in plain English."
    )

    # --- The input row: ticker box + overlay toggles. ---------------------
    col_input, col_period = st.columns([2, 1])
    with col_input:
        ticker = st.text_input(
            "Ticker symbol",
            value="NVDA",
            help="Examples: NVDA (Nvidia), AAPL (Apple), MSFT (Microsoft), "
                 "TSLA (Tesla).",
        ).strip().upper()
    with col_period:
        period = st.selectbox(
            "How much history?",
            options=["3mo", "6mo", "1y"],
            index=1,
            help="How far back the chart looks.",
        )

    # Overlay toggles — let the learner turn things on/off to see the effect.
    st.write("**Chart overlays** (toggle these on and off to learn what each does):")
    t1, t2, t3, t4 = st.columns(4)
    show_ma20 = t1.checkbox("20-day average", value=True)
    show_ma50 = t2.checkbox("50-day average", value=True)
    show_fib = t3.checkbox("Fibonacci levels", value=True)
    show_patterns = t4.checkbox("Candle patterns", value=True)

    if not ticker:
        st.info("Type a ticker symbol above to begin.")
        return

    # --- Guard: is live data even available? ------------------------------
    if not YFINANCE_AVAILABLE:
        st.error(
            "⚠️ Live data isn't available right now (the data tool failed to "
            "load). The other tabs — Pattern Library, Quiz and Glossary — still "
            "work perfectly. Try the Chart Trainer again later."
        )
        return

    # --- Fetch the data (cached for 5 minutes). ---------------------------
    with st.spinner(f"Fetching live data for {ticker}…"):
        data = fetch_stock_data(ticker, period=period)

    if data is None or len(data) < 20:
        st.error(
            f"Couldn't get enough data for **{ticker}**. Double-check the "
            "symbol is correct (e.g. NVDA, not 'Nvidia'), or try again in a "
            "moment — the free data source occasionally hiccups."
        )
        return

    # ----------------------------------------------------------------------
    # THE GOLDEN RULE OF THIS APP:
    # ALWAYS show live price, % change, volume-vs-average, and RSI FIRST,
    # before any chart or analysis. Never analyse without showing these.
    # ----------------------------------------------------------------------

    close = data["Close"]
    volume = data["Volume"]

    latest_price = float(close.iloc[-1])
    prev_price = float(close.iloc[-2])
    pct_change = (latest_price - prev_price) / prev_price * 100

    latest_volume = float(volume.iloc[-1])
    avg_volume_20 = float(volume.tail(20).mean())
    volume_ratio = latest_volume / avg_volume_20 if avg_volume_20 else 0

    rsi_series = compute_rsi(close)
    latest_rsi = float(rsi_series.iloc[-1])

    st.subheader(f"Live snapshot — {ticker}")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(
        "Current price",
        f"${latest_price:,.2f}",
        f"{pct_change:+.2f}% vs yesterday",
    )
    m2.metric(
        "Volume (today)",
        f"{latest_volume:,.0f}",
        help="How many shares traded — the size of the crowd.",
    )
    m3.metric(
        "Volume vs 20-day avg",
        f"{volume_ratio:.2f}×",
        help="Above 1× means busier than usual; below 1× means quieter.",
    )
    m4.metric(
        "RSI (14-day)",
        f"{latest_rsi:.0f}",
        help="0–100 speedometer. Above 70 = overbought, below 30 = oversold.",
    )

    st.caption(
        "☝️ We ALWAYS show live price and volume before any analysis. "
        "Numbers reflect the latest available data (cached up to 5 minutes)."
    )

    # ----------------------------------------------------------------------
    # THE CANDLESTICK CHART with the toggled overlays.
    # ----------------------------------------------------------------------
    fig = go.Figure()

    # The candles themselves.
    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data["Open"],
            high=data["High"],
            low=data["Low"],
            close=data["Close"],
            name="Price",
            increasing_line_color="#26a69a",   # calm green for up days
            decreasing_line_color="#ef5350",   # soft red for down days
        )
    )

    # 20-day moving average overlay.
    if show_ma20:
        ma20 = compute_moving_average(close, 20)
        fig.add_trace(go.Scatter(
            x=data.index, y=ma20, mode="lines",
            name="20-day avg", line=dict(color="#42a5f5", width=1.5),
        ))

    # 50-day moving average overlay.
    if show_ma50:
        ma50 = compute_moving_average(close, 50)
        fig.add_trace(go.Scatter(
            x=data.index, y=ma50, mode="lines",
            name="50-day avg", line=dict(color="#ab47bc", width=1.5),
        ))

    # Fibonacci retracement levels, drawn as horizontal lines.
    # We base them on the high/low of the visible window.
    swing_high = float(data["High"].max())
    swing_low = float(data["Low"].min())
    fib_levels = compute_fibonacci_levels(swing_high, swing_low)
    if show_fib:
        for label, level in fib_levels.items():
            # Emphasise the 'golden' 61.8% level: thicker, gold, dashed.
            is_golden = label.startswith("61.8")
            fig.add_hline(
                y=level,
                line=dict(
                    color="#FFB300" if is_golden else "rgba(150,150,150,0.5)",
                    width=2.5 if is_golden else 1,
                    dash="dash",
                ),
                annotation_text=f"Fib {label}" + (" ⭐ golden" if is_golden else ""),
                annotation_position="right",
                annotation_font_size=11,
            )

    # Auto-detected candlestick patterns, marked with arrows.
    detected = detect_candlestick_patterns(data) if show_patterns else []
    if detected:
        # Bullish hits point up (green); bearish point down (red); neutral grey.
        colour_map = {"Bullish": "#26a69a", "Bearish": "#ef5350",
                      "Neutral": "#9e9e9e"}
        symbol_map = {"Bullish": "triangle-up", "Bearish": "triangle-down",
                      "Neutral": "circle"}
        for bias in ["Bullish", "Bearish", "Neutral"]:
            pts = [h for h in detected if h["bias"] == bias]
            if not pts:
                continue
            fig.add_trace(go.Scatter(
                x=[p["date"] for p in pts],
                y=[p["price"] for p in pts],
                mode="markers",
                name=f"{bias} pattern",
                marker=dict(symbol=symbol_map[bias], size=12,
                            color=colour_map[bias],
                            line=dict(width=1, color="white")),
                text=[p["name"] for p in pts],
                hovertemplate="%{text}<br>%{x|%d %b %Y}<extra></extra>",
            ))

    fig.update_layout(
        title=f"{ticker} — daily candlesticks",
        xaxis_rangeslider_visible=False,   # hide the mini-slider for a clean look
        height=560,
        margin=dict(l=10, r=80, t=50, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    # ----------------------------------------------------------------------
    # "WHAT THIS CHART IS TELLING YOU" — generated from the ACTUAL numbers.
    # ----------------------------------------------------------------------
    st.subheader("🧠 What this chart is telling you")
    insights = build_plain_english_read(
        ticker=ticker,
        pct_change=pct_change,
        volume_ratio=volume_ratio,
        latest_rsi=latest_rsi,
        latest_price=latest_price,
        fib_levels=fib_levels,
        close=close,
        show_ma20=show_ma20,
        show_ma50=show_ma50,
        detected=detected,
    )
    for line in insights:
        st.markdown(f"- {line}")

    st.caption(
        "These notes are generated automatically from what's actually on the "
        "chart right now. They're hints to help you learn — not advice."
    )


def build_plain_english_read(
    *,                              # everything after this must be named (clarity)
    ticker: str,
    pct_change: float,
    volume_ratio: float,
    latest_rsi: float,
    latest_price: float,
    fib_levels: dict[str, float],
    close: pd.Series,
    show_ma20: bool,
    show_ma50: bool,
    detected: list[dict],
) -> list[str]:
    """Turn the raw numbers into friendly, plain-English bullet points.

    Returns a list of strings. The Chart Trainer prints each as a bullet.
    """
    notes: list[str] = []

    # --- Today's move. ----------------------------------------------------
    if pct_change > 1:
        notes.append(
            f"**{ticker} is up {pct_change:+.2f}% today** — buyers are in "
            "control on the day."
        )
    elif pct_change < -1:
        notes.append(
            f"**{ticker} is down {pct_change:+.2f}% today** — sellers have the "
            "upper hand on the day."
        )
    else:
        notes.append(
            f"**{ticker} is roughly flat today ({pct_change:+.2f}%)** — a quiet, "
            "indecisive session."
        )

    # --- Volume (the crowd size). ----------------------------------------
    if volume_ratio >= 2:
        notes.append(
            f"Volume is **{volume_ratio:.1f}× the 20-day average — a big "
            "crowd**. Heavy volume makes today's move more trustworthy."
        )
    elif volume_ratio >= 1.3:
        notes.append(
            f"Volume is **{volume_ratio:.1f}× average — busier than usual**, so "
            "there's real interest behind the move."
        )
    elif volume_ratio <= 0.7:
        notes.append(
            f"Volume is only **{volume_ratio:.1f}× average — a thin crowd**. "
            "Low-volume moves are easier to reverse, so trust them less."
        )
    else:
        notes.append(
            f"Volume is **about average ({volume_ratio:.1f}×)** — a normal day "
            "of activity."
        )

    # --- RSI (the speedometer). ------------------------------------------
    if latest_rsi >= 70:
        notes.append(
            f"RSI is **{latest_rsi:.0f} — overbought**. Price is stretched like "
            "a rubber band; chasing it here is riskier and a pause or pullback "
            "wouldn't be surprising."
        )
    elif latest_rsi <= 30:
        notes.append(
            f"RSI is **{latest_rsi:.0f} — oversold**. The stock has been beaten "
            "down hard; bounces sometimes start from here, but falling knives "
            "can keep falling."
        )
    else:
        notes.append(
            f"RSI is **{latest_rsi:.0f} — in the neutral middle zone**, neither "
            "overbought nor oversold. No extreme to lean on."
        )

    # --- Position vs the 61.8% 'golden' Fibonacci level. -----------------
    golden = fib_levels.get("61.8%")
    if golden:
        distance_pct = abs(latest_price - golden) / latest_price * 100
        if distance_pct <= 2:
            notes.append(
                "Price is **right near the 61.8% Fibonacci 'golden' level** "
                f"(~${golden:,.2f}). Pullbacks often find support and bounce "
                "around here — a level worth watching."
            )

    # --- Trend vs moving averages. ---------------------------------------
    if show_ma20:
        ma20_now = compute_moving_average(close, 20).iloc[-1]
        if not np.isnan(ma20_now):
            if latest_price > ma20_now:
                notes.append(
                    "Price is **above its 20-day average** — the short-term "
                    "trend is up (the recent tide is rising)."
                )
            else:
                notes.append(
                    "Price is **below its 20-day average** — the short-term "
                    "trend is down (the recent tide is falling)."
                )
    if show_ma50:
        ma50_now = compute_moving_average(close, 50).iloc[-1]
        if not np.isnan(ma50_now):
            if latest_price > ma50_now:
                notes.append(
                    "Price is **above its 50-day average** too — the broader "
                    "trend is healthy."
                )
            else:
                notes.append(
                    "Price is **below its 50-day average** — the broader trend "
                    "is still weak."
                )

    # --- Most recent detected pattern. -----------------------------------
    if detected:
        last = detected[-1]
        notes.append(
            f"Most recent pattern spotted: a **{last['name']}** "
            f"({last['bias'].lower()} hint) on "
            f"{last['date'].strftime('%d %b %Y')}. See the Pattern Library tab "
            "for what it means and how much to trust it."
        )

    return notes


# ===========================================================================
#  PART D: TAB 2 — PATTERN LIBRARY
# ===========================================================================

def render_pattern_library() -> None:
    """A filterable visual dictionary of candlestick & chart patterns."""
    st.header("📚 Pattern Library")
    st.write(
        "A visual dictionary of the patterns traders look for. Each one has a "
        "simple sketch, a plain-English meaning, and an **honest reliability "
        "note** — because not all patterns are equally trustworthy."
    )

    # Filter controls.
    f1, f2 = st.columns(2)
    type_filter = f1.selectbox(
        "Pattern type", options=["All", "Candlestick", "Chart"], index=0,
    )
    bias_filter = f2.selectbox(
        "Bias (direction it hints)",
        options=["All", "Bullish", "Bearish", "Neutral"], index=0,
    )

    # Apply the filters by keeping only patterns that match.
    patterns = [
        p for p in content.PATTERNS
        if (type_filter == "All" or p["type"] == type_filter)
        and (bias_filter == "All" or p["bias"] == bias_filter)
    ]

    if not patterns:
        st.info("No patterns match those filters. Try widening them.")
        return

    # A small colour for each bias so the cards are scannable.
    bias_emoji = {"Bullish": "🟢", "Bearish": "🔴", "Neutral": "⚪"}

    # Show patterns two-per-row for a tidy grid.
    for i in range(0, len(patterns), 2):
        cols = st.columns(2)
        for col, pattern in zip(cols, patterns[i:i + 2]):
            with col:
                with st.container(border=True):
                    st.markdown(
                        f"### {bias_emoji[pattern['bias']]} {pattern['name']}"
                    )
                    st.caption(f"{pattern['type']} pattern · {pattern['bias']} bias")
                    # The ASCII sketch, shown in a monospace code block so it
                    # keeps its shape.
                    st.code(pattern["sketch"], language=None)
                    st.markdown(f"**What it means:** {pattern['meaning']}")
                    st.markdown(f"**Reliability:** {pattern['reliability']}")


# ===========================================================================
#  PART E: TAB 3 — QUIZ MODE
# ===========================================================================

def render_quiz() -> None:
    """Show a pattern and ask the user to identify it; track the score."""
    st.header("🎯 Quiz Mode")
    st.write(
        "Look at the sketch and the hint, then pick the pattern. We'll tell you "
        "if you're right **and why**, and keep your score for this session."
    )

    # Streamlit forgets variables between clicks UNLESS we store them in
    # st.session_state — a little memory box that survives button presses.
    # We set up the quiz once and keep it there.
    if "quiz_questions" not in st.session_state:
        st.session_state.quiz_questions = content.build_quiz_questions()
        st.session_state.quiz_index = 0       # which question we're on
        st.session_state.quiz_score = 0       # how many correct
        st.session_state.quiz_attempts = 0    # how many answered
        st.session_state.quiz_answered = False  # has the current one been answered?
        st.session_state.quiz_last_correct = False

    questions = st.session_state.quiz_questions
    index = st.session_state.quiz_index
    question = questions[index]

    # Scoreboard at the top.
    s1, s2, s3 = st.columns(3)
    s1.metric("Score", f"{st.session_state.quiz_score}")
    s2.metric("Answered", f"{st.session_state.quiz_attempts}")
    accuracy = (
        st.session_state.quiz_score / st.session_state.quiz_attempts * 100
        if st.session_state.quiz_attempts else 0
    )
    s3.metric("Accuracy", f"{accuracy:.0f}%")

    st.divider()
    st.markdown(f"**Question {index + 1} of {len(questions)} — which pattern is this?**")
    st.code(question["sketch"], language=None)
    st.markdown(f"*Hint:* {question['hint']}")

    # The multiple-choice options as radio buttons.
    # key includes the index so the selection resets on each new question.
    choice = st.radio(
        "Your answer:",
        options=question["options"],
        index=None,
        key=f"choice_{index}",
    )

    col_submit, col_next = st.columns(2)

    # --- Submit button: check the answer once. ---------------------------
    with col_submit:
        if st.button("Check answer", disabled=st.session_state.quiz_answered):
            if choice is None:
                st.warning("Pick an option first!")
            else:
                st.session_state.quiz_answered = True
                st.session_state.quiz_attempts += 1
                correct = choice == question["answer"]
                st.session_state.quiz_last_correct = correct
                if correct:
                    st.session_state.quiz_score += 1
                st.rerun()   # refresh so the feedback shows immediately

    # --- Next button: move on (and loop back to start at the end). -------
    with col_next:
        if st.button("Next question →"):
            st.session_state.quiz_index = (index + 1) % len(questions)
            st.session_state.quiz_answered = False
            st.rerun()

    # --- Feedback after answering. ---------------------------------------
    if st.session_state.quiz_answered:
        if st.session_state.quiz_last_correct:
            st.success("✅ Correct!")
        else:
            st.error(f"❌ Not quite — the answer is **{question['answer']}**.")
        st.info(question["why"])

    st.divider()
    if st.button("🔄 Reset quiz & score"):
        # Clear the quiz keys so it rebuilds fresh on the next run.
        for key in ["quiz_questions", "quiz_index", "quiz_score",
                    "quiz_attempts", "quiz_answered", "quiz_last_correct"]:
            st.session_state.pop(key, None)
        st.rerun()


# ===========================================================================
#  PART F: TAB 4 — GLOSSARY
# ===========================================================================

def render_glossary() -> None:
    """Searchable, filterable definitions — simple explanation first."""
    st.header("📖 Glossary")
    st.write(
        "Key terms explained in everyday language **first**, with a more "
        "technical version underneath for when you're ready to go deeper."
    )

    # Search + category filter.
    g1, g2 = st.columns([2, 1])
    search = g1.text_input("Search terms", placeholder="e.g. RSI, volume…").strip().lower()

    # Build the list of categories from the data (so it stays in sync).
    categories = ["All"] + sorted({item["category"] for item in content.GLOSSARY})
    category = g2.selectbox("Category", options=categories, index=0)

    # Filter: term/text matches the search AND matches the category.
    results = [
        item for item in content.GLOSSARY
        if (category == "All" or item["category"] == category)
        and (
            search == ""
            or search in item["term"].lower()
            or search in item["simple"].lower()
            or search in item["technical"].lower()
        )
    ]

    # Sort alphabetically so it reads like a real dictionary.
    results.sort(key=lambda item: item["term"].lower())

    if not results:
        st.info("No terms match your search. Try a different word.")
        return

    st.caption(f"Showing {len(results)} term(s).")

    for item in results:
        # An expander keeps the page tidy: click a term to reveal its meaning.
        with st.expander(f"**{item['term']}**  ·  _{item['category']}_"):
            st.markdown("**In plain English:**")
            st.write(item["simple"])
            st.markdown("**Going deeper (technical):**")
            st.write(item["technical"])


# ===========================================================================
#  PART G: MAIN — wire everything together.
# ===========================================================================

def render_footer() -> None:
    """The disclaimer footer shown at the bottom of every page."""
    st.divider()
    st.caption(content.DISCLAIMER)
    st.caption("Trading School · an educational project · data via yfinance.")


def main() -> None:
    """The app's entry point — builds the title and the four tabs."""
    st.title("📈 Trading School")
    st.write(
        "**Learn to read stock charts from zero.** Pick a tab below: start in "
        "the Glossary or Pattern Library to learn the vocabulary, take the Quiz "
        "to test yourself, then use the Chart Trainer on a real, live stock."
    )

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Chart Trainer",
        "📚 Pattern Library",
        "🎯 Quiz Mode",
        "📖 Glossary",
    ])

    with tab1:
        render_chart_trainer()
    with tab2:
        render_pattern_library()
    with tab3:
        render_quiz()
    with tab4:
        render_glossary()

    render_footer()


# This standard Python line means: "only run main() if this file is the one
# being launched" (which is exactly what `streamlit run app.py` does).
if __name__ == "__main__":
    main()
