import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common import keys

site = 'https://www.sec.gov/cgi-bin/browse-edgar?company=americredit&owner=exclude&action=getcompany'
driver = webdriver.Chrome()
driver.get(site)
next_ = '//*[@id="contentDiv"]/form/input'
next_element = driver.find_element_by_xpath(next_)
next_element.click()
next2_ = '//*[@id="contentDiv"]/form/input[2]'
next2_element = driver.find_element_by_xpath(next2_)
next2_element.click()

AMCAR20181 = '//*[@id="seriesDiv"]/table/tbody/tr[6]/td[1]/a'
AMCAR20181_element = driver.find_element_by_xpath(AMCAR20181)
AMCAR20181_element.click()

search = '//*[@id="contentDiv"]/div[2]/form/table/tbody/tr/td[2]'
search_element = driver.find_element_by_xpath(search)
search_element.click()

