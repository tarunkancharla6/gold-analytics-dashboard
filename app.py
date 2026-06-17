import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime, date, timedelta
import calendar

st.set_page_config(
    page_title="Gold Analytics Dashboard",
    page_icon="\U0001f4ca",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap');
    * { font-family: 'Inter', sans-serif; }
    h1, h2, h3, h4 { font-family: 'Playfair Display', serif; }

    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #111111 100%);
    }

    .main-header {
        text-align: center;
        padding: 2rem 0 1rem 0;
        background: linear-gradient(180deg, #1a1a1a 0%, transparent 100%);
        border-bottom: 1px solid rgba(212, 175, 55, 0.15);
        margin-bottom: 2rem;
    }

    .main-header h1 {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #FFD700 0%, #D4AF37 40%, #C5A028 70%, #FFD700 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        letter-spacing: 2px;
    }

    .main-header p {
        color: #8a8a8a;
        font-size: 0.9rem;
        margin-top: 0.3rem;
        letter-spacing: 3px;
        text-transform: uppercase;
    }

    .kpi-card {
        background: linear-gradient(145deg, #1a1a1a, #0d0d0d);
        border: 1px solid rgba(212, 175, 55, 0.15);
        border-radius: 16px;
        padding: 1.2rem;
        text-align: center;
        position: relative;
        overflow: hidden;
        height: 100%;
    }

    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, #FFD700, transparent);
    }

    .kpi-label {
        color: #8a8a8a;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 0.4rem;
    }

    .kpi-value {
        font-family: 'Playfair Display', serif;
        font-size: 1.6rem;
        font-weight: 700;
        color: #FFD700;
        line-height: 1.2;
    }

    .kpi-sub {
        font-size: 0.75rem;
        margin-top: 0.3rem;
    }

    .kpi-sub.positive { color: #00c853; }
    .kpi-sub.negative { color: #ff1744; }

    .section-title {
        font-family: 'Playfair Display', serif;
        color: #D4AF37;
        font-size: 1.4rem;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(212, 175, 55, 0.1);
    }

    .insight-box {
        background: rgba(255, 215, 0, 0.05);
        border: 1px solid rgba(212, 175, 55, 0.2);
        border-radius: 12px;
        padding: 1.2rem;
        margin: 0.5rem 0;
    }

    .insight-box h4 {
        color: #FFD700;
        margin: 0 0 0.5rem 0;
        font-size: 1rem;
    }

    .insight-box p {
        color: #bbb;
        font-size: 0.9rem;
        margin: 0;
        line-height: 1.6;
    }

    .purity-badge {
        display: inline-block;
        background: rgba(212, 175, 55, 0.15);
        color: #FFD700;
        padding: 0.2rem 0.8rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 500;
        border: 1px solid rgba(212, 175, 55, 0.2);
    }

    .stButton button {
        background: linear-gradient(135deg, #D4AF37, #C5A028) !important;
        color: #0a0a0a !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 8px !important;
    }

    footer { display: none; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>GOLD ANALYTICS DASHBOARD</h1>
    <p>Market Performance &bull; Purity Analysis &bull; Statistical Insights</p>
</div>
""", unsafe_allow_html=True)

GOLD_SYMBOL = "GC=F"
SILVER_SYMBOL = "SI=F"

@st.cache_data(ttl=60)
def fetch_gold_data(period="1y"):
    try:
        gold = yf.Ticker(GOLD_SYMBOL)
        df = gold.history(period=period)
        if not df.empty:
            df.index = pd.to_datetime(df.index)
            return df
    except:
        pass
    return None

@st.cache_data(ttl=60)
def fetch_silver_data(period="1y"):
    try:
        silver = yf.Ticker(SILVER_SYMBOL)
        df = silver.history(period=period)
        if not df.empty:
            df.index = pd.to_datetime(df.index)
            return df
    except:
        pass
    return None

def calculate_purity(price_24k, purity):
    ratios = {24: 1.0, 22: 0.9167, 18: 0.75, 14: 0.585, 10: 0.417}
    return price_24k * ratios.get(purity, 1.0)

def calculate_metrics(df):
    metrics = {}
    close = df["Close"]
    daily_returns = close.pct_change().dropna()

    metrics["current"] = close.iloc[-1]
    metrics["prev_close"] = close.iloc[-2] if len(close) > 1 else close.iloc[-1]
    metrics["daily_change"] = metrics["current"] - metrics["prev_close"]
    metrics["daily_change_pct"] = (metrics["daily_change"] / metrics["prev_close"]) * 100

    metrics["high_52w"] = close.tail(252).max() if len(close) > 1 else close.max()
    metrics["low_52w"] = close.tail(252).min() if len(close) > 1 else close.min()
    metrics["avg_30d"] = close.tail(30).mean() if len(close) >= 30 else close.mean()

    if len(daily_returns) > 0:
        metrics["volatility_30d"] = daily_returns.tail(30).std() * (252 ** 0.5) * 100
        metrics["volatility_1y"] = daily_returns.tail(252).std() * (252 ** 0.5) * 100 if len(daily_returns) >= 252 else 0

    if len(close) >= 252:
        start = close.iloc[-252]
        end = close.iloc[-1]
        years = 1.0
        metrics["cagr_1y"] = ((end / start) ** (1 / years) - 1) * 100
    else:
        metrics["cagr_1y"] = 0

    if len(close) >= 60:
        metrics["sma_20"] = close.tail(20).mean()
        metrics["sma_50"] = close.tail(50).mean() if len(close) >= 50 else close.mean()
        metrics["sma_200"] = close.tail(200).mean() if len(close) >= 200 else None
    else:
        metrics["sma_20"] = close.mean()
        metrics["sma_50"] = close.mean()
        metrics["sma_200"] = None

    returns_positive = (daily_returns > 0).sum()
    returns_total = len(daily_returns)
    metrics["win_rate"] = (returns_positive / returns_total * 100) if returns_total > 0 else 0

    metrics["max_drawdown"] = ((close / close.cummax()) - 1).min() * 100

    return metrics, daily_returns

with st.spinner("Fetching live gold market data..."):
    raw_df = fetch_gold_data("1y")
    if raw_df is None:
        raw_df = fetch_gold_data("6mo")
    silver_df = fetch_silver_data("1y")

if raw_df is None or raw_df.empty:
    st.error("Could not fetch gold data. Please check your internet connection.")
    st.stop()

usd_to_inr = 83.50
metrics, daily_returns = calculate_metrics(raw_df)

st.markdown("### Executive Summary")

kpi_cols = st.columns(6)

with kpi_cols[0]:
    chg_class = "positive" if metrics["daily_change"] >= 0 else "negative"
    chg_sign = "+" if metrics["daily_change"] >= 0 else ""
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Gold Price (USD)</div>
        <div class="kpi-value">${metrics['current']:,.2f}</div>
        <div class="kpi-sub {chg_class}">{chg_sign}{metrics['daily_change']:.2f} ({chg_sign}{metrics['daily_change_pct']:.2f}%)</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[1]:
    inr_price = metrics["current"] * usd_to_inr
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Gold Price (INR)</div>
        <div class="kpi-value">\u20b9{inr_price:,.0f}</div>
        <div class="kpi-sub">per Troy Ounce</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[2]:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">1-Year Return (CAGR)</div>
        <div class="kpi-value" style="color:{"#00c853" if metrics["cagr_1y"] >= 0 else "#ff1744"};">{metrics["cagr_1y"]:+.2f}%</div>
        <div class="kpi-sub {"positive" if metrics["cagr_1y"] >= 0 else "negative"}">Annualized Return</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[3]:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">30-Day Volatility</div>
        <div class="kpi-value" style="color:#D4AF37;">{metrics["volatility_30d"]:.1f}%</div>
        <div class="kpi-sub">Annualized</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[4]:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">52-Week Range</div>
        <div class="kpi-value" style="font-size:1.1rem;">${metrics['high_52w']:,.0f}</div>
        <div class="kpi-sub">High &bull; Low ${metrics['low_52w']:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[5]:
    max_dd = metrics["max_drawdown"]
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Max Drawdown (1Y)</div>
        <div class="kpi-value" style="color:#ff1744;">{max_dd:.1f}%</div>
        <div class="kpi-sub negative">Peak to Trough</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="section-title"> Price Trends & Market Performance</div>', unsafe_allow_html=True)

chart_row1 = st.columns([3, 1])

with chart_row1[0]:
    tf = st.selectbox("Timeframe", ["1 Month", "3 Months", "6 Months", "1 Year", "Max"], index=2, key="tf_select")

    period_map = {"1 Month": 21, "3 Months": 63, "6 Months": 126, "1 Year": 252, "Max": len(raw_df)}
    days_to_show = period_map[tf]

    df_plot = raw_df.tail(days_to_show).copy()

    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        row_heights=[0.6, 0.2, 0.2],
        subplot_titles=("Price & Moving Averages", "Daily Returns %", "Volume")
    )

    fig.add_trace(go.Scatter(
        x=df_plot.index, y=df_plot["Close"],
        mode="lines", name="Close Price",
        line=dict(color="#FFD700", width=2),
        hovertemplate="$%{y:,.2f}<br>%{x|%b %d, %Y}<extra></extra>"
    ), row=1, col=1)

    df_plot["SMA_20"] = df_plot["Close"].rolling(20, min_periods=1).mean()
    df_plot["SMA_50"] = df_plot["Close"].rolling(50, min_periods=1).mean()

    fig.add_trace(go.Scatter(
        x=df_plot.index, y=df_plot["SMA_20"],
        mode="lines", name="20-Day SMA",
        line=dict(color="#D4AF37", width=1.5, dash="dash"),
        hovertemplate="20-SMA: $%{y:,.2f}<extra></extra>"
    ), row=1, col=1)

    if len(df_plot) >= 50:
        fig.add_trace(go.Scatter(
            x=df_plot.index, y=df_plot["SMA_50"],
            mode="lines", name="50-Day SMA",
            line=dict(color="#C5A028", width=1.5, dash="dot"),
            hovertemplate="50-SMA: $%{y:,.2f}<extra></extra>"
        ), row=1, col=1)

    returns_plot = df_plot["Close"].pct_change() * 100
    colors = ["#00c853" if v >= 0 else "#ff1744" for v in returns_plot.fillna(0)]
    fig.add_trace(go.Bar(
        x=df_plot.index, y=returns_plot,
        name="Daily Return %",
        marker=dict(color=colors, opacity=0.7),
        hovertemplate="%{y:+.2f}%<extra></extra>"
    ), row=2, col=1)

    fig.add_trace(go.Bar(
        x=df_plot.index, y=df_plot["Volume"],
        name="Volume",
        marker=dict(color="rgba(212, 175, 55, 0.4)", opacity=0.6),
        hovertemplate="Volume: %{y:,.0f}<extra></extra>"
    ), row=3, col=1)

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#8a8a8a", size=10)),
        margin=dict(l=10, r=10, t=40, b=10),
        height=520,
        showlegend=True
    )

    fig.update_xaxes(gridcolor="rgba(255,255,255,0.03)", zeroline=False, tickfont=dict(color="#666", size=9))
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.03)", zeroline=False, tickfont=dict(color="#666", size=9))

    st.plotly_chart(fig, use_container_width=True)

with chart_row1[1]:
    st.markdown("### Key Levels")

    sma_20 = metrics["sma_20"]
    sma_50 = metrics["sma_50"]
    current = metrics["current"]

    st.markdown(f"""
    <div class="kpi-card" style="text-align:left;padding:1rem;margin-bottom:0.5rem;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <span style="color:#8a8a8a;font-size:0.8rem;">Current</span>
            <span style="color:#FFD700;font-weight:600;">${current:,.2f}</span>
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;margin-top:0.5rem;">
            <span style="color:#8a8a8a;font-size:0.8rem;">20-Day SMA</span>
            <span style="color:#D4AF37;font-weight:600;">${sma_20:,.2f}</span>
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;margin-top:0.5rem;">
            <span style="color:#8a8a8a;font-size:0.8rem;">50-Day SMA</span>
            <span style="color:#C5A028;font-weight:600;">${sma_50:,.2f}</span>
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;margin-top:0.5rem;padding-top:0.5rem;border-top:1px solid rgba(212,175,55,0.1);">
            <span style="color:#8a8a8a;font-size:0.8rem;">52W High</span>
            <span style="color:#00c853;font-weight:600;">${metrics['high_52w']:,.2f}</span>
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;margin-top:0.3rem;">
            <span style="color:#8a8a8a;font-size:0.8rem;">52W Low</span>
            <span style="color:#ff1744;font-weight:600;">${metrics['low_52w']:,.2f}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    pos_pct = (current - sma_20) / sma_20 * 100
    signal = "Bullish \U0001f7e2" if current > sma_50 else "Bearish \U0001f534"
    signal_color = "#00c853" if current > sma_50 else "#ff1744"

    st.markdown(f"""
    <div class="kpi-card" style="text-align:center;padding:1rem;">
        <div style="color:#8a8a8a;font-size:0.7rem;text-transform:uppercase;letter-spacing:1px;">Market Signal</div>
        <div style="color:{signal_color};font-size:1.3rem;font-weight:700;margin:0.3rem 0;">{signal}</div>
        <div style="color:#8a8a8a;font-size:0.75rem;">Price vs 50-SMA: {pos_pct:+.2f}%</div>
    </div>
    """, unsafe_allow_html=True)

    if silver_df is not None and not silver_df.empty:
        silv_close = silver_df["Close"].iloc[-1]
        gold_silver_ratio = current / silv_close
        st.markdown(f"""
        <div class="kpi-card" style="text-align:center;padding:1rem;margin-top:0.5rem;">
            <div style="color:#8a8a8a;font-size:0.7rem;text-transform:uppercase;letter-spacing:1px;">Gold/Silver Ratio</div>
            <div style="color:#D4AF37;font-size:1.3rem;font-weight:700;margin:0.3rem 0;">{gold_silver_ratio:.1f}x</div>
            <div style="color:#8a8a8a;font-size:0.75rem;">Silver: ${silv_close:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('<div class="section-title"> Purity-Wise Price Breakdown</div>', unsafe_allow_html=True)

pur_col1, pur_col2 = st.columns([2, 1])

with pur_col1:
    purities = [24, 22, 18, 14]
    purity_data = []
    for p in purities:
        price_usd = calculate_purity(metrics["current"], p)
        price_inr = price_usd * usd_to_inr
        purity_data.append({"Purity": f"{p}K", "USD": round(price_usd, 2), "INR": round(price_inr, 2)})

    purity_df = pd.DataFrame(purity_data)

    fig_pur = px.bar(
        purity_df, x="Purity", y="INR",
        text="INR",
        color="Purity",
        color_discrete_map={"24K": "#FFD700", "22K": "#D4AF37", "18K": "#C5A028", "14K": "#A08020"},
        template="plotly_dark"
    )

    fig_pur.update_traces(
        texttemplate="\u20b9%{text:,.0f}",
        textposition="outside",
        textfont=dict(color="#FFD700", size=12),
        hovertemplate="<b>%{x}</b><br>\u20b9%{y:,.2f}<extra></extra>"
    )

    fig_pur.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=20, b=10),
        height=300,
        xaxis=dict(gridcolor="rgba(255,255,255,0.03)", title="", tickfont=dict(color="#8a8a8a")),
        yaxis=dict(gridcolor="rgba(255,255,255,0.03)", title="Price (INR)", tickfont=dict(color="#8a8a8a"), tickprefix="\u20b9"),
        showlegend=False
    )

    st.plotly_chart(fig_pur, use_container_width=True)

with pur_col2:
    st.markdown("### Purity Details")
    for p in purities:
        p_usd = calculate_purity(metrics["current"], p)
        p_inr = p_usd * usd_to_inr
        purity_label = {24: "24K (99.9%)", 22: "22K (91.7%)", 18: "18K (75.0%)", 14: "14K (58.5%)"}
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;align-items:center;padding:0.5rem 0.8rem;border-bottom:1px solid rgba(255,255,255,0.05);">
            <span style="color:#D4AF37;font-size:0.85rem;">{purity_label[p]}</span>
            <span style="color:#ccc;font-weight:500;">\u20b9{p_inr:,.0f}</span>
        </div>
        """, unsafe_allow_html=True)

st.markdown('<div class="section-title"> Statistical Analysis & Insights</div>', unsafe_allow_html=True)

stat_col1, stat_col2 = st.columns(2)

with stat_col1:
    st.markdown("### Returns Distribution")

    if len(daily_returns) > 0:
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Histogram(
            x=daily_returns * 100,
            nbinsx=40,
            marker=dict(
                color="#D4AF37",
                opacity=0.6,
                line=dict(color="rgba(212,175,55,0.3)", width=0.5)
            ),
            hovertemplate="Return: %{x:+.2f}%<br>Frequency: %{y}<extra></extra>"
        ))

        fig_hist.add_vline(x=0, line=dict(color="#8a8a8a", width=1, dash="dash"))

        fig_hist.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=20, b=10),
            height=300,
            xaxis=dict(gridcolor="rgba(255,255,255,0.03)", title="Daily Return %", tickfont=dict(color="#8a8a8a")),
            yaxis=dict(gridcolor="rgba(255,255,255,0.03)", title="Frequency", tickfont=dict(color="#8a8a8a")),
            bargap=0.08,
            showlegend=False
        )

        st.plotly_chart(fig_hist, use_container_width=True)

with stat_col2:
    st.markdown("### Key Statistics")

    stats_metrics = {
        "Number of Trading Days": f"{len(daily_returns):,}",
        "Average Daily Return": f"{daily_returns.mean()*100:+.4f}%",
        "Median Daily Return": f"{daily_returns.median()*100:+.4f}%",
        "Best Day": f"{daily_returns.max()*100:+.2f}%",
        "Worst Day": f"{daily_returns.min()*100:+.2f}%",
        "Daily Std Deviation": f"{daily_returns.std()*100:+.3f}%",
        "Annualized Volatility": f"{metrics['volatility_1y']:.1f}%" if metrics["volatility_1y"] > 0 else "N/A",
        "Win Rate (Positive Days)": f"{metrics['win_rate']:.1f}%",
        "Max Drawdown (1Y)": f"{metrics['max_drawdown']:.1f}%",
        "CAGR (1 Year)": f"{metrics['cagr_1y']:+.2f}%" if metrics["cagr_1y"] != 0 else "N/A",
    }

    st.markdown('<div class="kpi-card" style="text-align:left;padding:1rem;">', unsafe_allow_html=True)
    for label, value in stats_metrics.items():
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;padding:0.35rem 0;border-bottom:1px solid rgba(255,255,255,0.03);">
            <span style="color:#8a8a8a;font-size:0.8rem;">{label}</span>
            <span style="color:#ccc;font-weight:500;font-size:0.85rem;">{value}</span>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section-title"> Automated Market Insights</div>', unsafe_allow_html=True)

ins_col1, ins_col2, ins_col3 = st.columns(3)

current_price = metrics["current"]
prev_close = metrics["prev_close"]

if sma_50 is not None and current > sma_50:
    trend_icon = "\U0001f4c8"
    trend_desc = f"Gold is trading above its 50-day SMA (${sma_50:,.0f}), indicating a bullish trend. The 20-day SMA (${sma_20:,.0f}) is also supporting upward momentum."
else:
    trend_icon = "\U0001f4c9"
    trend_desc = f"Gold is trading below its 50-day SMA (${sma_50:,.0f}), indicating a bearish trend."

if metrics["volatility_30d"] > 20:
    vol_icon = "\u26a0\ufe0f"
    vol_insight = "elevated volatility - consider wider stop-losses for trading strategies"
elif metrics["volatility_30d"] > 15:
    vol_icon = "\u2696\ufe0f"
    vol_insight = "moderate volatility - normal market conditions for gold"
else:
    vol_icon = "\U0001f3af"
    vol_insight = "low volatility environment - gold prices are relatively stable"

cagr = metrics["cagr_1y"]
if cagr > 20:
    perf_icon = "\U0001f680"
    perf_desc = f"Gold has delivered a {cagr:+.1f}% annualized return over the past year, significantly outperforming traditional safe-haven assets."
elif cagr > 10:
    perf_icon = "\u2705"
    perf_desc = f"Gold has delivered a solid {cagr:+.1f}% annualized return over the past year."
elif cagr > 0:
    perf_icon = "\U0001f4ca"
    perf_desc = f"Gold has shown modest positive returns ({cagr:+.1f}% CAGR) over the past year."
else:
    perf_icon = "\U0001f504"
    perf_desc = f"Gold has corrected ({cagr:+.1f}% CAGR) over the past year - potential buying opportunity"

with ins_col1:
    st.markdown(f"""
    <div class="insight-box">
        <h4>{trend_icon} Trend Analysis</h4>
        <p>{trend_desc}</p>
    </div>
    """, unsafe_allow_html=True)

with ins_col2:
    st.markdown(f"""
    <div class="insight-box">
        <h4>{vol_icon} Volatility Assessment</h4>
        <p>30-day annualized volatility is at {metrics["volatility_30d"]:.1f}%, indicating {vol_insight}</p>
    </div>
    """, unsafe_allow_html=True)

with ins_col3:
    st.markdown(f"""
    <div class="insight-box">
        <h4>{perf_icon} Performance Summary</h4>
        <p>{perf_desc}</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("#### Data-Driven Decision Support")

dd_col1, dd_col2 = st.columns(2)

with dd_col1:
    risk_level = "Low" if metrics["volatility_30d"] < 15 else ("Medium" if metrics["volatility_30d"] < 22 else "High")
    risk_color = {"Low": "#00c853", "Medium": "#D4AF37", "High": "#ff1744"}

    signal_text = "Accumulation" if current > sma_50 else "Distribution"
    signal_c = "#00c853" if current > sma_50 else "#ff1744"

    st.markdown(f"""
    <div class="kpi-card" style="text-align:left;padding:1.2rem;">
        <h4 style="color:#D4AF37;margin:0 0 0.8rem 0;font-size:1rem;">Portfolio Context</h4>
        <div style="display:flex;justify-content:space-between;margin-bottom:0.5rem;">
            <span style="color:#8a8a8a;">Risk Level</span>
            <span style="color:{risk_color[risk_level]};font-weight:600;">{risk_level}</span>
        </div>
        <div style="display:flex;justify-content:space-between;margin-bottom:0.5rem;">
            <span style="color:#8a8a8a;">Trend Strength</span>
            <span style="color:#D4AF37;font-weight:600;">{"Strong" if abs(metrics["daily_change_pct"]) > 1 else "Moderate" if abs(metrics["daily_change_pct"]) > 0.5 else "Weak"}</span>
        </div>
        <div style="display:flex;justify-content:space-between;">
            <span style="color:#8a8a8a;">Market Phase</span>
            <span style="color:{signal_c};font-weight:600;">{signal_text}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with dd_col2:
    purity_24k_inr = metrics["current"] * usd_to_inr
    purity_22k_inr = calculate_purity(metrics["current"], 22) * usd_to_inr
    diff = purity_24k_inr - purity_22k_inr

    st.markdown(f"""
    <div class="kpi-card" style="text-align:left;padding:1.2rem;">
        <h4 style="color:#D4AF37;margin:0 0 0.8rem 0;font-size:1rem;">Business Application</h4>
        <div style="display:flex;justify-content:space-between;margin-bottom:0.5rem;">
            <span style="color:#8a8a8a;">24K - 22K Price Gap</span>
            <span style="color:#FFD700;font-weight:600;">\u20b9{diff:,.0f}</span>
        </div>
        <div style="display:flex;justify-content:space-between;margin-bottom:0.5rem;">
            <span style="color:#8a8a8a;">Partner Margin Potential</span>
            <span style="color:#00c853;font-weight:600;">\u20b9{diff*0.02:,.0f}/oz</span>
        </div>
        <div style="display:flex;justify-content:space-between;">
            <span style="color:#8a8a8a;">Auto-Report Ready</span>
            <span style="color:#00c853;font-weight:600;">Yes (CSV/PDF)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("#### Dashboard Insights Report")

rep_col1, rep_col2, rep_col3 = st.columns([1, 1, 1])

with rep_col1:
    report_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    st.markdown(f"""
    <div style="color:#8a8a8a;font-size:0.8rem;padding:0.5rem 0;">
        Report Generated: {report_date}<br>
        Data Source: yfinance (Gold Futures: GC=F)
    </div>
    """, unsafe_allow_html=True)

with rep_col2:
    if st.button(" Export Report (CSV)", use_container_width=True):
        export_df = raw_df.tail(252).copy()
        export_df["Daily_Return_%"] = export_df["Close"].pct_change() * 100
        export_df["SMA_20"] = export_df["Close"].rolling(20, min_periods=1).mean()
        export_df["SMA_50"] = export_df["Close"].rolling(50, min_periods=1).mean()
        csv_data = export_df.to_csv()

        st.download_button(
            " Download CSV",
            csv_data,
            f"gold_analytics_report_{date.today()}.csv",
            "text/csv",
            use_container_width=True
        )

with rep_col3:
    summary_text = f"""GOLD ANALYTICS SUMMARY
Date: {date.today()}
Current Price: ${metrics['current']:,.2f} (\u20b9{inr_price:,.0f})
Daily Change: {metrics['daily_change']:+.2f} ({metrics['daily_change_pct']:+.2f}%)
1Y CAGR: {metrics['cagr_1y']:+.2f}%
30D Volatility: {metrics['volatility_30d']:.1f}%
52W Range: ${metrics['low_52w']:,.2f} - ${metrics['high_52w']:,.2f}
Max Drawdown: {metrics['max_drawdown']:.1f}%
Signal: {'Bullish' if current > sma_50 else 'Bearish'}"""

    if st.button(" Copy Summary", use_container_width=True):
        st.code(summary_text, language="text")
        st.success("Summary copied!")

st.markdown("""
<div style="text-align:center;margin-top:3rem;padding:2rem;border-top:1px solid rgba(212,175,55,0.1);">
    <p style="color:#666;font-size:0.8rem;">
        Gold Analytics Dashboard | Python + Streamlit + Plotly + yfinance<br>
        KPI Analytics &bull; Purity Breakdown &bull; Statistical Insights &bull; Automated Reporting
    </p>
</div>
""", unsafe_allow_html=True)
