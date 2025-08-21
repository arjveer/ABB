# 📈 Stock Analysis Dashboard

A comprehensive web-based stock analysis application built with **Streamlit**, **yfinance**, **pandas**, and **plotly**. This dashboard allows users to analyze historical stock and ETF data with interactive charts, technical indicators, and a user-friendly web interface.

## ✨ Features

### 📊 Data Fetching
- **Real-time stock data** using Yahoo Finance API (yfinance)
- Support for **stocks**, **ETFs**, and **cryptocurrencies**
- **Flexible date ranges** with quick presets (1M, 3M, 6M, 1Y, 5Y)
- **Custom date selection** for precise analysis periods

### 🔧 Technical Analysis
- **Moving Averages**: Simple Moving Average (SMA) 20 & 50, Exponential Moving Average (EMA) 12 & 26
- **MACD**: Moving Average Convergence Divergence with signal line and histogram
- **RSI**: Relative Strength Index with overbought/oversold levels (30/70)
- **Bollinger Bands**: Upper, middle, and lower bands for volatility analysis
- **Volume Analysis**: Volume trends and volume moving averages

### 📈 Interactive Charts
- **Multi-panel charts** with price, volume, and RSI
- **Interactive plotly visualizations** with zoom, pan, and hover details
- **Color-coded volume bars** (green for price up, red for price down)
- **Technical indicator overlays** on price charts
- **Separate MACD chart** for detailed momentum analysis

### 🎯 Key Metrics
- **Current price** with daily change and percentage
- **Volume analysis** and trends
- **Company information** including market cap, P/E ratio
- **52-week high/low** ranges
- **Real-time data updates**

### 💾 Data Export
- **CSV download** functionality for further analysis
- **Raw data table** display for detailed inspection
- **Formatted data** ready for external tools

## 🚀 Installation

### Prerequisites
- Python 3.8.1 or higher
- uv package manager (recommended) or pip

### Setup with UV (Recommended)
1. **Clone or download** this repository
2. **Navigate** to the project directory:
   ```bash
   cd session-1_from_start
   ```

3. **Install core dependencies** using uv:
   ```bash
   uv pip install streamlit yfinance pandas plotly numpy
   ```
   
   Or install all dependencies including dev tools:
   ```bash
   uv pip install -r requirements.txt
   ```

### Setup with pip
```bash
pip install streamlit yfinance pandas plotly numpy
```

## 🎮 Usage

### Running the Application
1. **Start the Streamlit app** with uv:
   ```bash
   uv run streamlit run main.py
   ```
   
   Or with pip:
   ```bash
   streamlit run main.py
   ```

2. **Open your browser** and navigate to the displayed URL (usually `http://localhost:8501`)

### How to Use
1. **Enter a ticker symbol** in the sidebar (e.g., AAPL, MSFT, SPY)
2. **Select date range** using the date pickers or quick preset buttons
3. **Choose analysis options** (technical indicators, MACD, volume analysis)
4. **Click "Analyze Stock"** to fetch and display data
5. **Explore the charts** and metrics
6. **Download data** as CSV for further analysis

### Popular Tickers to Try
- **Stocks**: AAPL, MSFT, GOOGL, TSLA, AMZN, NVDA
- **ETFs**: SPY, QQQ, VTI, VOO, IWM, TLT
- **Crypto**: BTC-USD, ETH-USD, ADA-USD
- **International**: ^GSPC (S&P 500), ^DJI (Dow Jones), ^IXIC (NASDAQ)

## 🏗️ Architecture

### Core Components
- **`main.py`**: Main application entry point and Streamlit interface
- **`fetch_stock_data()`**: Data retrieval using yfinance
- **`calculate_technical_indicators()`**: Technical analysis calculations
- **`create_price_chart()`**: Interactive chart generation
- **`create_macd_chart()`**: MACD-specific visualization
- **`display_stock_info()`**: Company information display

### Data Flow
1. **User Input** → Ticker symbol and date range
2. **API Call** → yfinance fetches data from Yahoo Finance
3. **Data Processing** → pandas for data manipulation and calculations
4. **Visualization** → plotly for interactive charts
5. **Display** → Streamlit web interface

## 🔧 Customization

### Adding New Indicators
To add new technical indicators, modify the `calculate_technical_indicators()` function:

```python
def calculate_technical_indicators(df):
    # Existing indicators...
    
    # Add your custom indicator
    df['Custom_Indicator'] = your_calculation_function(df)
    
    return df
```

### Modifying Charts
Customize chart appearance by modifying the `create_price_chart()` function:

```python
def create_price_chart(df, ticker):
    # Modify colors, styles, or add new traces
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Your_Indicator'], 
                  name='Your Indicator', line=dict(color='purple'))
    )
```

## 📚 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `streamlit` | ≥1.28.0 | Web application framework |
| `yfinance` | ≥0.2.18 | Yahoo Finance data API |
| `pandas` | ≥2.0.0 | Data manipulation and analysis |
| `plotly` | ≥5.15.0 | Interactive plotting library |
| `numpy` | ≥1.24.0 | Numerical computing |

## 🚨 Troubleshooting

### Common Issues

#### Python Version Compatibility
If you encounter dependency resolution errors, ensure you're using Python 3.8.1 or higher:
```bash
python --version
```

#### UV Dependency Issues
If `uv pip install -r requirements.txt` fails, install core dependencies only:
```bash
uv pip install streamlit yfinance pandas plotly numpy
```

#### Streamlit Not Found
If `streamlit` command is not found, ensure it's installed:
```bash
uv pip install streamlit
```

### Alternative Installation Methods
```bash
# Using pip directly
pip install streamlit yfinance pandas plotly numpy

# Using conda
conda install -c conda-forge streamlit yfinance pandas plotly numpy
```

## 🌟 Key Benefits

- **Real-time data**: Live stock information from Yahoo Finance
- **Professional charts**: Publication-quality interactive visualizations
- **Technical analysis**: Built-in indicators for trading decisions
- **User-friendly**: Intuitive web interface for non-technical users
- **Exportable**: Download data for external analysis
- **Responsive**: Works on desktop and mobile devices

## 🚨 Limitations

- **Rate limiting**: Yahoo Finance API may have usage limits
- **Data accuracy**: Depends on Yahoo Finance data quality
- **Market hours**: Real-time data only available during market hours
- **Internet required**: Needs active internet connection

## 🤝 Contributing

Feel free to contribute by:
- Adding new technical indicators
- Improving chart aesthetics
- Adding new data sources
- Enhancing the user interface
- Fixing bugs or issues

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- **Yahoo Finance** for providing free financial data
- **Streamlit** for the excellent web app framework
- **Plotly** for interactive charting capabilities
- **Pandas** for powerful data manipulation tools

---

**Happy Trading! 📈💰**
