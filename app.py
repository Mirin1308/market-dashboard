import streamlit as st
from streamlit_autorefresh import st_autorefresh
import yfinance as yf
import requests
from datetime import datetime

st.set_page_config(page_title="Market Dashboard", layout="wide")

# ✅ auto refresh
st_autorefresh(interval=5000, key="refresh")

st.title("📊 Market Dashboard (BTC | Gold | S&P 500)")

# ===== CONFIG =====
BINANCE_BTC = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
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
        import yfinance as yf
        btc = yf.Ticker("BTC-USD")
        data = btc.history(period="1d", interval="1m")
        return float(data["Close"].iloc[-1])
    except Exception as e:
        st.error(f"BTC ERROR: {e}")
        return None

    except Exception as e:
        st.error(f"BTC REQUEST FAILED: {e}")
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

# ===== DATA =====
btc = get_btc()
gold = get_gold()
sp500 = get_sp500()

# ===== UI =====
col1, col2, col3 = st.columns(3)

col1.metric("BTC", f"${btc:,.2f}" if btc else "N/A")
col2.metric("Gold", f"${gold:,.2f}" if gold else "N/A")
col3.metric("S&P 500", f"{sp500:,.2f}" if sp500 else "N/A")

st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
