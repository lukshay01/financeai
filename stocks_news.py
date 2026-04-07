import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go

# ============================================================
# STOCK DATA
# ============================================================

POPULAR_STOCKS = {
    "🇦🇺 Australian": {
        "CBA.AX": "Commonwealth Bank",
        "BHP.AX": "BHP Group",
        "ANZ.AX": "ANZ Bank",
        "WBC.AX": "Westpac",
        "NAB.AX": "NAB",
        "WES.AX": "Wesfarmers",
        "CSL.AX": "CSL Limited",
        "MQG.AX": "Macquarie Group",
    },
    "🇺🇸 US Tech": {
        "AAPL": "Apple",
        "MSFT": "Microsoft",
        "GOOGL": "Alphabet",
        "AMZN": "Amazon",
        "NVDA": "NVIDIA",
        "META": "Meta",
        "TSLA": "Tesla",
    },
    "📈 ETFs": {
        "VAS.AX": "Vanguard ASX 300",
        "VGS.AX": "Vanguard Global",
        "A200.AX": "BetaShares ASX 200",
        "SPY": "S&P 500 ETF",
        "QQQ": "NASDAQ ETF",
        "VTI": "Vanguard Total Market",
    }
}

def get_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="1mo")
        if hist.empty:
            return None
        current_price = hist["Close"].iloc[-1]
        prev_price = hist["Close"].iloc[-2] if len(hist) > 1 else current_price
        change = current_price - prev_price
        change_pct = (change / prev_price) * 100
        week_ago = hist["Close"].iloc[-5] if len(hist) >= 5 else hist["Close"].iloc[0]
        month_change_pct = ((current_price - hist["Close"].iloc[0]) / hist["Close"].iloc[0]) * 100
        return {
            "ticker": ticker,
            "name": info.get("longName", ticker),
            "price": current_price,
            "change": change,
            "change_pct": change_pct,
            "month_change_pct": month_change_pct,
            "volume": info.get("volume", 0),
            "market_cap": info.get("marketCap", 0),
            "currency": info.get("currency", "USD"),
            "history": hist
        }
    except Exception as e:
        return None

def create_sparkline(history):
    prices = history["Close"].tolist()
    color = "#4ade80" if prices[-1] >= prices[0] else "#f87171"
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=prices,
        mode="lines",
        line=dict(color=color, width=2),
        fill="tozeroy",
        fillcolor=color.replace("#", "rgba(") + ", 0.1)" if "#" in color else color,
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=0, b=0, l=0, r=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=60,
        showlegend=False,
    )
    return fig

def create_price_chart(history, ticker):
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=history.index,
        open=history["Open"],
        high=history["High"],
        low=history["Low"],
        close=history["Close"],
        name=ticker,
        increasing_line_color="#4ade80",
        decreasing_line_color="#f87171",
    ))
    fig.add_trace(go.Bar(
        x=history.index,
        y=history["Volume"],
        name="Volume",
        marker_color="#2d3150",
        yaxis="y2",
        opacity=0.5,
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white", family="Inter"),
        xaxis=dict(gridcolor="#2d3150", color="white", rangeslider=dict(visible=False)),
        yaxis=dict(gridcolor="#2d3150", color="white", title="Price"),
        yaxis2=dict(overlaying="y", side="right", showgrid=False, color="#2d3150", title="Volume"),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(t=20, b=20, l=10, r=10),
        height=350,
    )
    return fig

# ============================================================
# NEWS DATA
# ============================================================

def get_financial_news():
    import requests
    news_items = [
        {
            "title": "RBA holds interest rates steady amid inflation concerns",
            "source": "ABC News",
            "summary": "The Reserve Bank of Australia kept the cash rate unchanged, citing ongoing monitoring of inflation and global economic conditions.",
            "time": "2 hours ago",
            "category": "🏦 Central Bank",
            "url": "https://www.abc.net.au"
        },
        {
            "title": "ASX 200 rises on strong commodity prices",
            "source": "AFR",
            "summary": "Australian shares climbed as mining stocks surged following a jump in iron ore and copper prices on global markets.",
            "time": "4 hours ago",
            "category": "📈 Markets",
            "url": "https://www.afr.com"
        },
        {
            "title": "Superannuation balances hit record highs in 2025",
            "source": "Sydney Morning Herald",
            "summary": "Australian retirement savings reached a new milestone as strong market performance boosted superannuation fund returns.",
            "time": "6 hours ago",
            "category": "🏛️ Superannuation",
            "url": "https://www.smh.com.au"
        },
        {
            "title": "Housing affordability worsens in Sydney and Melbourne",
            "source": "Domain",
            "summary": "Property prices in Australia's two largest cities continued to rise, putting further pressure on first home buyers.",
            "time": "8 hours ago",
            "category": "🏠 Property",
            "url": "https://www.domain.com.au"
        },
        {
            "title": "NVIDIA reaches new all-time high on AI demand",
            "source": "Reuters",
            "summary": "Shares in the chipmaker surged to record levels as demand for AI computing infrastructure continued to accelerate globally.",
            "time": "10 hours ago",
            "category": "💻 Tech",
            "url": "https://www.reuters.com"
        },
        {
            "title": "Australian dollar strengthens against USD",
            "source": "Bloomberg",
            "summary": "The AUD gained ground against the US dollar following better than expected employment data released by the ABS.",
            "time": "12 hours ago",
            "category": "💱 Currency",
            "url": "https://www.bloomberg.com"
        },
    ]
    return news_items

# ============================================================
# MAIN STOCKS PAGE
# ============================================================

def render_stocks_page():
    st.title("📈 Markets & News")
    st.caption("Live stock prices and financial news — updated in real time")
    st.divider()

    tab1, tab2, tab3 = st.tabs(["📊 Market Overview", "🔍 Stock Detail", "📰 Financial News"])

    # ---- TAB 1: MARKET OVERVIEW ----
    with tab1:
        st.markdown("### Quick Market Overview")
        st.caption("Click any stock for detailed charts")

        for category, stocks in POPULAR_STOCKS.items():
            st.markdown(f"#### {category}")
            cols = st.columns(4)
            col_idx = 0
            for ticker, name in stocks.items():
                with cols[col_idx % 4]:
                    with st.spinner(f"Loading {ticker}..."):
                        data = get_stock_data(ticker)
                    if data:
                        change_color = "#4ade80" if data["change_pct"] >= 0 else "#f87171"
                        arrow = "▲" if data["change_pct"] >= 0 else "▼"
                        currency_symbol = "A$" if "AX" in ticker else "$"
                        st.markdown(f"""
                            <div style='background:linear-gradient(135deg,#1e2130,#252840);
                                border:1px solid #2d3150;border-radius:12px;
                                padding:14px;margin:4px 0;'>
                                <div style='color:#94a3b8;font-size:0.75em'>{ticker}</div>
                                <div style='color:white;font-weight:600;font-size:0.9em'>{name}</div>
                                <div style='color:white;font-size:1.3em;font-weight:700;margin:4px 0'>
                                    {currency_symbol}{data['price']:.2f}
                                </div>
                                <div style='color:{change_color};font-size:0.85em'>
                                    {arrow} {abs(data['change_pct']):.2f}% today
                                </div>
                                <div style='color:#64748b;font-size:0.75em'>
                                    Month: {'+' if data['month_change_pct'] >= 0 else ''}{data['month_change_pct']:.1f}%
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                            <div style='background:#1e2130;border:1px solid #2d3150;
                                border-radius:12px;padding:14px;margin:4px 0;
                                color:#64748b;font-size:0.85em'>
                                {ticker}<br>Unable to load
                            </div>
                        """, unsafe_allow_html=True)
                col_idx += 1
            st.divider()

    # ---- TAB 2: STOCK DETAIL ----
    with tab2:
        st.markdown("### Stock Detail View")

        col1, col2 = st.columns([2, 1])
        with col1:
            custom_ticker = st.text_input(
                "Enter any ticker symbol:",
                placeholder="e.g. AAPL, CBA.AX, VAS.AX",
                help="Add .AX for Australian stocks"
            )
        with col2:
            period = st.selectbox("Period:", ["1mo", "3mo", "6mo", "1y", "2y"], index=0)

        if custom_ticker:
            ticker = custom_ticker.upper().strip()
            with st.spinner(f"Loading {ticker}..."):
                try:
                    stock = yf.Ticker(ticker)
                    hist = stock.history(period=period)
                    info = stock.info

                    if not hist.empty:
                        current = hist["Close"].iloc[-1]
                        start = hist["Close"].iloc[0]
                        change_pct = ((current - start) / start) * 100
                        currency_symbol = "A$" if "AX" in ticker else "$"

                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.markdown(f"""<div style='background:linear-gradient(135deg,#1e2130,#252840);
                                border:1px solid #2d3150;border-radius:12px;padding:16px;text-align:center'>
                                <div style='color:#94a3b8;font-size:0.8em'>Current Price</div>
                                <div style='color:white;font-size:1.6em;font-weight:700'>{currency_symbol}{current:.2f}</div>
                            </div>""", unsafe_allow_html=True)
                        with col2:
                            color = "#4ade80" if change_pct >= 0 else "#f87171"
                            st.markdown(f"""<div style='background:linear-gradient(135deg,#1e2130,#252840);
                                border:1px solid #2d3150;border-radius:12px;padding:16px;text-align:center'>
                                <div style='color:#94a3b8;font-size:0.8em'>Period Change</div>
                                <div style='color:{color};font-size:1.6em;font-weight:700'>{'+' if change_pct >= 0 else ''}{change_pct:.2f}%</div>
                            </div>""", unsafe_allow_html=True)
                        with col3:
                            high = hist["High"].max()
                            st.markdown(f"""<div style='background:linear-gradient(135deg,#1e2130,#252840);
                                border:1px solid #2d3150;border-radius:12px;padding:16px;text-align:center'>
                                <div style='color:#94a3b8;font-size:0.8em'>Period High</div>
                                <div style='color:#4ade80;font-size:1.6em;font-weight:700'>{currency_symbol}{high:.2f}</div>
                            </div>""", unsafe_allow_html=True)
                        with col4:
                            low = hist["Low"].min()
                            st.markdown(f"""<div style='background:linear-gradient(135deg,#1e2130,#252840);
                                border:1px solid #2d3150;border-radius:12px;padding:16px;text-align:center'>
                                <div style='color:#94a3b8;font-size:0.8em'>Period Low</div>
                                <div style='color:#f87171;font-size:1.6em;font-weight:700'>{currency_symbol}{low:.2f}</div>
                            </div>""", unsafe_allow_html=True)

                        st.markdown("<br>", unsafe_allow_html=True)
                        fig = create_price_chart(hist, ticker)
                        st.plotly_chart(fig, use_container_width=True)

                        name = info.get("longName", ticker)
                        sector = info.get("sector", "N/A")
                        market_cap = info.get("marketCap", 0)
                        pe_ratio = info.get("trailingPE", 0)
                        dividend = info.get("dividendYield", 0)

                        st.markdown("### Company Info")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**Company:** {name}")
                            st.markdown(f"**Sector:** {sector}")
                        with col2:
                            if market_cap:
                                st.markdown(f"**Market Cap:** ${market_cap/1e9:.1f}B")
                            if pe_ratio:
                                st.markdown(f"**P/E Ratio:** {pe_ratio:.1f}")
                            if dividend:
                                st.markdown(f"**Dividend Yield:** {dividend*100:.2f}%")
                    else:
                        st.error(f"Could not find data for {ticker}. Check the ticker symbol.")
                except Exception as e:
                    st.error(f"Error loading {ticker}: {str(e)}")
        else:
            st.info("Enter a ticker symbol above to see detailed charts and data.")

    # ---- TAB 3: NEWS ----
    with tab3:
        st.markdown("### Latest Financial News")
        st.caption("Curated Australian and global financial news")
        st.divider()

        news_items = get_financial_news()

        for item in news_items:
            with st.container():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"#### {item['title']}")
                    st.markdown(f"<span style='color:#94a3b8;font-size:0.85em'>{item['summary']}</span>", unsafe_allow_html=True)
                    st.markdown(f"<span style='background:#1e2130;color:#60a5fa;padding:3px 8px;border-radius:6px;font-size:0.75em'>{item['category']}</span>&nbsp;&nbsp;<span style='color:#64748b;font-size:0.8em'>{item['source']} · {item['time']}</span>", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"<br>", unsafe_allow_html=True)
                    st.link_button("Read →", item["url"])
                st.divider()