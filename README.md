# FDXDATA
Project of API from Angle one SmartAPI to access data and us for real time moments and Breakouts
# 📈 Angel One SmartAPI Stock Data Fetcher (with OI + Live Price via WebSocket)

This Python script connects to Angel One's SmartAPI to:

- 🔒 Log in using your credentials and TOTP
- 🧠 Let you input a stock symbol (with fuzzy match suggestions)
- 📊 Fetch historical 5-minute candle data for the last 10 days
- 📉 Fetch Open Interest (OI) data for the selected stock
- 📡 (Optional) Set up a live WebSocket stream for real-time LTP (last traded price)

---

## 🚀 Features

- Auto-login using API key, client code, password, and TOTP secret
- Intelligent fuzzy matching for stock symbol entry
- Fetch historical candle data (OHLCV) from the SmartAPI
- Retrieve Open Interest (OI) data
- (Optional) Live market feed via Smart WebSocket v2

---

## 🧰 Requirements
requests
pyotp
pandas
tabulate
SmartApi

```bash
pip install requests pyotp pandas tabulate
pip install git+https://github.com/angel-one/smartapi-python.git
```
Replace the placeholders in the script:

#Changement
API_KEY = "your_api_key"
CLIENT_CODE = "your_client_code"
PASSWORD = "your_password"
TOTP_SECRET = "your_totp_secret"

#📁 Sample Output
Enter stock symbol (e.g., RELIANCE, TCS): relince
✅ Did you mean: RELIANCE? (Y/N): y
✅ Proceeding with symbol: RELIANCE
[historical candle data table]
OI data: { ... }


