https://momentum-strat-vjw3babgrwxvggqwjlqezn.streamlit.app/
---

This project showcases a **Momentum Trading Strategy** implemented using Python and other data science tools. It leverages:

- **Financial market knowledge**: Utilizing key technical indicators like moving averages and volume to capture price momentum and generate trading signals.
- **Python programming**: Built with libraries including `pandas`, `numpy`, `yfinance` (for live and historical market data), and `matplotlib` for visualization.
- **Quantitative analysis skills**: Incorporates backtesting of strategy performance with key metrics such as return, drawdown, Sharpe ratio, and trade logs to evaluate effectiveness.
- **Interactive visualization**: Powered by [Streamlit](https://streamlit.io/) to create a clean, user-friendly web app allowing dynamic input of ticker symbols and customizable timeframes.
- **Version control & deployment**: Hosted on GitHub with automated deployment on Streamlit Community Cloud for seamless sharing and collaboration.

---


# Momentum Strategy

This project is a simple moving average crossover strategy built in Python.

## 📈 Strategy Overview
- Uses 20-day and 50-day moving averages on closing prices
- Buys when 20-day MA crosses above 50-day MA
- Sells when 20-day MA crosses below 50-day MA
- Visualizes buy/sell signals on a stock chart

## 🔧 Built With
- Python
- Jupyter Notebook
- pandas, numpy, matplotlib
- yfinance (for historical stock data)

## 🚀 How to Run
1. Install dependencies:
pip install yfinance pandas matplotlib numpy
2. Open the notebook in Jupyter:
jupyter notebook
3. Run each cell and view the chart

## 💡 Ideas for Future Work
- Add performance backtesting
- Try more tickers or ETFs
- Build a Streamlit web app (coming soon)

## 👤 Author
Max Lonergan

