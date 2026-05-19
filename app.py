import streamlit as st
import pandas as pd
import yfinance as yf
import ta as ta_indicators

# Page configuration
st.set_page_config(page_title="MasterPro F&O Scanner", layout="wide")

# Custom Styling (Dark Premium Theme)
st.markdown("""
<style>
    .header {
        background: linear-gradient(135deg, #0f172a, #1e293b); 
        padding: 25px; 
        border-radius: 12px; 
        color: white; 
        text-align: center; 
        border: 1px solid #334155;
        margin-bottom: 20px;
    }
    .section {
        background: linear-gradient(135deg, #065f46, #10b981); 
        color: white; 
        padding: 12px; 
        border-radius: 10px; 
        font-weight: bold; 
        margin: 15px 0 8px 0;
    }
    .sell-section {
        background: linear-gradient(135deg, #991b1b, #ef4444); 
        color: white; 
        padding: 12px; 
        border-radius: 10px; 
        font-weight: bold; 
        margin: 15px 0 8px 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header"><h1>Master Pro F&O Scanner</h1><p>NSE Futures & Options Live Momentum & Trend Scanner</p></div>', unsafe_allow_html=True)

# Sidebar Settings
st.sidebar.header("⚙️ Scanner Settings")
# 5m ടൈംഫ്രെയിം ഇവിടെ ഉൾപ്പെടുത്തിയിട്ടുണ്ട്
tf_choice = st.sidebar.selectbox("Select Timeframe", ["5m", "15m", "1h", "1d"], index=1)

# yfinance പരിമിതികൾ അനുസരിച്ച് പീരിയഡ് മാപ്പ് ചെയ്യുന്നു (5m ടൈംഫ്രെയിമിന് 1d/2d ആണ് സുരക്ഷിതം)
period_map = {"5m": "1d", "15m": "5d", "1h": "20d", "1d": "60d"}
data_period = period_map[tf_choice]

# Full NSE F&O Stock List
fno_symbols = [
    "AARTIIND", "ABB", "ABBOTINDIA", "ABCAPITAL", "ABFRL", "ACC", "ADANIENT", "ADANIPORTS",
    "ADANIPOWER", "ALKEM", "AMBUJACEM", "APOLLOHOSP", "APOLLOTYRES", "ASHOKLEY", "ASIANPAINT",
    "ASTRAL", "ATUL", "AUBANK", "AUROPHARMA", "AXISBANK", "BAJAJ-AUTO", "BAJAJFINSV",
    "BAJFINANCE", "BALKRISIND", "BALRAMCHIN", "BANDHANBNK", "BANKBARODA", "BATAINDIA",
    "BEL", "BERGEPAINT", "BHARATFORG", "BHARTIARTL", "BHEL", "BIOCON", "BOSCHLTD",
    "BPCL", "BRITANNIA", "BSOFT", "CANBK", "CANFINHOME", "CHAMBLFERT", "CHOLAMANDM",
    "CIPLA", "COALINDIA", "COFORGE", "COLPAL", "CONCOR", "COROMANDEL", "CROMPTON",
    "CUMMINSIND", "DABUR", "DALBHARAT", "DEEPAKNTR", "DELHIVERY", "DIVISLAB", "DIXON",
    "DLF", "DRREDDY", "EICHERMOT", "ESCORTS", "EXIDEIND", "FEDERALBNK", "GAIL",
    "GLENMARK", "GMRINFRA", "GODREJCP", "GODREJPROP", "GRANULES", "GRASIM", "GUJGASLTD",
    "HAL", "HAVELLS", "HCLTECH", "HDFCBANK", "HDFCLIFE", "HEROMOTOCO", "HINDALCO",
    "HINDCOPPER", "HINDUNILVR", "ICICIBANK", "ICICIGI", "ICICIPRULI", "IDEA", "IDFCFIRSTB",
    "IEX", "IGL", "INDHOTEL", "INDIACEM", "INDIAMART", "INDIGO", "INDUSINDBK",
    "INDUSTOWER", "INFY", "IOC", "IRCTC", "IRFC", "ITC", "JINDALSTEL", "JIOFIN",
    "JKCEMENT", "JSWSTEEL", "JUBLFOOD", "KALYANKJIL", "KEI", "KFINTECH", "KOTAKBANK",
    "L&TFH", "LALPATHLAB", "LICHSGFIN", "LTIM", "LT", "LUPIN", "M&MFIN", "M&M",
    "MANAPPURAM", "MARUTI", "MCX", "METROPOLIS", "MFSL", "MGL", "MOTHERSON", "MPHASIS",
    "MRF", "MUTHOOTFIN", "NATIONALUM", "NAVINFLUOR", "NESTLEIND", "NMDC", "NTPC",
    "NYKAA", "OBEROIRLTY", "OFSS", "ONGC", "PAGEIND", "PEL", "PERSISTENT", "PETRONET",
    "PFC", "PIDILITIND", "PIIND", "PNB", "POLYCAB", "POWERGRID", "PVRINOX", "RAMCOCEM",
    "RBLBANK", "RECLTD", "RELIANCE", "SAIL", "SBICARD", "SBILIFE", "SBIN", "SHREECEM",
    "SHRIRAMFIN", "SIEMENS", "SRF", "SUNPHARMA", "SUNTV", "SUPREMEIND",
    "SYNGENE", "TATACHEMICALS", "TATACOMM", "TATACONSUM", "TATAELXSI", "TATAMOTORS",
    "TATAPOWER", "TATASTEEL", "TCS", "TECHM", "TITAN", "TORNTPHARM", "TRENT",
    "TVSMOTOR", "UBL", "ULTRACEMCO", "UNIONBANK", "UPL", "VEDL", "VOLTAS", "WIPRO",
    "YESBANK", "ZOMATO"
]

symbols_ns = [f"{sym}.NS" for sym in fno_symbols]

buy_signals = []
sell_signals = []

st.write(f"📊 **Timeframe: {tf_choice}** | {len(fno_symbols)} F&O സ്റ്റോക്കുകൾ പരിശോധിക്കുന്നു...")
progress = st.progress(0)

for i, sym in enumerate(symbols_ns):
    try:
        df = yf.download(sym, period=data_period, interval=tf_choice, progress=False)
        
        # 5m ടൈംഫ്രെയിമിൽ EMA 55 കണക്കാക്കാൻ കുറഞ്ഞത് 55 കാൻഡിലുകൾ വേണം. 
        # ലൈവ് മാർക്കറ്റിൽ 1d എടുത്താൽ 55-ലധികം കാൻഡിലുകൾ ഉണ്ടാകും. രാവിലെ 10 മണിക്ക് മുൻപ് റൺ ചെയ്യുമ്പോൾ ഡാറ്റ കുറവാണെങ്കിൽ 2d ലേക്ക് തനിയെ മാറും.
        if df.empty or len(df) < 55:
            if tf_choice == "5m":
                df = yf.download(sym, period="2d", interval=tf_choice, progress=False)
            if df.empty or len(df) < 55:
                continue
            
        # 1. EMA Calculations
        df['EMA8'] = ta_indicators.trend.ema_indicator(df['Close'], window=8)
        df['EMA13'] = ta_indicators.trend.ema_indicator(df['Close'], window=13)
        df['EMA21'] = ta_indicators.trend.ema_indicator(df['Close'], window=21)
        df['EMA55'] = ta_indicators.trend.ema_indicator(df['Close'], window=55)
        
        # 2. VWAP Calculation
        typical_price = (df['High'] + df['Low'] + df['Close']) /
