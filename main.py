import sys
from PyQt5.QtWidgets import *
import Kiwoom
import time, datetime
from pandas import DataFrame
import numpy as np
from pymon import pymon
import LSTM_Stock as lstm
from DB_Control import FR_info_db, FS_info_db, KRX_list_db, price_info_db


if __name__ == "__main__":
    # DB 업데이트
    answer = input("환영합니다. \n\n주식 예측 프로그램을 가동하기에 앞서 DB 업데이트가 필요합니다.\n업데이트에는 10분이상 소요될 수 있습니다.\n\n업데이트를 수행하시겠습니까?[y/n]\n")
    if answer.lower() == "y":
        FR_info_db.func_FRinfo("재무비율정보.db")
        FS_info_db.func_FSinfo("재무제표정보.db")
        KRX_list_db.func_krxList("전체종목정보.db")
        price_info_db.func_price("종목별_가격정보.db")
        print("\n전체 DB 업데이트가 완료 되었습니다.\n")
    elif answer.lower() == "n":
        pass
    else:
        print("\n잘못된 입력입니다. 프로그램을 종료합니다.\n")
        exit()

    # 투자성향 입력 (1차 검증)
    print("-"*100)
    print("본인의 투자 성향에 맞는 투자방법을 골라주세요.\n")
    answer = input("\n1. 국채시가배당률(배당금 위주의 안전 투자) \n2. EV/EBIT(기업가치 중심 보수 투자) \n3. 그레이엄 전략(저평가주 중심 투자)\n[1/2/3]\n")
    buy_list = []
    pymon = pymon()
    if answer == '1':
        buy_list = pymon.run_dividend()
    elif answer == '2':
        buy_list = pymon.run_Greenblatt()
    elif answer == '3':
        buy_list = pymon.run_grahem()
    else:
        print("\n잘못된 입력입니다. 프로그램을 종료합니다.")
        exit()


     # 2차 검증 & 결과 도표 출력
    lstm.LSTM_Stock(buy_list)


   


