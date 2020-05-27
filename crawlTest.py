from bs4 import BeautifulSoup
import requests
from datetime import datetime
def get_EVEBIT(code):
    url = "http://companyinfo.stock.naver.com/company/c1010001.aspx?cmp_cd="+code
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html5lib')

    #mktCapital
    dt_data = soup.select("table:nth-of-type(1) tr:nth-of-type(5) td:nth-of-type(1)")
    mktCapital = dt_data[0].text
    mktCapital = str.strip(mktCapital)

    #liabilities(부채)
    #dt_data = soup.select("table:nth-of-type(1) tr:nth-of-type(5) td:nth-of-type(1)")
    liabilities = dt_data[0].text
    liabilities = str.strip(liabilities)

    #cash(현금)
    # dt_data = soup.select("table:nth-of-type(1) tr:nth-of-type(5) td:nth-of-type(1)")
    cash = dt_data[0].text
    cash = str.strip(cash)

    #non-operating assets(비영업자산)
    # dt_data = soup.select("table:nth-of-type(1) tr:nth-of-type(5) td:nth-of-type(1)")
    Noa = dt_data[0].text
    Noa = str.strip(Noa)


    #EBIT(영업이익)
    #dt_data = soup.select("table:nth-of-type(1) tr:nth-of-type(5) td:nth-of-type(1)")
    EBIT = dt_data[0].text
    EBIT = str.strip(EBIT)

    EVEBIT = (mktCapital+liabilities-cash-Noa)/EBIT

    return EVEBIT

def get_ebit_over_ev(code):  # to get EV/EBIT
    url = "http://companyinfo.stock.naver.com/company/c1010001.aspx?cmp_cd=" + code
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html5lib')
    # print(soup)
    td_data = soup.find('table', {'class': 'gHead03'})  # table 중에 class 이름이 저거인거
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
    return td_data



if __name__ == "__main__":
    print(get_ebit_over_ev("005930"))