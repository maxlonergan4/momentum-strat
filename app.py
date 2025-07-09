import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import date, timedelta

# Page config: title and icon
st.set_page_config(
    page_title="Momentum Strategy Dashboard",
    page_icon="📈",
    layout="wide",
)

# --- Style tweaks with markdown ---
st.markdown("""
    <style>
    .main {
        background-color: #f5f7fa;
        color: #111;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stButton>button {
        background-color: #0072C6;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        padding: 0.4em 1.2em;
    }
    .stSlider>div>div>input {
        accent-color: #0072C6;
    }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.title("🚀 Momentum Strategy Dashboard")
st.markdown("Built with Python, Streamlit & yfinance")

# Sidebar inputs
with st.sidebar:
    st.header("Settings")

    ticker = st.text_input("Stock Ticker", "AAPL", help="Enter a valid stock symbol (e.g., AAPL, MSFT, TSLA)").upper()

    st.markdown("### Moving Average Settings")
    short_window = st.slider("Short-Term SMA (days)", 5, 50, 20, help="Shorter period moving average window")
    long_window = st.slider("Long-Term SMA (days)", 20, 200, 50, help="Longer period moving average window")

    st.markdown("### Date Range")
    today = date.today()
    default_start = today - timedelta(days=365)
    start_date = st.date_input("Start Date", default_start, min_value=date(2000,1,1), max_value=today)
    end_date = st.date_input("End Date", today, min_value=start_date, max_value=today)

# Fetch company info function with caching
@st.cache_data
def get_company_info(ticker):
    try:
        info = yf.Ticker(ticker).info
        return {
            "Name": info.get("longName", "N/A"),
            "Sector": info.get("sector", "N/A"),
            "Market Cap": info.get("marketCap", "N/A"),
            "PE Ratio": info.get("trailingPE", "N/A"),
            "Beta": info.get("beta", "N/A"),
            "Dividend Yield": info.get("dividendYield", "N/A")
        }
    except Exception:
        return None

# Fetch price data with caching
@st.cache_data
def get_data(ticker, start, end):
    data = yf.download(ticker, start=start, end=end, progress=False)
    data.columns = data.columns.get_level_values(0)
    return data

# Main app logic
if ticker:
    df = get_data(ticker, start_date, end_date)
    company_info = get_company_info(ticker)

    if df.empty:
        st.warning("⚠️ No data found for this ticker or date range. Please adjust inputs.")
    else:
        # Company info display in columns
        if company_info:
            st.markdown("### 🏢 Company Profile & Key Stats")
            col1, col2, col3 = st.columns(3)
            col1.write(f"**Name:** {company_info['Name']}")
            col1.write(f"**Sector:** {company_info['Sector']}")
            col2.write(f"**Market Cap:** {company_info['Market Cap']:,}" if company_info['Market Cap'] != "N/A" else "**Market Cap:** N/A")
            col2.write(f"**P/E Ratio:** {company_info['PE Ratio']}")
            col3.write(f"**Beta:** {company_info['Beta']}")
            dividend_yield = company_info['Dividend Yield']
            col3.write(f"**Dividend Yield:** {dividend_yield*100:.2f}%" if dividend_yield else "**Dividend Yield:** N/A")

        # Calculate indicators
        df[f'{short_window}_SMA'] = df['Close'].rolling(window=short_window).mean()
        df[f'{long_window}_SMA'] = df['Close'].rolling(window=long_window).mean()
        df['Volume_MA'] = df['Volume'].rolling(window=20).mean()

        # Generate signals
        df['Signal'] = 0
        buy_condition = (df[f'{short_window}_SMA'] > df[f'{long_window}_SMA']) & (df['Volume'] > df['Volume_MA'])
        sell_condition = (df[f'{short_window}_SMA'] < df[f'{long_window}_SMA'])
        df.loc[buy_condition, 'Signal'] = 1
        df.loc[sell_condition, 'Signal'] = -1
        df['Position'] = df['Signal'].diff()

        # Plot chart with signals
        st.markdown("### 📈 Price Chart with Buy/Sell Signals")
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(df.index, df['Close'], label='Close Price', color='#111111')
        ax.plot(df.index, df[f'{short_window}_SMA'], label=f'{short_window}-day SMA', color='#0072C6')
        ax.plot(df.index, df[f'{long_window}_SMA'], label=f'{long_window}-day SMA', color='#E85C41')

        buy_signals = df[df['Position'] == 2]
        sell_signals = df[df['Position'] == -2]
        ax.scatter(buy_signals.index, buy_signals['Close'], marker='^', color='green', label='Buy', s=100)
        ax.scatter(sell_signals.index, sell_signals['Close'], marker='v', color='red', label='Sell', s=100)

        ax.set_title(f"{ticker} Price & SMA Buy/Sell Signals with Volume Filter", fontsize=16, fontweight='bold')
        ax.legend()
        ax.grid(alpha=0.3)
        st.pyplot(fig)

        # Backtest calculations
        df['Daily Return'] = df['Close'].pct_change()
        df['Strategy Return'] = df['Daily Return'] * (df['Signal'].shift(1) == 1)
        initial_value = 10000
        df['Strategy Equity'] = initial_value * (1 + df['Strategy Return']).cumprod()
        df['BuyHold Equity'] = initial_value * (1 + df['Daily Return']).cumprod()
        final_strategy = df['Strategy Equity'].iloc[-1]
        final_hold = df['BuyHold Equity'].iloc[-1]

        # Backtest results and chart
        st.markdown("### 📊 Backtest Results (Starting with $10,000)")
        col1, col2 = st.columns(2)
        col1.metric("Strategy Value", f"${final_strategy:,.2f}", delta=f"{((final_strategy/initial_value - 1)*100):.2f}%")
        col2.metric("Buy & Hold Value", f"${final_hold:,.2f}", delta=f"{((final_hold/initial_value - 1)*100):.2f}%")
        st.line_chart(df[['Strategy Equity', 'BuyHold Equity']])

        # Performance metrics
        st.markdown("### 📐 Strategy Performance Metrics")
        strategy_return = (final_strategy / initial_value - 1) * 100
        rolling_max = df['Strategy Equity'].cummax()
        drawdown = df['Strategy Equity'] / rolling_max - 1
        max_drawdown = drawdown.min() * 100
        trades = df[df['Position'].isin([2, -2])].copy()
        trades['Price'] = df['Close']
        trades['Trade Return'] = trades['Price'].pct_change()
        win_rate = (trades['Trade Return'] > 0).sum() / len(trades['Trade Return'].dropna()) * 100 if len(trades) > 1 else 0
        num_trades = len(trades['Trade Return'].dropna())
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Return", f"{strategy_return:.2f}%")
        col2.metric("Max Drawdown", f"{max_drawdown:.2f}%")
        col3.metric("Win Rate", f"{win_rate:.2f}%")
        col4.metric("Number of Trades", f"{num_trades}")

        # Risk & reward
        st.markdown("### ⚡ Risk & Reward Metrics")
        rf_rate = 0.04
        trading_days = 252
        strategy_returns = df['Strategy Return'].dropna()
        if len(strategy_returns) > 1:
            sharpe_ratio = ((strategy_returns.mean() - rf_rate/trading_days) / strategy_returns.std()) * np.sqrt(trading_days)
            volatility = strategy_returns.std() * np.sqrt(trading_days)
            col1, col2 = st.columns(2)
            col1.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}")
            col2.metric("Annualized Volatility", f"{volatility:.2%}")
        else:
            st.info("Not enough data to calculate Sharpe Ratio and Volatility.")

        # Trade log
        st.markdown("### 📝 Trade Log")
        trades_list = []
        for idx, row in trades.iterrows():
            action = "Buy" if row['Position'] == 2 else "Sell"
            trades_list.append({
                "Date": idx.strftime('%Y-%m-%d'),
                "Action": action,
                "Price": row['Close']
            })
        trades_df = pd.DataFrame(trades_list)
        if not trades_df.empty:
            st.dataframe(trades_df, height=250)
        else:
            st.write("No trades executed in this timeframe.")
