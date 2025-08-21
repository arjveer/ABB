import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Stock Analysis Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

def fetch_stock_data(ticker, start_date, end_date):
    """Fetch historical stock data using yfinance"""
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(start=start_date, end=end_date)
        
        if data.empty:
            st.error(f"No data found for {ticker}")
            return None
            
        return data, stock
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {str(e)}")
        return None, None

def calculate_technical_indicators(df):
    """Calculate technical indicators"""
    # Moving averages
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['EMA_12'] = df['Close'].ewm(span=12).mean()
    df['EMA_26'] = df['Close'].ewm(span=26).mean()
    
    # MACD
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
    df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Bollinger Bands
    df['BB_Middle'] = df['Close'].rolling(window=20).mean()
    bb_std = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
    df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
    
    # Volume indicators
    df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
    df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']
    
    return df

def create_price_chart(df, ticker):
    """Create interactive price chart with technical indicators"""
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=(f'{ticker} Price & Indicators', 'Volume', 'RSI'),
        row_heights=[0.6, 0.2, 0.2]
    )
    
    # Price and moving averages
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Close'], name='Close Price', 
                  line=dict(color='#1f77b4', width=2)),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=df.index, y=df['SMA_20'], name='SMA 20', 
                  line=dict(color='orange', width=1)),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=df.index, y=df['SMA_50'], name='SMA 50', 
                  line=dict(color='red', width=1)),
        row=1, col=1
    )
    
    # Bollinger Bands
    fig.add_trace(
        go.Scatter(x=df.index, y=df['BB_Upper'], name='BB Upper', 
                  line=dict(color='gray', width=1, dash='dash')),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=df.index, y=df['BB_Lower'], name='BB Lower', 
                  line=dict(color='gray', width=1, dash='dash')),
        row=1, col=1
    )
    
    # Volume
    colors = ['red' if close < open else 'green' for close, open in zip(df['Close'], df['Open'])]
    fig.add_trace(
        go.Bar(x=df.index, y=df['Volume'], name='Volume', 
               marker_color=colors, opacity=0.7),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Volume_SMA'], name='Volume SMA', 
                  line=dict(color='blue', width=1)),
        row=2, col=1
    )
    
    # RSI
    fig.add_trace(
        go.Scatter(x=df.index, y=df['RSI'], name='RSI', 
                  line=dict(color='purple', width=2)),
        row=3, col=1
    )
    
    # RSI overbought/oversold lines
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
    
    fig.update_layout(
        height=800,
        showlegend=True,
        title_text=f"{ticker} Technical Analysis",
        xaxis_rangeslider_visible=False
    )
    
    return fig

def create_macd_chart(df, ticker):
    """Create MACD chart"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], name='MACD', 
                             line=dict(color='blue', width=2)))
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD_Signal'], name='Signal', 
                             line=dict(color='red', width=2)))
    fig.add_trace(go.Bar(x=df.index, y=df['MACD_Histogram'], name='Histogram', 
                         marker_color='gray', opacity=0.7))
    
    fig.update_layout(
        title_text=f"{ticker} MACD",
        height=400,
        xaxis_title="Date",
        yaxis_title="MACD"
    )
    
    return fig

def display_stock_info(stock, ticker):
    """Display stock information and key metrics"""
    try:
        info = stock.info
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Market Cap", f"${info.get('marketCap', 'N/A'):,}" if info.get('marketCap') else 'N/A')
        
        with col2:
            st.metric("P/E Ratio", f"{info.get('trailingPE', 'N/A'):.2f}" if info.get('trailingPE') else 'N/A')
        
        with col3:
            st.metric("52 Week High", f"${info.get('fiftyTwoWeekHigh', 'N/A'):.2f}" if info.get('fiftyTwoWeekHigh') else 'N/A')
        
        with col4:
            st.metric("52 Week Low", f"${info.get('fiftyTwoWeekLow', 'N/A'):.2f}" if info.get('fiftyTwoWeekLow') else 'N/A')
        
        # Company description
        if info.get('longBusinessSummary'):
            st.subheader("Company Description")
            st.write(info['longBusinessSummary'])
            
    except Exception as e:
        st.warning(f"Could not fetch company information: {str(e)}")

def main():
    # Header
    st.markdown('<h1 class="main-header">📈 Stock Analysis Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.header("📊 Analysis Settings")
    
    # Ticker input
    ticker = st.sidebar.text_input("Enter Stock/ETF Ticker", value="AAPL").upper()
    
    # Date range selection
    st.sidebar.subheader("📅 Date Range")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=start_date)
    with col2:
        end_date = st.date_input("End Date", value=end_date)
    
    # Quick date presets
    st.sidebar.subheader("⏱️ Quick Presets")
    if st.sidebar.button("1 Month"):
        start_date = end_date - timedelta(days=30)
    if st.sidebar.button("3 Months"):
        start_date = end_date - timedelta(days=90)
    if st.sidebar.button("6 Months"):
        start_date = end_date - timedelta(days=180)
    if st.sidebar.button("1 Year"):
        start_date = end_date - timedelta(days=365)
    if st.sidebar.button("5 Years"):
        start_date = end_date - timedelta(days=1825)
    
    # Analysis options
    st.sidebar.subheader("🔧 Analysis Options")
    show_indicators = st.sidebar.checkbox("Show Technical Indicators", value=True)
    show_macd = st.sidebar.checkbox("Show MACD Chart", value=True)
    show_volume = st.sidebar.checkbox("Show Volume Analysis", value=True)
    
    # Fetch data
    if st.sidebar.button("🚀 Analyze Stock", type="primary"):
        with st.spinner(f"Fetching data for {ticker}..."):
            data, stock = fetch_stock_data(ticker, start_date, end_date)
            
            if data is not None and stock is not None:
                st.success(f"✅ Successfully fetched data for {ticker}")
                
                # Calculate technical indicators
                if show_indicators:
                    data = calculate_technical_indicators(data)
                
                # Display stock information
                st.subheader(f"📋 {ticker} Information")
                display_stock_info(stock, ticker)
                
                # Key metrics
                st.subheader("📊 Key Metrics")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    current_price = data['Close'].iloc[-1]
                    price_change = data['Close'].iloc[-1] - data['Close'].iloc[-2]
                    price_change_pct = (price_change / data['Close'].iloc[-2]) * 100
                    
                    st.metric(
                        "Current Price",
                        f"${current_price:.2f}",
                        f"{price_change:+.2f} ({price_change_pct:+.2f}%)"
                    )
                
                with col2:
                    st.metric("Volume", f"{data['Volume'].iloc[-1]:,}")
                
                with col3:
                    if show_indicators:
                        st.metric("RSI", f"{data['RSI'].iloc[-1]:.2f}")
                    else:
                        st.metric("Open", f"${data['Open'].iloc[-1]:.2f}")
                
                with col4:
                    if show_indicators:
                        st.metric("MACD", f"{data['MACD'].iloc[-1]:.4f}")
                    else:
                        st.metric("High", f"${data['High'].iloc[-1]:.2f}")
                
                # Price chart
                st.subheader(f"📈 {ticker} Price Chart")
                if show_indicators:
                    fig = create_price_chart(data, ticker)
                else:
                    fig = px.line(data, x=data.index, y='Close', title=f'{ticker} Close Price')
                    fig.update_layout(height=500)
                
                st.plotly_chart(fig, use_container_width=True)
                
                # MACD chart
                if show_macd and show_indicators:
                    st.subheader("📊 MACD Analysis")
                    macd_fig = create_macd_chart(data, ticker)
                    st.plotly_chart(macd_fig, use_container_width=True)
                
                # Data table
                st.subheader("📋 Raw Data")
                st.dataframe(data.tail(20), use_container_width=True)
                
                # Download data
                st.subheader("💾 Download Data")
                csv = data.to_csv(index=True)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"{ticker}_data_{start_date}_{end_date}.csv",
                    mime="text/csv"
                )
                
            else:
                st.error("Failed to fetch data. Please check the ticker symbol and try again.")
    
    # Instructions
    if not st.session_state.get('data_fetched', False):
        st.info("""
        **📖 How to use this dashboard:**
        1. Enter a stock/ETF ticker symbol (e.g., AAPL, MSFT, SPY)
        2. Select your desired date range
        3. Choose analysis options
        4. Click "Analyze Stock" to fetch and analyze data
        
        **💡 Popular tickers to try:**
        - **Stocks:** AAPL, MSFT, GOOGL, TSLA, AMZN
        - **ETFs:** SPY, QQQ, VTI, VOO, IWM
        - **Crypto:** BTC-USD, ETH-USD
        """)

if __name__ == "__main__":
    main()
