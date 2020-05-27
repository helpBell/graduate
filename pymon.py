import sys
from PyQt5.QtWidgets import *
import Kiwoom
import time
from pandas import DataFrame
import datetime
import crawl
import numpy as np


MARKET_KOSPI = 0
MARKET_KOSDAQ = 10


class PyMon:
    def __init__(self):
        self.kiwoom = Kiwoom.Kiwoom()
        self.kiwoom.comm_connect()
        self.get_code_list()

    def is_it_float(self,num): #들어온 문자가 소수인지 파악하는 함수, 문자가 만약 빈칸이나 '-'인 경우, false를 반환
        try:
            float(num)
            return True
        except ValueError:
            return False

    def run(self):
        buy_list = []
        num = len(self.kosdaq_codes)
        split_kosdaq_codes = self.kosdaq_codes[0:20]

        for i, code in enumerate(split_kosdaq_codes):
            print(i, '/', num)
            if self.check_speedy_rising_volume(code):
                buy_list.append(code)

        self.update_buy_list(buy_list)

    def get_code_list(self):
        self.kospi_codes = self.kiwoom.get_code_list_by_market(MARKET_KOSPI)
        self.kosdaq_codes = self.kiwoom.get_code_list_by_market(MARKET_KOSDAQ)

    def get_ohlcv(self, code, start):
        self.kiwoom.ohlcv = {'date':[], 'open':[], 'high':[], 'low':[], 'close':[], 'volume':[]}

        self.kiwoom.set_input_value("종목코드", code)
        self.kiwoom.set_input_value("기준일자", start)
        self.kiwoom.set_input_value("수정주가구분", 1)
        self.kiwoom.comm_rq_data("opt10081_req","opt10081", 0, "0101")
        time.sleep(0.2)

        dog = DataFrame(self.kiwoom.ohlcv, columns=['open','high', 'low', 'close', 'volume'], index=self.kiwoom.ohlcv['date'])
        return dog

    def check_speedy_rising_volume(self, code):
        today = datetime.datetime.today().strftime("%Y%m%d")
        df = self.get_ohlcv(code, today)
        volumes = df['volume']

        if len(volumes) < 21:
            return False

        sum_vol20 = 0
        today_vol = 0

        for i, vol in enumerate(volumes):
            if i == 0:
                today_vol = vol
            elif 1<= i <= 20:
                sum_vol20 += vol
            else:
                break

        avg_vol20 = sum_vol20/20
        if today_vol > avg_vol20*10:
            return True
        else:
            return False

    def update_buy_list(self, buy_list):
        f = open("buy_list.txt", "wt", encoding='UTF8')
        for code in buy_list:
            f.writelines("매수;%s;시장가;10;0;매수전\n" % (code))
        f.close()

    def get_min_max_diviend_to_treasury(self, code):#3년 동안의 국채시가배당률 구하고, 최소랑 최대 반환
        previous_dividend_yield = crawl.get_previous_diviend_yield(code)
        three_years_treasury = crawl.get_3years_treasury()
        today = datetime.datetime.now()
        curr_year = today.year
        previous_dividend_to_treasury = {}

        for year in range(curr_year-3,curr_year):
            if year in previous_dividend_yield.keys() and year in three_years_treasury.keys():
                if(self.is_it_float(previous_dividend_yield[year])):
                    ratio = float(previous_dividend_yield[year]) / float(three_years_treasury[year])
                else:
                    ratio = 0

                previous_dividend_to_treasury[year] = ratio

        min_ratio = min(previous_dividend_to_treasury.values())
        max_ratio = max(previous_dividend_to_treasury.values())

        return (min_ratio, max_ratio)

    def buy_check_by_dividend_algorithm(self,code): #위 함수에서 3년동안의 국채시가배당률 구하고 그 최대값을 현재 국채시가배당률과 비교해서 매수의견 내놓는 알고리즘
        estimated_dividend_to_treasury = crawl.calculate_estimated_divi_to_treasury(code)
        (min_ratio,max_ratio) = self.get_min_max_diviend_to_treasury(code)

        if estimated_dividend_to_treasury > max_ratio:
            return(1, estimated_dividend_to_treasury)
        else:
            return (0,estimated_dividend_to_treasury)

    def run_dividend(self):
        buy_list = []

        for code in self.kospi_codes:
            print("Check: ",code)
            ret = self.buy_check_by_dividend_algorithm(code)

            if ret[0] == 1:
                print("Pass",ret)
                buy_list.append((code,ret[1]))
            else:
                print("Fail",ret)

            sorted_list = sorted(buy_list, key=lambda t: t[1], reverse=True)
            print(sorted_list)

        for i in range(0, 5):
            code = sorted_list[i][0]
            buy_list.append(code)


        self.update_buy_list(buy_list)

    def run_evebitda(self):
        buy_list1 = []
        buy_list = []

        for code in self.kospi_codes:
            print("Check: ",code)

            ret = crawl.get_ebit_over_ev(code)

            if ret is None :
                print("Fail", ret)
            else:
                print("Pass", ret)
                buy_list.append((code, ret))
            print(buy_list)

        sorted_list = sorted(buy_list, key=lambda t: t[1], reverse=True)
        for i in range(0, 5):
            code = sorted_list[i][0]
            buy_list1.append(code)


        self.update_buy_list(buy_list1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pymon = PyMon()
    pymon.run_evebitda()

