import pandas as pd
import sqlite3
import datetime
import FinanceDataReader as fdr

def func_krxList(name):
    df_krx = fdr.StockListing('KRX')

    con = sqlite3.connect(name)
    df_krx.to_sql("CorpList", con, if_exists="replace", index=True)

    con.close()
    print(name + " is updated")

if __name__=="__main__":
    func_krxList("전체종목정보.db")