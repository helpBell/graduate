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

class pymon:
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

    def update_buy_list(self, buy_list):
        f = open("buy_list.txt", "wt", encoding='UTF8')
        for code in buy_list:
            f.writelines("매수;%s;시장가;10;0;매수전\n" % (code))
        f.close()
        print("list updated")

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

    # 국채시가배당률은 ‘현금배당 수익률’을 ‘3년 만기 국채 수익률’로 나눈 값 <- 이것으로 순위 측정
    def run_dividend(self):
        buy_list = []

        for code in self.kospi_codes:
            ret = self.buy_check_by_dividend_algorithm(code)
            if ret[0] == 1:
                print(code, ret)
                buy_list.append((code,ret[1]))
            else:
                print(code, "Fail")
            sorted_list = sorted(buy_list, key=lambda t: t[1], reverse=True)
            print(sorted_list)

        for i in range(0, 5):
            code = sorted_list[i][0]
            buy_list1.append(code)

        # self.update_buy_list(buy_list1)
        return buy_list1

    # 그린블라트 마법 공식 부분
    def run_Greenblatt(self):
        buy_list1 = []
        buy_list2 = []
        buy_list = []

        # EV/EVITDA 부분
        for code in self.kospi_codes:
            ret = crawl.get_ebit_over_ev(code)
            if ret is None :
                print(code, "Fail")
            else:
                print(code, ret)
                buy_list1.append((code, ret))
        sorted_list1 = sorted(buy_list1, key=lambda t: t[1], reverse=True)
        buy_list1 = []
        for i in range(0, 10):
            code = sorted_list1[i][0]
            buy_list1.append([code, i])

        # ROIC 부분
        for code in self.kospi_codes:
            ret = crawl.get_roic(code)
            if ret is None :
                print(code, "Fail")
            else:
                print(code, ret)
                buy_list2.append((code, ret))
        sorted_list2 = sorted(buy_list2, key=lambda t: t[1], reverse=True)
        buy_list2 = []
        for i in range(0, 10):
            code = sorted_list2[i][0]
            buy_list2.append([code, i])
        
        # 합쳐서 종합 순위 측정
        for i in range(10):
            for j in buy_list2:
                if buy_list1[i][0] == j[0]: 
                    buy_list.append([buy_list1[i][0],buy_list1[i][1]+j[1]])
            buy_list.append([buy_list1[i][0],buy_list1[i][1]*10])
            buy_list.append([buy_list2[i][0],buy_list2[i][1]*10])

        sorted_list = sorted(buy_list, key=lambda t: t[1])
        buy_list = []
        for i in range(0, 5):
            code = sorted_list[i][0]
            buy_list.append(code)
        # self.update_buy_list(buy_list)
        return buy_list

    # 그레이엄 전략
    def run_grahem(self):
        buy_list=[]

        for code in self.kospi_codes:
            per_data = crawl.get_per(code)
            debt_ratio_data = crawl.get_debt_ratio(code)
            if per_data is None or debt_ratio_data is None :
                print(code, "Fail")
            elif 0<=per_data<=5 and debt_ratio_data<=50:
                print(code, per_data, debt_ratio_data)
                buy_list.append(code)
            else:
                print("Inappropriate")
        # self.update_buy_list(buy_list)
        return buy_list

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pymon = pymon()
    # pymon.run_dividend()
    # pymon.run_Greenblatt()
    # pymon.run_grahem()
    print(pymon.kospi_codes)


