"""
    This module gets the name of the university URL and creates university.csv in the data repo.

    data includes university rank, university name, university town, and university org_id in google scholar.
    university org_id: this id is crawled on google scholar when you search for it. you can access to
        university profile in google scholar with this org_id.
    
    def get_uni_names(url) -> df
    def clean_name(name) -> str
    def get_org_id(url) -> crawl google scholar and get org_id for each university.
    at last, university.csv create in the data repository with rank, name, town, org_id.
"""
from bs4 import BeautifulSoup
from selenium import webdriver
import re, pandas as pd
from time import sleep
import numpy as np
import winsound

path_to_save = "googleScholar/data/universities.csv"
top_uni_Iran_url = "https://www.4icu.org/ir/"

def get_uni_names(url:str):
    df = pd.read_html(url)[0]
    df.columns = df.columns.droplevel()
    df.Town = df.Town.str.replace(" ...", "", regex=False)
    df["org_id"] = pd.Series([None for i in range(len(df))])
    df.to_csv(path_to_save, index=False)
    return df



def clean_name(name):
    l_name = name.lower().split()
    if l_name[0] == "the":
        name = " ".join(name.split()[1:])
    return name


def get_org_id(url):
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html)
    while not soup.find("div", attrs={"class": "gsc_1usr"}):
        #Tell them I'am not a robot! :)
        winsound.Beep(440, 1000)
        sleep(30)
        soup = BeautifulSoup(html)
    rec_div = soup.find("div", attrs={"class":"gsc_instbox_sec"})
    link = rec_div.find("a") if rec_div else None
    org = re.findall(r"org=(\d+)",link["href"]) if link else []
    org_id = org[0] if len(org) > 0 else None
    print(f"{uni}   {org_id}")
    df.iloc[np.where(df["University"] == uni)[0], 3] = org_id





df = pd.read_csv(path_to_save)
df.replace('', pd.NA, inplace=True)

driver = webdriver.Firefox()

to_iter = df[df["org_id"].isna()]["University"]
c=0

for uni in to_iter:
    c+=1
    uni = clean_name(uni)
    params = {
        'q': uni,
        "hl": "en",
    }
    get_org_id(f"https://scholar.google.com/citations?view_op=search_authors&hl=en&mauthors={params['q'].replace(' ','+')}")
    if c%50==0:
        df.to_csv(path_to_save, index=False)

df.to_csv(path_to_save, index=False)