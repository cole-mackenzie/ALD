import xml.etree.ElementTree as et
import requests
import pandas as pd
import time
import my_functions
from my_functions import get_rss_links, construct_url, wipe_file, no_print

#establish the auto loan asset class

asset_list = []

class asset:
			
	def __init__(self, month, balance, fico, dq_status):
		self.month = month
		self.balance = balance
		self.fico = fico
		self.dq_status = dq_status
		asset_list.append(self)

rss_file = r'C:\Users\dcsma\Documents\Python XML Testing\RSS.csv'
rss_urls = []
get_rss_links(rss_file,rss_urls)

temp_rss = r'C:\Users\dcsma\Documents\Python XML Testing\XMLs\temp_RSS.xml'
temp_xml = r'C:\Users\dcsma\Documents\Python XML Testing\XMLs\temp_xml.xml'

for url in rss_urls:
	asset_list = []
	rss_get = requests.get(url)
	rss_content = rss_get.content
	rss_get.close()
	time.sleep(10)
	with open(temp_rss, 'wb') as file:
		file.write(rss_content)
	rss_tree = et.parse(temp_rss)
	rss_root = rss_tree.getroot()
	abs_ee_links = []
	for child in rss_root.findall('{http://www.w3.org/2005/Atom}entry'):
		for element in child:
			for attribute in element:
				if attribute.tag  == '{http://www.w3.org/2005/Atom}filing-href':
					abs_ee_links.append(attribute.text)
	for child in rss_root.findall('{http://www.w3.org/2005/Atom}company-info'):
		for element in child.findall('{http://www.w3.org/2005/Atom}conformed-name'):
			deal = element.text
	filing_page = abs_ee_links[0]
	page = requests.get(filing_page)
	time.sleep(10)
	tables = pd.read_html(page.text)
	time.sleep(5)
	filing = tables[0]
	page.close()
	df = pd.DataFrame(data=filing)
	data = requests.get(construct_url(filing_page,df))
	time.sleep(10)
	tape = data.content
	data.close()
	with open(temp_xml, 'wb') as file:
		file.write(tape)
	data_tape = et.parse(temp_xml)
	root = data_tape.getroot()
	for child in root.findall('{http://www.sec.gov/edgar/document/absee/autoloan/assetdata}assets'):
		month = child.find('{http://www.sec.gov/edgar/document/absee/autoloan/assetdata}reportingPeriodEndingDate').text
		balance = float(child.find('{http://www.sec.gov/edgar/document/absee/autoloan/assetdata}reportingPeriodActualEndBalanceAmount').text)
		try:
			dq_status = float(child.find('{http://www.sec.gov/edgar/document/absee/autoloan/assetdata}currentDelinquencyStatus').text)
		except:
			dq_status = 0
		try:
			fico = float(child.find('{http://www.sec.gov/edgar/document/absee/autoloan/assetdata}obligorCreditScore').text)
		except:
			fico = 0
		with no_print():
			asset(month, balance, fico, dq_status)

	lt_500_dq = 0
	lt_500_bal = 0
	dq_501_600 = 0
	bal_501_600 = 0
	dq_601_700 = 0
	bal_601_700 = 0
	dq_701 = 0
	bal_701 = 0

	report_month = asset_list[1].month

	for x in asset_list:
		if x.fico <= 500:
			if x.dq_status > 60:
				lt_500_dq = lt_500_dq + x.balance
				lt_500_bal = lt_500_bal + x.balance
			else:
				lt_500_bal = lt_500_bal + x.balance
		elif x.fico > 500 and x.fico <= 600:
			if x.dq_status > 60:
				dq_501_600 = dq_501_600 + x.balance
				bal_501_600 = bal_501_600 + x.balance
			else:
				bal_501_600 = bal_501_600 + x.balance
		elif x.fico > 600 and x.fico <= 700:
			if x.dq_status > 60:
				dq_601_700 = dq_601_700 + x.balance
				bal_601_700 = bal_601_700 + x.balance
			else:
				bal_601_700 = bal_601_700 + x.balance
		elif x.fico > 700:
			if x.dq_status > 60:
				dq_701 = dq_701 + x.balance
				bal_701 = bal_701 + x.balance
			else:
				bal_701 = bal_701 + x.balance

	dq_data = {'Collection Month':report_month,'LT 500 DQ': lt_500_dq, 'LT 500 Bal': lt_500_bal, '501-600 DQ':dq_501_600, '501-600 Balance':bal_501_600, '601-700 DQ':dq_601_700, '601-700 Balance': bal_601_700,'701+ DQ':dq_701, '701+ Balance':bal_701, 'Deal':deal}
	dq_df = pd.DataFrame(data=dq_data, index = [0])
	final_file = r'C:\Users\dcsma\Documents\Python Scripts\ALD\AMCAR DQ by FICO.csv'
	with open(final_file, 'a') as f:
		dq_df.to_csv(f, header=False)
	wipe_file(temp_xml)