"""
content.py
==========

This is the "single source of truth" for all the EDUCATIONAL TEXT in the app.

Why keep it separate from app.py?
    Imagine you write the definition of "RSI" in three different places.
    Later you improve the wording. Now you have to remember to fix it in all
    three places — and you will forget one. Instead, we write every definition
    and every pattern description EXACTLY ONCE, here. Every tab in the app reads
    from this file. Fix it once -> it updates everywhere.

There is no Streamlit, no charts, and no live data in this file — it is pure
plain Python data (dictionaries and lists). That means the "static" tabs
(Glossary, Pattern Library, Quiz) keep working perfectly even if the internet
or the live-data service is down.

The file has three sections:
    1. GLOSSARY      -> key terms, explained simply first, then technically.
    2. PATTERNS      -> candlestick + chart patterns for the Pattern Library.
    3. QUIZ_QUESTIONS-> questions built automatically from the patterns.
"""

# ---------------------------------------------------------------------------
# SECTION 1: GLOSSARY
# ---------------------------------------------------------------------------
# A list of dictionaries. Each dictionary is one term.
#   "term"      -> the word being defined.
#   "category"  -> used so the Glossary tab can filter (e.g. "Indicator").
#   "simple"    -> plain-English explanation using an everyday analogy. FIRST.
#   "technical" -> the more precise/“grown-up” version, shown underneath.
#
# Rule we follow everywhere: SIMPLE explanation first, technical second.

GLOSSARY: list[dict] = [
    {
        "term": "Volume",
        "category": "Basics",
        "simple": (
            "Volume is the SIZE OF THE CROWD. It counts how many shares "
            "changed hands. A price move on huge volume is like a stadium "
            "roaring — lots of people agree, so the move is more trustworthy. "
            "A move on tiny volume is like one person clapping in an empty "
            "room — easy to ignore."
        ),
        "technical": (
            "Volume is the total number of shares (or contracts) traded over "
            "a given period. Rising price + rising volume confirms a trend; "
            "rising price + falling volume warns of a weakening move "
            "(a 'divergence'). Volume is often compared to its own moving "
            "average (e.g. the 20-day average) to judge whether activity is "
            "unusually high or low."
        ),
    },
    {
        "term": "Candlestick",
        "category": "Basics",
        "simple": (
            "A candlestick is one little picture that tells you four things "
            "about a day: where price OPENED, where it CLOSED, and the "
            "HIGHEST and LOWEST it reached. The fat part (the 'body') is the "
            "open-to-close range. The thin lines (the 'wicks') are the "
            "extremes. Green-ish = closed higher than it opened; red-ish = "
            "closed lower. Think of it as a daily mood candle."
        ),
        "technical": (
            "A candlestick encodes OHLC (Open, High, Low, Close) for a period. "
            "Body = |Open - Close|; upper/lower wicks (shadows) extend to High "
            "and Low. Colour convention shows direction. Sequences of "
            "candlesticks form recognisable patterns used in technical "
            "analysis."
        ),
    },
    {
        "term": "Fibonacci",
        "category": "Indicator",
        "simple": (
            "After a big move, price often takes a 'breather' and pulls back "
            "part of the way before continuing. Fibonacci retracement levels "
            "are like floor markings showing the popular spots where that "
            "breather tends to stop and bounce — most famously the 61.8% "
            "level, nicknamed the 'golden' level because price respects it "
            "surprisingly often."
        ),
        "technical": (
            "Fibonacci retracements are horizontal levels at 23.6%, 38.2%, "
            "50%, 61.8% and 78.6% of a prior swing (high to low or low to "
            "high). Traders watch them as potential support/resistance zones. "
            "The ratios derive from the Fibonacci sequence; 50% is included by "
            "convention. They are self-fulfilling to a degree because many "
            "traders place orders around them."
        ),
    },
    {
        "term": "RSI",
        "category": "Indicator",
        "simple": (
            "RSI (Relative Strength Index) is a 'speedometer' from 0 to 100 "
            "for how hard a stock has been pushed recently. Above 70 it may be "
            "OVERBOUGHT — stretched like a rubber band, due for a rest. Below "
            "30 it may be OVERSOLD — beaten down, maybe due for a bounce. It "
            "warns you when chasing might be risky."
        ),
        "technical": (
            "RSI is a momentum oscillator (Wilder, 1978) measuring the speed "
            "and magnitude of price changes over a lookback period (typically "
            "14). RSI = 100 - 100/(1 + RS), where RS = average gain / average "
            "loss. >70 conventionally signals overbought, <30 oversold, though "
            "in strong trends it can stay extreme for a long time."
        ),
    },
    {
        "term": "MACD",
        "category": "Indicator",
        "simple": (
            "MACD compares a stock's recent speed to its slightly-longer-term "
            "speed to spot when momentum is shifting — like noticing a car is "
            "easing off the gas before it actually slows down. When its two "
            "lines cross, traders treat it as an early hint that the trend may "
            "be turning."
        ),
        "technical": (
            "MACD (Moving Average Convergence Divergence) = 12-period EMA minus "
            "26-period EMA. A 9-period EMA of the MACD is the 'signal line'. "
            "Bullish/bearish crossovers, zero-line crosses, and histogram "
            "divergences are the common signals."
        ),
    },
    {
        "term": "Moving Average",
        "category": "Indicator",
        "simple": (
            "A moving average is a smoothed, rolling version of the price that "
            "irons out the daily jitters so you can see the real direction — "
            "like watching the tide instead of every wave. If price is above "
            "its average, the broad trend is up; below, it's down."
        ),
        "technical": (
            "A moving average (MA) is the mean price over a rolling window "
            "(e.g. 20- or 50-day SMA). It acts as dynamic support/resistance. "
            "Crossovers between a short and long MA (e.g. 50 over 200 = 'golden "
            "cross') are classic trend signals. EMAs weight recent prices more."
        ),
    },
    {
        "term": "Breakout",
        "category": "Concepts",
        "simple": (
            "A breakout is when price finally pushes through a 'ceiling' it "
            "kept bumping into (or falls through a 'floor'). Like a crowd "
            "breaking through a barrier — once it gives way, things can move "
            "fast. Breakouts on big volume are the ones to trust."
        ),
        "technical": (
            "A breakout occurs when price moves beyond a defined "
            "support/resistance level or chart-pattern boundary, ideally "
            "accompanied by above-average volume. Without volume confirmation, "
            "breakouts frequently fail ('fakeouts')."
        ),
    },
    {
        "term": "Support",
        "category": "Concepts",
        "simple": (
            "Support is a price 'floor' — a level where buyers have repeatedly "
            "stepped in and stopped the fall, like a trampoline under the "
            "price. It can break, but while it holds, dips tend to bounce "
            "there."
        ),
        "technical": (
            "Support is a price level where demand has historically been "
            "strong enough to halt or reverse a decline. The more times it is "
            "tested and holds, the more significant it is — though repeated "
            "tests can also weaken it."
        ),
    },
    {
        "term": "Resistance",
        "category": "Concepts",
        "simple": (
            "Resistance is a price 'ceiling' — a level where sellers keep "
            "showing up and pushing price back down, like a lid on a jar. "
            "Until price breaks through it, rallies tend to stall there."
        ),
        "technical": (
            "Resistance is a price level where supply has historically been "
            "strong enough to halt or reverse an advance. Once decisively "
            "broken, old resistance often becomes new support (role reversal)."
        ),
    },
    {
        "term": "Stop-Loss",
        "category": "Concepts",
        "simple": (
            "A stop-loss is your SAFETY NET. It's a pre-set price where you "
            "agree to sell and walk away if you're wrong, so one bad trade "
            "can't wipe you out. Decide it BEFORE you buy, while you're calm — "
            "not in a panic after price drops."
        ),
        "technical": (
            "A stop-loss is a pre-defined exit order that caps the loss on a "
            "position. Placement is commonly tied to volatility (e.g. an ATR "
            "multiple) or structure (just beyond support/resistance). It is a "
            "core component of risk management and position sizing."
        ),
    },
]


# ---------------------------------------------------------------------------
# SECTION 2: PATTERNS  (candlestick patterns + chart patterns)
# ---------------------------------------------------------------------------
# Each pattern is a dictionary:
#   "name"        -> the pattern's name.
#   "type"        -> "Candlestick" or "Chart" (used for filtering).
#   "bias"        -> "Bullish" (hints up), "Bearish" (hints down),
#                    or "Neutral" (hints indecision / could go either way).
#   "meaning"     -> plain-English description of what it suggests.
#   "reliability" -> honest note: NOT all patterns are equally trustworthy.
#   "schematic"   -> the SHAPE of the pattern as plain numbers, so the app can
#                    draw a clean little chart of it (real candlesticks / lines)
#                    instead of crude text art. See the format note below.
#
# SCHEMATIC FORMAT (just data — no charting code lives here, so this file stays
# dependency-free and the static tabs work even with no internet):
#
#   For candlestick patterns:
#     {"kind": "candles", "candles": [[open, high, low, close], ...]}
#     Each inner list is ONE candle. The app draws them as proper candlesticks
#     (green when close > open, red when close < open).
#
#   For chart patterns (shapes drawn as a price line):
#     {"kind": "line", "x": [...], "y": [...], "neckline": [x0, x1, y]}
#     "x"/"y" are the points of the price line; the optional "neckline" draws a
#     dashed reference line (used by Head and Shoulders).
#
# The numbers are just an illustrative 0–10-ish scale — only the SHAPE matters.

PATTERNS: list[dict] = [
    {
        "name": "Doji",
        "type": "Candlestick",
        "bias": "Neutral",
        "meaning": (
            "Open and close finish at almost the same price, leaving a tiny "
            "body that looks like a cross or plus sign. It means buyers and "
            "sellers fought to a draw — INDECISION. After a long trend, a doji "
            "can be an early hint that the trend is running out of steam."
        ),
        "reliability": (
            "Medium-low on its own. A doji is a 'pay attention' flag, not a "
            "signal by itself. It's far more useful AFTER a strong move and "
            "when the next candle confirms a turn."
        ),
        # One candle: open and close almost equal (tiny body) with long wicks
        # above and below -> a cross/plus shape.
        "schematic": {
            "kind": "candles",
            "candles": [[5.0, 8.0, 2.0, 5.1]],
        },
    },
    {
        "name": "Hammer",
        "type": "Candlestick",
        "bias": "Bullish",
        "meaning": (
            "A small body sits at the TOP with a long lower wick — like a "
            "hammer. It appears after a fall and shows that sellers pushed "
            "price way down, but buyers slammed it back up by the close. That "
            "rejection of lower prices hints the drop may be ending."
        ),
        "reliability": (
            "Medium. Stronger when it forms at a known support level and when "
            "the next day closes higher to confirm. Weak in isolation."
        ),
        # Small body near the TOP, long lower wick, little/no upper wick.
        "schematic": {
            "kind": "candles",
            "candles": [[7.0, 8.0, 3.0, 7.6]],
        },
    },
    {
        "name": "Shooting Star",
        "type": "Candlestick",
        "bias": "Bearish",
        "meaning": (
            "The mirror image of a hammer: a small body at the BOTTOM with a "
            "long upper wick. It shows up after a rise — buyers shot price up, "
            "but sellers slammed it back down by the close. A warning that the "
            "rally may be tiring."
        ),
        "reliability": (
            "Medium. Most reliable at resistance or after an extended rally, "
            "and when the following candle closes lower."
        ),
        # Small body near the BOTTOM, long upper wick, little/no lower wick.
        "schematic": {
            "kind": "candles",
            "candles": [[4.6, 9.0, 3.7, 4.0]],
        },
    },
    {
        "name": "Bullish Engulfing",
        "type": "Candlestick",
        "bias": "Bullish",
        "meaning": (
            "A small down-day is completely 'swallowed' by a big up-day right "
            "after it — the green body wraps around the previous red body. "
            "Buyers showed up in force and overwhelmed sellers. A common "
            "bottom-reversal hint."
        ),
        "reliability": (
            "Medium-high, especially after a clear downtrend and on strong "
            "volume. Bigger engulfing candle = stronger signal."
        ),
        # Two candles side by side: a small red one, then a big green one whose
        # body fully covers (engulfs) the previous red body.
        "schematic": {
            "kind": "candles",
            "candles": [
                [6.0, 6.3, 4.7, 5.0],   # small red (close < open)
                [4.6, 6.8, 4.3, 6.4],   # big green that engulfs it
            ],
        },
    },
    {
        "name": "Bearish Engulfing",
        "type": "Candlestick",
        "bias": "Bearish",
        "meaning": (
            "The opposite of bullish engulfing: a big red down-day completely "
            "swallows the prior small up-day. Sellers took control. A common "
            "top-reversal hint after a rise."
        ),
        "reliability": (
            "Medium-high after a clear uptrend and on strong volume. The "
            "larger the engulfing candle, the stronger the message."
        ),
        # Two candles side by side: a small green one, then a big red one whose
        # body fully covers (engulfs) the previous green body.
        "schematic": {
            "kind": "candles",
            "candles": [
                [5.0, 6.3, 4.7, 6.0],   # small green (close > open)
                [6.4, 6.8, 4.3, 4.6],   # big red that engulfs it
            ],
        },
    },
    {
        "name": "Cup and Handle",
        "type": "Chart",
        "bias": "Bullish",
        "meaning": (
            "Price makes a smooth, rounded 'U' (the cup) as it recovers from a "
            "dip, then a small downward drift (the handle) before pushing up. "
            "Like a ball settling in a cup and then rolling out the side. A "
            "breakout above the rim often follows."
        ),
        "reliability": (
            "Medium-high when the cup is rounded (not a sharp V) and the "
            "breakout comes on strong volume. A deep, jagged cup is less "
            "reliable."
        ),
        # A rounded "U" (the cup) that recovers to the rim, a small dip (the
        # handle), then a breakout above the rim.
        "schematic": {
            "kind": "line",
            "x": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            "y": [10.0, 9.0, 7.5, 6.3, 5.7, 5.6, 5.9, 6.8, 8.2, 9.8,
                  9.2, 9.0, 11.0],
        },
    },
    {
        "name": "Bull Flag",
        "type": "Chart",
        "bias": "Bullish",
        "meaning": (
            "A sharp run-up (the 'flagpole') followed by a small, tidy drift "
            "downward or sideways (the 'flag') as the move catches its breath. "
            "Often resolves with another push up in the same direction."
        ),
        "reliability": (
            "Medium-high. Best when the flag is short and orderly and the "
            "breakout above it comes on rising volume. A sloppy, long flag is "
            "weaker."
        ),
        # A sharp run-up (the flagpole), a small downward drift (the flag),
        # then a breakout higher.
        "schematic": {
            "kind": "line",
            "x": [0, 1, 2, 3, 4, 5, 6, 7, 8],
            "y": [3.0, 4.6, 6.4, 9.0, 8.6, 8.2, 7.9, 8.1, 10.6],
        },
    },
    {
        "name": "Head and Shoulders",
        "type": "Chart",
        "bias": "Bearish",
        "meaning": (
            "Three peaks: a higher middle peak (the head) between two lower "
            "peaks (the shoulders). When price falls below the 'neckline' "
            "connecting the dips, it often signals a top is in and a "
            "downtrend may follow."
        ),
        "reliability": (
            "High — one of the more respected reversal patterns — BUT only "
            "once the neckline actually breaks, ideally on increased volume. "
            "Before that, it's just three bumps."
        ),
        # Three peaks: left shoulder, a higher head, right shoulder, with a
        # dashed neckline through the two dips and a break below it at the end.
        "schematic": {
            "kind": "line",
            "x": [0, 1, 2, 3, 4, 5, 6],
            "y": [3.0, 6.0, 4.0, 8.0, 4.0, 6.0, 2.5],
            "neckline": [1.0, 5.0, 4.0],
        },
    },
]


# ---------------------------------------------------------------------------
# SECTION 3: QUIZ QUESTIONS
# ---------------------------------------------------------------------------
# We BUILD the quiz automatically from the PATTERNS list above. That way, if
# you add a new pattern, it can show up in the quiz too — no duplicate text.
#
# Each quiz question shows a pattern's diagram + meaning and asks "which pattern
# is this?". The correct answer is the pattern's name; the wrong choices are
# other pattern names of the SAME type (so the quiz isn't trivially easy).


def build_quiz_questions() -> list[dict]:
    """Create one quiz question per pattern.

    Returns a list of dictionaries, each with:
        "schematic"  -> the shape data to draw (same format as in PATTERNS).
        "hint"       -> the plain-English meaning (so the user can reason).
        "answer"     -> the correct pattern name.
        "options"    -> a list of possible names (includes the answer).
        "why"        -> explanation shown after answering.
    """
    import random  # imported here so the rest of the file has no dependencies

    questions: list[dict] = []

    for pattern in PATTERNS:
        # Find other patterns of the SAME type to use as believable wrong
        # answers (e.g. don't offer a chart pattern as a decoy for a candle).
        same_type_names = [
            p["name"] for p in PATTERNS
            if p["type"] == pattern["type"] and p["name"] != pattern["name"]
        ]

        # Pick up to 3 decoys; if there aren't enough of the same type, that's
        # fine — we just use what we have.
        decoys = random.sample(same_type_names, k=min(3, len(same_type_names)))

        options = decoys + [pattern["name"]]
        random.shuffle(options)  # so the answer isn't always last

        questions.append(
            {
                "schematic": pattern["schematic"],
                "hint": pattern["meaning"],
                "answer": pattern["name"],
                "options": options,
                "why": (
                    f"This is a **{pattern['name']}** "
                    f"({pattern['bias'].lower()} bias). {pattern['meaning']} "
                    f"\n\n**Reliability:** {pattern['reliability']}"
                ),
            }
        )

    return questions


# A short, friendly disclaimer reused in the footer of every tab.
DISCLAIMER: str = (
    "**Educational tool only — not financial advice.** Markets are risky and "
    "you can lose money. Patterns and indicators are hints, never guarantees. "
    "Always verify the live price and volume yourself before making any "
    "decision, and never risk money you can't afford to lose."
)
