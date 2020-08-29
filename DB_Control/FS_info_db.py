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
options.add_argument('headless') # headless: 브라우저X
driver = webdriver.Chrome('C:\\Users\hawoo\Desktop\SKKU CS\Graduate\chromedriver.exe', options=options)

def crawl_fs_data(Symbol):
    fs_url=f"http://comp.fnguide.com/SVO2/ASP/SVD_Finance.asp?pGB=1&gicode={Symbol}"
    driver.get(fs_url)

    fs_page = driver.page_source
    fs_tables = pd.read_html(fs_page)

    for i in range(len(fs_tables)):
        for j in range(20):
            try: driver.find_element_by_xpath(f'//*[@id="grid{i+1}_{j+1}"]').click()
            except NoSuchElementException: continue

    fs_page = driver.page_source
    fs_tables = pd.read_html(fs_page)

    # 포괄손익계산서 Income statement IS
    fs_is = fs_tables[0]
    # 인덱스 이름(계정목록들)을 지정해주고 빼주기. 첫째 열이 IFRS(연결), IFRS(개별), GAAP(개별)과 같이 상황에 따라 다름
    first_column=fs_is.columns[0]
    fs_is.index=fs_is[first_column].values
    # inplace는 변수 대입 불필요. axis=1은 열기준
    fs_is.drop([first_column,'전년동기','전년동기(%)'], inplace=True, axis=1)
    # 행 목록 필요없는 부분 제거
    for i, name in enumerate(fs_is.index):
        if '참여한' in name:
            name = '*' + name.strip().replace('계산에 참여한 계정 감추기','')
            fs_is.rename(index={str(fs_is.index[i]):str(name)}, inplace=True)

    # 재무상태표 Balance Sheet BS
    fs_bs = fs_tables[2]
    # 인덱스 이름(계정목록들)을 지정해주고 빼주기. 첫째 열이 IFRS(연결), IFRS(개별), GAAP(개별)과 같이 상황에 따라 다름
    first_column=fs_bs.columns[0]
    fs_bs.index=fs_bs[first_column].values
    # inplace는 변수 대입 불필요. axis=1은 열기준
    fs_bs.drop([first_column], inplace=True, axis=1)
    # 행 목록 필요없는 부분 제거
    for i, name in enumerate(fs_bs.index):
        if '참여한' in name:
            name = '*'+name.strip().replace('계산에 참여한 계정 감추기','')
            fs_bs.rename(index={str(fs_bs.index[i]):str(name)}, inplace=True)

    # 현금흐름표 statement of cash flow CF
    fs_cf = fs_tables[4]
    # 인덱스 이름(계정목록들)을 지정해주고 빼주기. 첫째 열이 IFRS(연결), IFRS(개별), GAAP(개별)과 같이 상황에 따라 다름
    first_column=fs_cf.columns[0]
    fs_cf.index=fs_cf[first_column].values
    # inplace는 변수 대입 불필요. axis=1은 열기준
    fs_cf.drop([first_column], inplace=True, axis=1)
    # 행 목록 필요없는 부분 제거
    for i, name in enumerate(fs_cf.index):
        if '참여한' in name:
            name = '*'+name.strip().replace('계산에 참여한 계정 감추기','')
            fs_cf.rename(index={str(fs_cf.index[i]):str(name)}, inplace=True)

    fs_df=pd.concat([fs_is,fs_bs,fs_cf])
    return fs_df

# 증권 종목쪽 데이터는 재무내용이 달라서 ElementNotInteractableException 에러발생 따로 처리
def crawl_er_fs_data(Symbol):

    fs_url=f"http://comp.fnguide.com/SVO2/ASP/SVD_Finance.asp?pGB=1&gicode={Symbol}"
    driver.get(fs_url)

    fs_page = driver.page_source
    fs_tables = pd.read_html(fs_page)

    for i in range(len(fs_tables)):
        for j in range(45):
            # print(i, j)
            try :
                driver.find_element_by_xpath(f'//*[@id="grid{i+1}_{j+1}"]').click()

            except NoSuchElementException :
                continue
            except ElementNotInteractableException:
                try:
                    print('wait...click')
                    element = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, f'//*[@id="grid{i+1}_{j+1}"]')))
                    element.click()
                    print('click ok')
                except TimeoutException:
                    print("timeout")
                    continue

    fs_page = driver.page_source
    fs_tables = pd.read_html(fs_page)

    fs_is = fs_tables[0]
    first_column=fs_is.columns[0]
    fs_is.index=fs_is[first_column].values
    fs_is.drop([first_column,'전년동기','전년동기(%)'], inplace=True, axis=1)
    for i, name in enumerate(fs_is.index):
        if '참여한' in name:
            name = '*'+name.strip().replace('계산에 참여한 계정 감추기','')
            fs_is.rename(index={str(fs_is.index[i]):str(name)}, inplace=True)

    fs_bs = fs_tables[2]
    first_column=fs_bs.columns[0]
    fs_bs.index=fs_bs[first_column].values
    fs_bs.drop([first_column], inplace=True, axis=1)
    for i, name in enumerate(fs_bs.index):
        if '참여한' in name:
            name = '*'+name.strip().replace('계산에 참여한 계정 감추기','')
            fs_bs.rename(index={str(fs_bs.index[i]):str(name)}, inplace=True)

    fs_cf = fs_tables[4]
    first_column=fs_cf.columns[0]
    fs_cf.index=fs_cf[first_column].values
    fs_cf.drop([first_column], inplace=True, axis=1)
    for i, name in enumerate(fs_cf.index):
        if '참여한' in name:
            name = '*'+name.strip().replace('계산에 참여한 계정 감추기','')
            fs_cf.rename(index={str(fs_cf.index[i]):str(name)}, inplace=True)

    fs_df=pd.concat([fs_is,fs_bs,fs_cf])
    return fs_df


# SQLite3 DB 불러오기
con = sqlite3.connect("전체종목정보.db")
code_data = pd.read_sql("SELECT * FROM CorpList", con)
con.close()

code_data = code_data[['Symbol', 'Name']]


# 재무제표 SQLite3 DB로 저장하기
con = sqlite3.connect("재무제표정보.db")

for i, code in enumerate(code_data['Symbol']):

    try:
        fs_data = crawl_fs_data('A'+str(code))
        fs_data.to_sql(code, con, if_exists="replace", index=True)
    except ValueError:
        print("temporary error")
        print(code + " Value error")
        continue
    # 투자회사 종목 096300에 에러. fnguide상으로는 안내페이지 나옴
    except ImportError:
        print("temporary error")
        print(code + " Import error")
        continue
    # 이상한 종목 ex. 094800 맵스리얼티1 168490 한국패러랠 같은 종목은 fnguide에 정보가 없어서(안내페이지 x) 함수에서 오류 (전년동기, %)
    except KeyError:
        print("temporary error")
        print(code + " key error")
        continue
    # 위 keyerror랑 같은 문제, 함수 구성에 따라 type error 발생 (참여한 부분)
    except TypeError:
        print("temporary error")
        print(code + " Type error")
        continue
    # 증권 종목 별도 함수이용 처리
    except ElementNotInteractableException:
        print(code + "not interactable")
        fs_data = crawl_er_fs_data('A'+str(code))
        fs_data.to_sql(code, con, if_exists="replace", index=True)
        continue

con.close()