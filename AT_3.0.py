from tracemalloc import start
import pyupbit
import time
import datetime
import schedule
import pandas as pd
import openpyxl
import matplotlib.pyplot as plt
import trade_utility as ut
from Upb_Get_Data import get_target_price, get_high_price, get_current_price, get_ma5, get_start_time, return_coin_name, get_ticker_list, get_balance
from upbit_trade_record import order_record, trade_record, get_win_rate, cal_CAGR

Debug_ = False       # True: 매매 API 호출 안됨, False: 실제로 매매 API 호출

program_version = 'Cyptocurrency Trade Bot v2.7'
strategy = "Larry's Volatility Breakout System"
key_path = '/home/ubuntu/upbit_key.txt' if Debug_ is False else 'upbit_key.txt'
file_path = '/home/ubuntu/trading_record.xlsx' if Debug_ is False else 'trading_record.xlsx'

k = 0.5
coin_nums = 5   # 일일 트레이딩 종목 수
stop_loss = 0.05   # 손절매 기준
tickers = ['KRW-BTC', 'KRW-ETH', 'KRW-XRP', 'KRW-SOL', 'KRW-AXS', 'KRW-MANA']

# Load account
with open(key_path) as f:
    lines = f.readlines()
    access = lines[0].strip()
    secret = lines[1].strip()
    upbit = pyupbit.Upbit(access, secret)

'''현재 보유 자산 현황 확인 / 초기투자금액 및 투자 시작일 설정 / 프로그램 실행시 1회만 실행'''
def trade_start_check():
    buy_list = get_balance(access, secret) 
    total_balance = upbit.get_balance("KRW") + upbit.get_amount('ALL')
    holdings = []
    try:
        for b in buy_list:
            holding = return_coin_name(b)
            holdings.append(holding)
        hold_list = ", ".join(holdings)
    except:
        hold_list = "None"

    record_data = [datetime.date.today(), total_balance, pyupbit.get_ohlcv("KRW-BTC", count=2).iloc[-2]['close']]

    try:
        df = pd.read_excel(file_path, sheet_name = 'return_record')
    except FileNotFoundError:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'return_record'
        ws.append(['Date','total_assets','BTC'])
        ws.append(record_data)
        wb.save(file_path)
        df = pd.read_excel(file_path, sheet_name = 'return_record')

    T_start_date = df.iloc[0]['Date']
    T_start_date = datetime.date(T_start_date.year,T_start_date.month,T_start_date.day)
    balance_init = df.iloc[0]['total_assets']

    ut.post_message('-'*35 + '\n' + program_version + '\n' + strategy +
                    '\n' + 'Running Program on ' + str(datetime.datetime.now())[:16] + '\n' + '-'*35)
    ut.post_message("Total Assets : {:0,.0f}won".format(total_balance)
                    + '\n' + "Cash : {:0,.0f}won".format(upbit.get_balance("KRW"))
                    + '\n' + "Holding Coins : " + hold_list)
    return T_start_date, balance_init

'''일일 트레이딩 데이터 셋업 / 매수종목 리스트 초기화 / 매일 09:00 실행'''
def trade_setup():
    start_time = get_start_time()
    end_time = start_time + datetime.timedelta(hours=23)
    sell_time = start_time + datetime.timedelta(days=1) - datetime.timedelta(minutes=5)
    buy_amt = (upbit.get_balance("KRW") + upbit.get_amount('ALL')) / coin_nums
    tomorrow = start_time + datetime.timedelta(days=1)
    set_time1 = datetime.datetime(year=tomorrow.year,
                                  month=tomorrow.month,
                                  day=tomorrow.day,
                                  hour=9,
                                  minute=0,
                                  second=30)
    set_time2 = set_time1 + datetime.timedelta(seconds=10)

    return start_time, end_time, sell_time, buy_amt, set_time1, set_time2

start_time, end_time, sell_time, buy_amt, set_time1, set_time2 = trade_setup()
T_start_date, balance_init = trade_start_check()
ut.post_message("Auto Trade Start...")

#schedule.every().day.at("09:00").do(daily_report)
#schedule.every().day.at("09:00").do(trade_setup)

while True:
    try:
        schedule.run_pending()
        now = datetime.datetime.now()
        if set_time1 < now < set_time2:
            start_time, end_time, sell_time, buy_amt, set_time1, set_time2 = trade_setup()


    except Exception as e:
        print(e)
        ut.post_message(str(e))
        time.sleep(1)
