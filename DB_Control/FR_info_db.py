import pandas as pd
import sqlite3
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, TimeoutException
import time
import datetime

options = webdriver.ChromeOptions()
options.add_argument('headless') # headless: 브라우저가 안뜸
driver = webdriver.Chrome('C:\\Users\\hawoo\\Desktop\\SKKU CS\\Graduate\\chromedriver.exe', options=options)

# 재무비율 데이터프레임 형태로 만들어 주기
def make_fr_dataframe(firm_code):
    fr_url=f"http://comp.fnguide.com/SVO2/ASP/SVD_Financeratio.asp?pGB=1&gicode={firm_code}"
    driver.get(fr_url)

    fr_page = driver.page_source
    fr_tables = pd.read_html(fr_page)

    #열 갯수가 연결재무재표와 다름
    for i in range(25):
        
        try :
            driver.find_element_by_xpath(f'//*[@id="grid{1}_{i}"]').click()

        except NoSuchElementException :
            continue
        except ElementNotInteractableException:
            try:
                print('wait...click')
                element = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, f'//*[@id="grid{1}_{i}"]')))
                element.click()
                print('click ok')
            except TimeoutException:
                print("timeout")
                continue

    fr_page = driver.page_source
    fr_tables = pd.read_html(fr_page)

    fr_df = fr_tables[0]

    # 인덱스 이름(계정목록들)을 지정해주고 빼주기
    first_column=fr_df.columns[0]
    fr_df.index=fr_df[first_column].values
    # inplace는 변수 대입 안해줘도 되고 axis=1은 열기준
    fr_df.drop([first_column], inplace=True, axis=1) 

    # 행 목록 필요없는 부분 제거
    for i, name in enumerate(fr_df.index):
        if '참여한' in name:
            name = '*'+name.strip().replace('계산에 참여한 계정 감추기','')
            fr_df.rename(index={str(fr_df.index[i]):str(name)}, inplace=True)

    return fr_df

def func_FRinfo(name):
    # SQLite3 DB 불러오기
    con = sqlite3.connect("전체종목정보.db")
    code_data = pd.read_sql("SELECT * FROM CorpList", con)
    con.close()

    code_data = code_data[['Symbol', 'Name']]

    # 재무비율 SQLite3 DB로 저장하기
    con = sqlite3.connect(name)

    for i, code in enumerate(code_data['Symbol']):
        try:
            fr_data = make_fr_dataframe('A'+str(code))
            fr_data.to_sql(code, con, if_exists="replace", index=True)
        except ValueError:
            print("temporary error")
            print(code + " Value error")
            continue
        # 투자회사 종목 096300 가 이 에러가 나옴. fnguide상으로는 안내페이지 나옴
        except ImportError:
            print("temporary error")
            print(code + " Import error")
            continue
        # 이상한 종목 ex. 094800 맵스리얼티1 168490 한국패러랠 같은 종목은 fnguide에 정보가 없어서(안내페이지 x) 함수에서 오류가 남 (전년동기, %)
        except KeyError:
            print("temporary error")
            print(code + " key error")
            continue
        # 위 keyerror랑 같은 문제인데 함수를 어떻게 짰냐에 따라 type error도 남 (참여한 부분)
        except TypeError:
            print("temporary error")
            print(code + " Type error")
            continue
        except ElementNotInteractableException:
            continue
    con.close()
    print(name + " is updated")

if __name__=="__main__":
    func_FRinfo("재무비율정보.db")

