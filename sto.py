import requests
import pyotp
import json
import time
import datetime
from SmartApi import SmartConnect
from SmartApi.smartWebSocketV2 import SmartWebSocketV2
import pandas as pd
import difflib
from tabulate import tabulate # to restructure the output in a table format

#Angel Broking API Setup 
# === Install required packages if not already installed ===
# Must have Angle broking account and SmartAPI account 

# === Replace with your own credentials ===
API_KEY = ""
CLIENT_CODE = ""
PASSWORD = "" #Angle one code when you login to the app
TOTP_SECRET = "" # This is the TOTP secret key from your Angel Broking account settings

# === Login and Session Setup ===
smartApi = SmartConnect(api_key=API_KEY)
totp = pyotp.TOTP(TOTP_SECRET).now()

login_data = smartApi.generateSession(CLIENT_CODE, PASSWORD, totp)
AUTH_TOKEN = login_data['data']['jwtToken']
FEED_TOKEN = smartApi.getfeedToken()

# === User Input for Symbol ===
exchange = "NSE"
symbol_token = None



# === Get Instrument Token from Master File ===
response = requests.get("https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json")
instruments = response.json()

symbol_list = [inst['symbol'] for inst in instruments if inst['exch_seg'] == 'NSE']
results = []


while True:
    symbol_input = input("Enter stock symbol (e.g., RELIANCE, TCS): ").upper()
    
    matches = difflib.get_close_matches(symbol_input, symbol_list, n=1, cutoff=0.6)

    if matches:
        corrected_symbol = matches[0]
        confirm = input(f"✅ Did you mean: {corrected_symbol}? (Y/N): ").strip().lower()
        
        if confirm == 'y':
            print(f"✅ Proceeding with symbol: {corrected_symbol}")
            break  # Exit loop with valid symbol
        else:
            print("🔁 Let's try again...")
    else:
        print("❌ No close match found. Please try again.")

for item in instruments:
    if item['symbol'] == corrected_symbol and item['exch_seg'] == exchange:
        symbol_token = item['token']
        break

if not symbol_token:
    print(f"❌ Symbol '{corrected_symbol}' not found on {exchange}.")
    exit()


try:
    end = datetime.datetime.now()
    start = end - datetime.timedelta(days=10)  # Last 5 days for 5-minute candles

    params = {
        "exchange": exchange,
        "symboltoken": str(symbol_token),
        "interval": "FIVE_MINUTE",
        "fromdate": start.strftime('%Y-%m-%d %H:%M'),
        "todate": end.strftime('%Y-%m-%d %H:%M')
    }

    response = smartApi.getCandleData(params)
    oi_data = smartApi.getOIData(params)
    print("OI data:", oi_data)

    if 'data' not in response or not response['data']:
        print(f"⚠️ No historical data for {symbol_token}")
    else:
        # Convert data to DataFrame
        df = pd.DataFrame(response['data'], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])#"open_interest","open_interest_change_percentage"
        df['symbol'] = symbol_token
        print(df)


except Exception as e:
    print(f"❌ Error with {symbol_token}: {e}")




# === Setup WebSocket for Live Price ===
sws = SmartWebSocketV2(AUTH_TOKEN, API_KEY, CLIENT_CODE, FEED_TOKEN)
correlation_id = ""
mode = 3  # Full quote with OHLC
token_list = [{"exchangeType": 1, "tokens": [symbol_token]}]

def on_data(wsapp, message):

    dt=pd.DataFrame(message)
    ltp = (dt.at[0, 'last_traded_price'])/100

    oi_data = (df.at[0,'open_interest_change_percentage'])
    print("OI data:", oi_data)
    print("Raw message received:",ltp )

    print(message)
    try:
        if isinstance(message, str):
            parsed = json.loads(message)

        else:
            parsed = message  # Use directly if already dict
            
        # Add the rest of your parsing logic here
    except Exception as e:
        print("❌ Error parsing tick:", e)


def on_open(wsapp):
    print("✅ WebSocket Connected")
    sws.subscribe(correlation_id, mode, token_list)

def on_error(wsapp, error):
    print("❌ WebSocket Error:", error)

def on_close(wsapp):
    print("🔌 WebSocket Closed")

# === Assign WebSocket Events ===
sws.on_open = on_open
sws.on_data = on_data
sws.on_error = on_error
sws.on_close = on_close

print(f"🔎 Fetching live price for {symbol_token}...")
sws.connect()


