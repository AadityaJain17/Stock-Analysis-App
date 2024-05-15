import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from scipy.stats import norm

st.write("""
# Simple Stock Analysis App

""")

# Get a list of ticker symbols from finance
ticker_list = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NFLX']  # You can add more ticker symbols

# Create a dropdown menu for selecting the ticker symbol
tickerSymbol = st.sidebar.selectbox("Select Ticker Symbol", ticker_list)

# Get data on the selected ticker symbol
tickerData = yf.Ticker(tickerSymbol)
# Get the historical prices for this ticker
tickerDf = tickerData.history(period='1d', start='2014-5-31', end='2024-5-31')

# Calculate Moving Averages
tickerDf['MA10'] = tickerDf['Close'].rolling(window=10).mean()
tickerDf['MA20'] = tickerDf['Close'].rolling(window=20).mean()

# Calculate Daily Returns
tickerDf['Daily Return'] = tickerDf['Close'].pct_change()

# Calculate Cumulative Returns
tickerDf['Cumulative Return'] = (1 + tickerDf['Daily Return']).cumprod() - 1

# Calculate Relative Strength Index (RSI)
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

tickerDf['RSI'] = calculate_rsi(tickerDf)

# Determine Overbought and Oversold
def overbought_oversold(data, overbought_thresh=70, oversold_thresh=30):
    signals = []
    for rsi in data['RSI']:
        if rsi > overbought_thresh:
            signals.append("Overbought")
        elif rsi < oversold_thresh:
            signals.append("Oversold")
        else:
            signals.append("Neutral")
    return signals

tickerDf['Signal'] = overbought_oversold(tickerDf)

# Plot Closing Price Over the Year
st.write("""
## Stock Price Over the Year
""")
st.line_chart(tickerDf['Close'])

# Plot Closing Price with Moving Averages
st.write("""
## Stock Price with Moving Averages (10-day and 20-day)
""")
fig, ax = plt.subplots()
ax.plot(tickerDf.index, tickerDf['Close'], label='Closing Price')
ax.plot(tickerDf.index, tickerDf['MA10'], label='10-day Moving Average')
ax.plot(tickerDf.index, tickerDf['MA20'], label='20-day Moving Average')
ax.legend()
st.pyplot(fig)

# Plot Histogram of Daily Returns
st.write("""
## Histogram of Daily Returns
""")
fig, ax = plt.subplots()
tickerDf['Daily Return'].hist(bins=50, edgecolor='black', alpha=0.7)
mean = tickerDf['Daily Return'].mean()
std_dev = tickerDf['Daily Return'].std()
xmin, xmax = plt.xlim()
x = np.linspace(xmin, xmax, 100)
p = norm.pdf(x, mean, std_dev)
ax.plot(x, p, 'k', linewidth=2)
ax.set_title('Daily Returns Histogram')
ax.set_xlabel('Daily Return')
ax.set_ylabel('Frequency')
st.pyplot(fig)

# Plot Cumulative Returns
st.write("""
## Cumulative Returns
""")
fig, ax = plt.subplots()
ax.plot(tickerDf.index, tickerDf['Cumulative Return'])
ax.set_title('Cumulative Returns')
ax.set_xlabel('Date')
ax.set_ylabel('Cumulative Return')
st.pyplot(fig)

# Plot RSI with Overbought and Oversold Signals
st.write("""
## RSI with Overbought and Oversold Signals
""")
fig, ax = plt.subplots()
ax.plot(tickerDf.index, tickerDf['RSI'], label='RSI', color='blue')
ax.fill_between(tickerDf.index, y1=70, y2=30, color='gray', alpha=0.3)
ax.text(tickerDf.index[10], 80, 'Overbought', fontsize=10, color='red')
ax.text(tickerDf.index[10], 20, 'Oversold', fontsize=10, color='green')
ax.set_title('Relative Strength Index (RSI)')
ax.set_xlabel('Date')
ax.set_ylabel('RSI')
ax.legend()
st.pyplot(fig)

# Show the dataframe
st.write("""
## Stock Data
""")
st.write(tickerDf)
