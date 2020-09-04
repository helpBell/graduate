from bs4 import BeautifulSoup
import requests
from datetime import datetime
def get_dividend_yield(code): #현재 DPS를 통한 예상 배당수익률
    url = "http://companyinfo.stock.naver.com/company/c1010001.aspx?cmp_cd="+code
    html = requests.get(url).text

    soup = BeautifulSoup(html, 'html5lib')
    dt_data = soup.select("td dl dt")
    dividend_yield = dt_data[-2].text
    dividend_yield = dividend_yield.split(' ')[1]
    dividend_yield = dividend_yield[:-1]
    return dividend_yield

def get_ebit_over_ev(code):  # to get EV/EBIT
    url = "http://companyinfo.stock.naver.com/company/c1010001.aspx?cmp_cd=" + code
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html5lib')
    td_data = soup.find('table', {'class': 'gHead03'})  # table 중에 class 이름이 저거인거
    if td_data is None: return
    td_data = td_data.select('tr:nth-of-type(4) td')
    td_data = td_data[0].text
    return td_data

def get_roa(code):  # ROA
    url = "http://companyinfo.stock.naver.com/company/c1010001.aspx?cmp_cd=" + code
    html = requests.get(url).text
    print(html)
    # soup = BeautifulSoup(html, 'html5lib')
    # print(soup)
    # td_data = soup.find('table', {'class': 'hTDdCYnFkT0 gHead01 all-width'})  # table 중에 class 이름이 저거인거
    # td_data = soup.select('table:nth-of-type(1)')
    # td_data = td_data[1].text
    # return td_data


def get_current_3years_treasury(): #일별 3년 만기 국채 수익률 가져오는 것, 가장 최신 일자로 반환
    url = "https://finance.naver.com/marketindex/interestDailyQuote.nhn?marketindexCd=IRR_GOVT03Y"
    html = requests.get(url).text
    soup = BeautifulSoup(html,'html5lib')
    td_data = soup.select("tr td")
    return td_data[1].text

def get_3years_treasury(): #3년 만기 국채 수익률 3개년치, 2019~2017, 다음 해가 되어도 써먹을 수 있도록 동적처리함
    url = "http://www.index.go.kr/potal/main/EachDtlPageDetail.do?idx_cd=1073"
    html = requests.get(url).text
    soup = BeautifulSoup(html,'html5lib')
    td_data = soup.find('table',{'class':'table_style_2'})
    result = soup.select('tr:nth-of-type(1) td')
    today_year = datetime.today().year - 1
    three_years_3years_treasury = {}
    for i in range(10,7,-1):
        three_years_3years_treasury[today_year] = result[i].text
        today_year-=1
    return three_years_3years_treasury


def get_previous_diviend_yield(code): #과거 배당 수익률 데이터 3년치
    url = "https://finance.naver.com/item/main.nhn?code="+code
    html = requests.get(url).text
    soup = BeautifulSoup(html,'html5lib')
    td_data = soup.find('table',{'class':'tb_type1 tb_num tb_type1_ifrs'})
    td_data = td_data.select('tr:nth-of-type(15) td')
    previous_3years_diviend_yield = {}
    today_year = datetime.today().year-1
    for i in range(3):
        previous_3years_diviend_yield[today_year] = td_data[i].text.strip()
        today_year-=1

    return previous_3years_diviend_yield

def calculate_estimated_divi_to_treasury(code):#최신 국채시가배당률 계산
    today_year = datetime.today().year - 1

    if (get_dividend_yield(code) == ""):
        estimated_dividend_yield = 0
    elif (float(get_dividend_yield(code)) == 0): #배당수익률 최신 지표가 없는 경우, 과거 배당수익률을 가져옴
        yield_history = get_previous_diviend_yield(code)
        if(yield_history[today_year] == "" or yield_history[today_year] =="-"):
            estimated_dividend_yield = 0
        else:
            estimated_dividend_yield = float(yield_history[today_year])

    else: #배당수익률 최신 지표가 있는 경우, 그걸 가져옴
        estimated_dividend_yield = float(get_dividend_yield(code))
    current_3years_treasury = float(get_current_3years_treasury())
    estimated_dividend_to_treasury = estimated_dividend_yield/current_3years_treasury

    return estimated_dividend_to_treasury


if __name__ == "__main__":
    print(get_previous_diviend_yield("000040"))
