import pandas as pd
from contextlib import contextmanager
import sys, os

#adds RSS feed links from csv source file to a list; this list serves as the transactions covered under the scope of a give script
def get_rss_links(source_file, link_list):
	read_rss = pd.read_csv(source_file)
	rss_df = pd.DataFrame(data=read_rss)
	for url in rss_df.iloc[0:,2]:
		link_list.append(url)

#creates the web url in which the ALD filing lives; the function dynamically matches on the 'EX-102' in case its location on the html table changes
def construct_url(current_url, dataframe):
	ex = 'EX-102'
	for x in range(0, len(dataframe.iloc[:][3])):
		if dataframe.iloc[x][3] == ex:
			replacing_text =  dataframe.iloc[x][2]
	start_point = current_url.rfind('/')+1
	text_to_replace = current_url[start_point:]
	new_url = current_url.replace(text_to_replace, replacing_text)
	return new_url

#simply wipes the temp xml file after its been parsed; reduces memory drag
def wipe_file(file):
	with open(file, 'w') as f:
		f.write('')

#important function to eliminate the printing after the creation of each class instance to the command terminal since tens of thousands of intances will be created per ALD
@contextmanager
def no_print():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:  
            yield
        finally:
            sys.stdout = old_stdout