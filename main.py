from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

base_url = "https://www.skysports.com/premier-league-table/"

input = input("Input years to scrape, separate multiple values with commas (or type all for all years): ")
if input.lower().strip() == 'all':
    years = ['2008','2009','2010','2011','2012','2013','2014','2015','2016','2017','2018','2019']
else:
    years = input.split(',')

def make_request(url):
    try:
        with closing(get(url)) as resp:
            if is_good_response(resp):
                #print(len(resp.content)) -- Debugging
                return resp.content
            else:
                print("Status code: {0} \n Content type: {1}".format(resp.status_code, resp.headers['Content-Type']).lower())
                return None

    except RequestException as e:
        print('Error occured during request {0} : {1}'.format(url, str(e)))
        return None

def is_good_response(resp):
    content_type = resp.headers['Content-Type'].lower()
    return(resp.status_code == 200 and content_type is not None and content_type.find('html') > -1)

for i in range(0, len(years)):
    raw_html = make_request(base_url + years[i].strip())
    html = BeautifulSoup(raw_html, 'html.parser')
    dataFrame = []
    data = []
    cut_off = 0
    for td in html.find_all('td', class_="standing-table__cell"):
        if td.string is not None and td.string != "\n": #Sanity check for "\n"
            #Older tables skip over last 6 games with new line, so columns and data didn't align.
            data.append(td.string)

        cut_off = cut_off + 1

        if cut_off == 11:
            dataFrame.append(data)
            #Reset variables.
            data = []
            cut_off = 0

    names = []
    for a in html.find_all('a', class_="standing-table__cell--name-link"):
        names.append(a.string)

    for j in range(0, len(names)):
        dataFrame[j].insert(1, names[j])

    names = []

    #print(dataFrame)

    df = pd.DataFrame(np.array(dataFrame), columns=['Position', 'Name', 'Played','Won', 'Draw','Lost', 'Goals For', 'Goals Against', 'Goal Difference', 'Points'])
    #print(df) -- Debugging
    with pd.ExcelWriter('league_tables.xlsx', mode='a') as writer:
        sheetname = str(years[i])
        df.to_excel(writer, sheet_name=sheetname)
