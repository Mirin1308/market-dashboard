import streamlit as st
from streamlit_autorefresh import st_autorefresh
import yfinance as yf
import requests
import pandas as pd
from datetime import datetime

# ✅ MUST BE FIRST
st.set_page_config(page_title="Market Dashboard", layout="wide")

# ✅ auto refresh
st_autorefresh(interval=5000, key="refresh")

st.title("📊 Market Dashboard (BTC | Gold | S&P 500)")

# ===== CONFIG =====
GOLD_URL = "https://api.twelvedata.com/price?symbol=XAU/USD&apikey={}"

# safe API key
try:
    API_KEY = st.secrets["API_KEY"]
except:
    API_KEY = None

# ===== FUNCTIONS =====
def safe_get_price(url):
    try:
        data = requests.get(url, timeout=5).json()
        return float(data["price"]) if "price" in data else None
    except:
        return None

def get_btc():
    try:
        btc = yf.Ticker("BTC-USD")
        data = btc.history(period="1d", interval="1m")
        return float(data["Close"].iloc[-1])
    except:
        return None

def get_gold():
    if not API_KEY:
        return None
    return safe_get_price(GOLD_URL.format(API_KEY))

def get_sp500():
    try:
        sp = yf.Ticker("^GSPC")
        data = sp.history(period="1d", interval="1m")
        return float(data["Close"].iloc[-1])
    except:
        return None

# ===== GET DATA FIRST =====
btc = get_btc()
gold = get_gold()
sp500 = get_sp500()

now = datetime.now()

# ===== SESSION STORAGE =====
if "btc_data" not in st.session_state:
    st.session_state.btc_data = []
if "gold_data" not in st.session_state:
    st.session_state.gold_data = []
if "sp500_data" not in st.session_state:
    st.session_state.sp500_data = []

# ===== APPEND DATA =====
if btc:
    st.session_state.btc_data.append({"time": now, "price": btc})
if gold:
    st.session_state.gold_data.append({"time": now, "price": gold})
if sp500:
    st.session_state.sp500_data.append({"time": now, "price": sp500})

# ===== LIMIT DATA =====
MAX_POINTS = 100
st.session_state.btc_data = st.session_state.btc_data[-MAX_POINTS:]
st.session_state.gold_data = st.session_state.gold_data[-MAX_POINTS:]
st.session_state.sp500_data = st.session_state.sp500_data[-MAX_POINTS:]

# ===== DATAFRAME =====
btc_df = pd.DataFrame(st.session_state.btc_data)
gold_df = pd.DataFrame(st.session_state.gold_data)
sp500_df = pd.DataFrame(st.session_state.sp500_data)

# ===== METRICS =====
col1, col2, col3 = st.columns(3)

col1.metric("BTC", f"${btc:,.2f}" if btc else "N/A")
col2.metric("Gold", f"${gold:,.2f}" if gold else "N/A")
col3.metric("S&P 500", f"{sp500:,.2f}" if sp500 else "N/A")

# ===== CHARTS =====
st.subheader("📈 Live Charts")

col1, col2, col3 = st.columns(3)

if not btc_df.empty:
    col1.line_chart(btc_df.set_index("time"))

if not gold_df.empty:
    col2.line_chart(gold_df.set_index("time"))

if not sp500_df.empty:
    col3.line_chart(sp500_df.set_index("time"))

st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
