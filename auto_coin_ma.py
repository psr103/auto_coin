import time
import pyupbit
import datetime
import sqlite3
import requests

access = "UGBpNlkA7pNwQpp7ltp09wFrxxWmd0caMH4R42qV"
secret = "dufl9E9qxLfbmpSjdaIybdaBtyZbgYjl5hMCgbPy"
myToken = "xoxb-3124966504087-3139586700627-bQ1inanvp9c5pcllzzJOdBEX"

def post_message(token, channel, text):
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )

def get_target_price(ticker, k):
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_ma15(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="day", count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15

def get_balance(ticker):
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]


upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
c = sqlite3.connect("/home/ec2-user/auto_coin/data.db")
cur= c.cursor()
cur.execute("INSERT into 'transaction' (price) VALUES ('10000')")
while True:
    try:
        cur.execute("SELECT COUNT(*) from 'transaction'")
        result = cur.fetchall()
        is_bought = str(result)[2]
        print(is_bought)
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price("KRW-BTC", 0.5)
            ma15 = get_ma15("KRW-BTC")
            current_price = get_current_price("KRW-BTC")
            if target_price < current_price and ma15 < current_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    upbit.buy_market_order("KRW-BTC", krw*0.9995)
                    buying_price = str(int(current_price))
                    cur.execute("INSERT into 'transaction' (price) VALUES ('%s')") %(buying_price)
                    krw = get_balance("KRW")
                    btc = get_balance("BTC")
            #if is_bought == "0":
            #    print("true")
            #else:
            #    print("false")
            cur.execute("SELECT * from 'transaction'")
            result = cur.fetchall()
            bought_price = str(result[1])
            print(bought_price)
            if int(current_price) <= int(bought_price):
                btc = get_balance("BTC")
                if btc > 0.00008:
                    upbit.sell_market_order("KRW-BTC", btc*0.9995)
                    cur.execute("DELETE from 'transaction'")
                    krw = get_balance("KRW")
                    btc = get_balance("BTC")
                    
        else:
            btc = get_balance("BTC")
            if btc > 0.00008:
                upbit.sell_market_order("KRW-BTC", btc*0.9995)
                cur.execute("DELETE from 'transaction'")
                krw = get_balance("KRW")
                btc = get_balance("BTC")
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
