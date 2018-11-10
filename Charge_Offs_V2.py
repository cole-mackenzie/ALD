import xml.etree.ElementTree as et
import requests
import pandas as pd
import time
import my_functions
from my_functions import get_rss_links, construct_url, wipe_file, no_print

#these lists will ultimately serve as the lists to which we append 1) all of the assets in a given xml for the asset_list, and 2) just the charged off assets in the co_list
asset_list = []
co_list = []
x = 0

#establish the charged off loan class. These are the attributes of each charged off loan that we want to eventually put in a dataframe
class charged_off_asset:
			
	def __init__(self, balance, fico, zero_code, month, orig_date, apr, o_term, pti, n_u, ltv, recover_amt, liqui_amt):
		self.balance = balance
		self.fico = fico
		self.zero_code = zero_code
		self.month = month
		self.orig_date = orig_date
		self.apr = apr
		self.o_term = o_term
		self.pti = pti
		self.n_u = n_u
		self.ltv = ltv
		self.recover_amt = recover_amt
		self.liqui_amt = liqui_amt
		asset_list.append(self)

#csv file where all the rss feeds are kept; probably a more sophisticated way to retrieve these but for now it works
rss_file = r'C:\Users\dcsma\Documents\Python XML Testing\RSS.csv'
rss_urls = []
get_rss_links(rss_file,rss_urls)

#temp text files that we will be writing the get statements to; the goal is to spend as little time doing anything on the webpages for both performance and ethical reasons
temp_rss = r'C:\Users\dcsma\Documents\Python XML Testing\XMLs\temp_RSS.xml'
temp_xml = r'C:\Users\dcsma\Documents\Python XML Testing\XMLs\temp_xml.xml'

#start of primary for loop. Phase 1 is to loop through the urls of the rss feeds from the rss file
for url in rss_urls:
	#x = x + 1 #these are just prints to the command terminal to serve as quasi progress reports
	#print(x)
	rss_get = requests.get(url)
	rss_content = rss_get.content
	rss_get.close()
	time.sleep(10) #sleep call to reduce bandwith drain
	with open(temp_rss, 'wb') as file:
		file.write(rss_content) #writing the RSS Feed xml to a text file
	rss_tree = et.parse(temp_rss) #officially have moved to local disk files
	rss_root = rss_tree.getroot()
	abs_ee_links = []
	#this for loop retrieves all of the URLs for the ABS-EE filings for a given transaction
	for child in rss_root.findall('{http://www.w3.org/2005/Atom}entry'):
		for element in child:
			for attribute in element:
				if attribute.tag  == '{http://www.w3.org/2005/Atom}filing-href': #all of the links are stored in the 'filing-href' attribute
					abs_ee_links.append(attribute.text) #list of all links
	for x in range(0,1):
		filing_page = abs_ee_links[x] #this particular script is just pulling the most recent filing; but it can be changed to loop through all links, or as many as desired
		page = requests.get(filing_page)
		time.sleep(10)
		tables = pd.read_html(page.text) #reads the html of the filing page; there is only one table in every filing page
		time.sleep(5)
		filing = tables[0]
		df = pd.DataFrame(data=filing)
		data = requests.get(construct_url(filing_page,df)) #construct_url is a function from the my_funcs module
		time.sleep(10)
		tape = data.content
		data.close()
		with open(temp_xml, 'wb') as file:
			file.write(tape)
		data_tape = et.parse(temp_xml)
		root = data_tape.getroot()
		#this for loop iterates through every child in the given ALD file, declaring the desired variables and assigning them a corresponding value
		for child in root.findall('{http://www.sec.gov/edgar/document/absee/autoloan/assetdata}assets'):
			try:
				zero_code = float(child.find('{http://www.sec.gov/edgar/document/absee/autoloan/assetdata}zeroBalanceCode').text)
			except:
				zero_code = 0
			try:
				balance = float(child.find('{http://www.sec.gov/edgar/document/absee/autoloan/assetdata}chargedoffPrincipalAmount').text)
			except:
				balance = 0
			try:
				fico = float(child.find('{http://www.sec.gov/edgar/document/absee/autoloan/assetdata}obligorCreditScore').text)
			except:
				fico = 0
			month = child.find('{http://www.sec.gov/edgar/document/absee/autoloan/assetdata}reportingPeriodEndingDate').text
			orig_date = child.find('{http://www.sec.gov/edgar/document/absee/autoloan/assetdata}originationDate').text
			apr = float(child.find('{http://www.sec.gov/edgar/document/absee/autoloan/assetdata}originalInterestRatePercentage').text)
			o_term = float(child.find('{http://www.sec.gov/edgar/document/absee/autoloan/assetdata}originalLoanTerm').text) - float(child.find('{http://www.sec.gov/edgar/document/absee/autoloan/assetdata}gracePeriodNumber').text)
			try:
				pti = float(child.find('{http://www.sec.gov/edgar/document/absee/autoloan/assetdata}paymentToIncomePercentage').text)
			except:
				pti = 'N/A'
			n_u = float(child.find('{http://www.sec.gov/edgar/document/absee/autoloan/assetdata}vehicleNewUsedCode').text)
			try:
				ltv = float(child.find('{http://www.sec.gov/edgar/document/absee/autoloan/assetdata}originalLoanAmount').text)/float(child.find('{http://www.sec.gov/edgar/document/absee/autoloan/assetdata}vehicleValueAmount').text)
			except:
				ltv = 'N/A'
			try:
				recover_amt = float(child.find('{http://www.sec.gov/edgar/document/absee/autoloan/assetdata}recoveredAmount').text)
			except:
				recover_amt = 0
			try:
				liqui_amt = float(child.find('{http://www.sec.gov/edgar/document/absee/autoloan/assetdata}repossessedProceedsAmount').text)
			except:
				liqui_amt = 0
			#here we call the class so that we can instantiate every discrete asset as an instance of the charged_off_asset type. However, despite the name every asset gets instantiated, not just charged off assets
			with no_print():
				charged_off_asset(balance, fico, zero_code, month, orig_date, apr, o_term, pti, n_u, ltv, recover_amt, liqui_amt)
		#shell lists which will serve as the columns in our final data frame
		bal_list = []
		fico_list = []
		code_list = []
		month_list = []
		orig_date_list = []
		apr_list = []
		o_term_list = []
		pti_list = []
		n_u_list = []
		ltv_list = []
		recover_list = []
		liqui_list = []

		#shave all of the assets to just the charged off assets
		for x in asset_list:
			if x.zero_code == 4:
				co_list.append(x)

		#iterate through the charged off assets to add the corresponding attributes to the shell lists
		for x in co_list:
			bal_list.append(x.balance)
			fico_list.append(x.fico)
			code_list.append(x.zero_code)
			month_list.append(x.month)
			orig_date_list.append(x.orig_date)
			apr_list.append(x.apr)
			o_term_list.append(x.o_term)
			pti_list.append(x.pti)
			n_u_list.append(x.n_u)
			ltv_list.append(x.ltv)
			recover_list.append(x.recover_amt)
			liqui_list.append(x.liqui_amt)

		#take the lists and turn them into a dataframe, and then save that to the final csv file
		co_data = {'Month':month_list,'Charged Off Amount':bal_list,'Credit Score':fico_list,'Reason Code':code_list,'Origination Date':orig_date_list,'APR':apr_list, 'Original Term':o_term_list,'PTI Ratio':pti_list,'New/Used':n_u_list,'LTV Ratio':ltv_list,'Recovered Amount':recover_list,'Repo Proceeds':liqui_list}
		charged_off_df = pd.DataFrame(data=co_data)
		print(charged_off_df.shape)
		charge_off_file = r'C:\Users\dcsma\Documents\Python Scripts\Charge Off List.csv'
		with open(charge_off_file, 'a') as f:
			charged_off_df.to_csv(f, header=False)