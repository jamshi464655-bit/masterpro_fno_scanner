import streamlit as st
import pandas as pd
import yfinance as yf
# പുതിയതും സുരക്ഷിതവുമായ ലൈബ്രറി ഉപയോഗിക്കുന്നു
import ta as ta_indicators

# Page configuration
st.set_page_config(page_title="MasterPro F&O Scanner", layout="wide")

# Custom Styling
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
tf_choice = st.sidebar.selectbox("Select Timeframe", ["15m", "1h", "1d"], index=0)

period_map = {"15m": "5d", "1h": "20d", "1d": "60d"}
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
        
        if df.empty or len(df) < 55:
            continue
            
        # 1. EMA Calculations (using ta library)
        df['EMA8'] = ta_indicators.trend.ema_indicator(df['Close'], window=8)
        df['EMA13'] = ta_indicators.trend.ema_indicator(df['Close'], window=13)
        df['EMA21'] = ta_indicators.trend.ema_indicator(df['Close'], window=21)
        df['EMA55'] = ta_indicators.trend.ema_indicator(df['Close'], window=55)
        
        # 2. VWAP Calculation (Manual fallback for stability)
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3
        df['VWAP'] = (typical_price * df['Volume']).cumsum() / df['Volume'].cumsum()
        
        # 3. RSI Calculation
        df['RSI'] = ta_indicators.momentum.rsi(df['Close'], window=14)
        
        # 4. MACD Calculation
        df['MACD'] = ta_indicators.trend.macd(df['Close'], window_fast=12, window_slow=26)
        df['MACD_Signal'] = ta_indicators.trend.macd_signal(df['Close'], window_fast=12, window_slow=26, window_sign=9)
        
        # 5. ADX Calculation
        df['ADX'] = ta_indicators.trend.adx(df['High'], df['Low'], df['Close'], window=14)
        
        latest = df.iloc[-1]
        
        ltp = float(latest['Close'])
        rsi_val = float(latest['RSI'])
        adx_val = float(latest['ADX'])
        vwap_val = float(latest['VWAP'])
        
        ema8_val = float(latest['EMA8'])
        ema13_val = float(latest['EMA13'])
        ema21_val = float(latest['EMA21'])
        macd_val = float(latest['MACD'])
        macd_sig = float(latest['MACD_Signal'])

        # BUY Condition
        buy_condition = (ema8_val > ema13_val > ema21_val) and (ltp > vwap_val) and (rsi_val > 50) and (macd_val > macd_sig) and (adx_val > 20)
        
        # SELL Condition
        sell_condition = (ema8_val < ema13_val < ema21_val) and (ltp < vwap_val) and (rsi_val < 50) and (macd_val < macd_sig) and (adx_val > 20)
        
        stock_name = sym.replace(".NS", "")
        
        stock_data = {
            "Symbol": stock_name,
            "LTP": round(ltp, 2),
            "RSI": round(rsi_val, 1),
            "ADX": round(adx_val, 1),
            "VWAP": round(vwap_val, 2)
        }
        
        if buy_condition:
            buy_signals.append(stock_data)
        elif sell_condition:
            sell_signals.append(stock_data)
            
    except:
        pass
        
    progress.progress((i + 1) / len(symbols_ns))

st.success("✅ സ്കാനിംഗ് വിജയകരമായി പൂർത്തിയായി!")

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section">🚀 MASTER PRO: BUY SIGNALS</div>', unsafe_allow_html=True)
    if buy_signals:
        st.dataframe(pd.DataFrame(buy_signals), use_container_width=True, hide_index=True)
    else:
        st.info("ഈ ടൈംഫ്രെയിമിൽ BUY കണ്ടീഷൻ ഒത്തുവരുന്ന സ്റ്റോക്കുകൾ ഇല്ല.")

with col2:
    st.markdown('<div class="sell-section">📉 MASTER PRO: SELL SIGNALS</div>', unsafe_allow_html=True)
    if sell_signals:
        st.dataframe(pd.DataFrame(sell_signals), use_container_width=True, hide_index=True)
    else:
        st.info("ഈ ടൈംഫ്രെയിമിൽ SELL കണ്ടീഷൻ ഒത്തുവരുന്ന സ്റ്റോക്കുകൾ ഇല്ല.")

st.markdown("---")
if st.button("🔄 Manual Refresh"):
    st.rerun()
