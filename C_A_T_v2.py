import pyupbit
import time
import datetime
import telegram
import schedule
import pandas as pd
import requests

access = "2nUWiu0PnEtvlUlpiq5PJGc0b1N4ix5fPox6KRYA"
secret = "AmSsPXpxvx12UEZsxBIIPyLU0ZVsDiMl2cSLtX5X"

token = "5094155373:AAGwbZOBTw990tvU6TIdHWilsHP7R95T-qM"
chat_id = "5033041863"

def post_message(chat_id, message):
	bot = telegram.Bot(token)
	bot.sendMessage(chat_id=chat_id, text=message)

def get_target_price(ticker):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_daily_ohlcv_from_base(ticker, base=reset_time)
    target_price = df.iloc[-2]['close'] + (df.iloc[-2]['high'] - df.iloc[-2]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_daily_ohlcv_from_base(ticker, base=reset_time)
    start_time = df.index[-1]
    return start_time

def get_ma5(ticker):
    """5일 이동 평균선 조회"""
    df = pyupbit.get_daily_ohlcv_from_base(ticker, base=reset_time)
    ma5 = df['close'].rolling(5).mean().iloc[-1]
    return ma5

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

def get_ticker_list():
    """ 최근 5일 평균 거래대금 상위 10개 종목 선정 """    
    Ticker = pyupbit.get_tickers(fiat="KRW")
    DF = pd.DataFrame(columns = ["ticker","trading amount"])
    post_message(chat_id, "매매 종목 선정중...")
    print("매매 종목 선정중...")
    for t in Ticker:
        df = pyupbit.get_ohlcv(t, period=1, interval="day", count=6) 
        df["amount"] = df["close"] * df["volume"]
        df = df.iloc[:-1]
        mean_amount = df["amount"].mean()   
        DF.loc[len(DF)]=[t,mean_amount]
        time.sleep(0.1)
    DF = DF.sort_values(by=['trading amount'], ascending=False, axis=0).iloc[:10]
    ticker_list = DF["ticker"].tolist()

    return ticker_list

def get_balance():
    balance = upbit.get_balances()
    total_balance = 0
    for b in balance:
        if b['currency'] == "KRW":
            total_balance += float(b["balance"])
        else:
            ticker = "KRW-" + b['currency']
            total_balance += upbit.get_amount(ticker)
    return total_balance

def auto_trade_start():
    post_message(chat_id,str(datetime.date.today()))
    balance_now = get_balance()
    FnL = (balance_now / balance_init - 1)*100
    post_message(chat_id,"원화잔고 : {:0,.0f}원".format(upbit.get_balance("KRW")))
    post_message(chat_id, "총 평가금액 : {:0,.0f}원".format(balance_now))
    post_message(chat_id,"누적 수익률 : {:0,.2f}%".format(FnL))
    global ticker
    ticker = get_ticker_list()
    today_list = []
    for t in ticker:
        today_list.append(return_coin_name(t))
    post_message(chat_id,"매매 종목 선정 완료..")
    post_message(chat_id,"오늘의 매매 종목 : ")
    post_message(chat_id,today_list)
    post_message(chat_id, "자동매매 시작..")
    print("자동매매 시작..")

def trading_check():
    post_message(chat_id,"System running check.. OK")

def return_coin_name(ticker):
    url = "https://api.upbit.com/v1/market/all"
    coinname = requests.get(url)  # api 데이터 호출
    coinname = coinname.json()  # coinname으로 가져온 json 데이터를 list로 저장
    coinname_df = pd.DataFrame(coinname).set_index("market")
    coin_name = coinname_df.loc[ticker, "english_name"]
    return coin_name

upbit = pyupbit.Upbit(access, secret)

k = 0.5
reset_time = 9    # 트레이딩 기준시간
trading_size = 5   # 일일 트레이딩 종목 수
loss_cut_ratio = 0.05   # 손절매 기준
balance_init = 1000000

# 자동매매 시작
auto_trade_start()
schedule.every().day.at("09:00").do(auto_trade_start)
schedule.every().hour.at(":30").do(trading_check)

while True:
    try:
        schedule.run_pending()
        count = len(upbit.get_balances())-1
        buy_amount = upbit.get_balance("KRW")/(trading_size-count)
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)
		
        if start_time < now < end_time - datetime.timedelta(seconds=30):
            for t in ticker:
                target_price = get_target_price(t)
                ma5 = get_ma5(t)
                current_price = get_current_price(t)
                balance = upbit.get_balance(t)
                loss_cut_price = upbit.get_avg_buy_price(t) * (1 - loss_cut_ratio)  # 5%이상 손실발생시 손절매
                krw = upbit.get_balance("KRW")
                if target_price < current_price and ma5 < current_price:
                    if balance == 0 and krw > 5000:
                        upbit.buy_market_order(t, buy_amount*0.9995)
                        post_message(chat_id, return_coin_name(t) + "  목표가 돌파.. 매수")
                if balance > 0 and current_price < loss_cut_price:
                    upbit.sell_market_order(t, balance)
                    post_message(chat_id,return_coin_name(t)+"  손절매")

        else:
            for t in ticker:
                balance = upbit.get_balance(t)
                if balance > 0:
                    upbit.sell_market_order(t, balance)
                    post_message(chat_id, return_coin_name(t) + "  매도 청산")
        time.sleep(1)

    except Exception as e:
        print(e)
        post_message(chat_id, str(e))
        time.sleep(1)
