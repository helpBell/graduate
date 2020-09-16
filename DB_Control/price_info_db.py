import pandas as pd
import sqlite3
import datetime
import FinanceDataReader as fdr


def func_price(name):

    # SQLite3 DB 불러오기
    con = sqlite3.connect("전체종목정보.db")
    code_data = pd.read_sql("SELECT Symbol FROM CorpList", con)
    con.close()

    # SQLite3 DB로 저장하기
    con = sqlite3.connect(name)

    # 20년간 가격데이터 종목별 테이블로 저장 (2000년 부터)
    for i, code in enumerate(code_data['Symbol']):
        price_data = fdr.DataReader(code, '2000-01-01')
        price_data.to_sql(code, con, if_exists="replace", index=True)

    con.close()
    print(name + " is updated")

if __name__=="__main__":
    func_price("종목별_가격정보.db")



