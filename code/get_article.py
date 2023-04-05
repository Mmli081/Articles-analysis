import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import winsound


profs_df = pd.read_csv("../data/professors.csv")
df = pd.read_csv("../data/articles2.csv")
df.link_id = df.link_id.astype("str")
# df = pd.DataFrame()
last_p = int(df.iloc[-1]["link_id"].split(" ")[-1])
# last_p = -1

n_driver = 4
drivers = [webdriver.Firefox() for i in range(n_driver)]

error = 0
for id,row in profs_df.iterrows():

    if id<=last_p:
        continue

    drivers[0].get(f"https://scholar.google.com/citations?hl=en&user={row['user_id']}")
    soup = BeautifulSoup(drivers[0].page_source)
    while not soup.find("tbody", attrs={"id": "gsc_a_b"}):
        #Tell them I'am not a robot! :)
        winsound.Beep(440, 1000)
        sleep(2*60)
        drivers[driver_i].refresh()
        soup = BeautifulSoup(drivers[0].page_source)

    b = drivers[0].find_element(By.XPATH, "//button[@class='gs_btnPD gs_in_ib gs_btn_flat gs_btn_lrge gs_btn_lsu']")
    while b.is_enabled():
        drivers[0].execute_script("window.scrollTo(0,document.body.scrollHeight)")
        b.click()
        sleep(1.5)

    soup = BeautifulSoup(drivers[0].page_source)
    articles = soup.find("tbody", attrs={"id":"gsc_a_b"}).find_all('tr')
    print(f"id:  {id}  -> len(articles): {len(articles)}")

    for counter,article in enumerate(articles):
        driver_i = counter % 4
        print(f"{counter + 1}", end=" ")
        result = {}

        result["Title"] = " ".join([str(x) for x in article.find('a').contents])
        y = article.find("td",{"class":"gsc_a_y"}).text  #year
        c = article.find("td",{"class":"gsc_a_c"}).text  #cite

        if c == '' and (y == '' or int(y) < 2020):
            continue

        if result["Title"] in df["Title"].values:
            if str(id) not in df.iloc[np.where(df["Title"].str.contains(result["Title"], regex=False))[0][0], 3].split():
                df.iloc[np.where(df["Title"].str.contains(result["Title"], regex=False))[0][0], 3] += " " + str(id)
            continue


        drivers[driver_i].get("https://scholar.google.com" + f"{article.find('a')['href']}")
        sleep(.051)
        soup_art = BeautifulSoup(drivers[driver_i].page_source)
        while not soup_art.find("div", attrs={"class": "gs_scl"}):
            #Tell them I'am not a robot! :)
            winsound.Beep(440, 1000)
            sleep(2*60)
            drivers[driver_i].refresh()
            soup_art = BeautifulSoup(drivers[driver_i].page_source)

        try:
            header = soup_art.find('div', attrs={"id": "gsc_oci_title_wrapper"}).find_all('a')
            try:
                if len(header) > 1:
                    result["d_link"] = header[0]["href"]
                    result["art_link"] = header[1]["href"]
                else:
                    result["art_link"] = header[0]["href"]
            except:
                pass
            result["link_id"] = str(id)
            result["GS_link"] = drivers[driver_i].current_url 

            body = soup_art.find("div", attrs={"id":"gsc_oci_table"})
            body = body.find_all('div', attrs={"class": "gs_scl"})
            result["Authors"] = body[0].find_all('div')[1].get_text().split(", ")

            for div in body[1:-3]:
                try:
                    key, value = div.find_all('div')
                    key, value = key.get_text(), value.get_text()
                    if key == "Description":
                        break
                    result[key] = value
                except:
                    continue

            try:
                result["Description"] = soup_art.find('div', {"id": "gsc_oci_descr"}).get_text()
            except:
                pass
            try:
                result["Cited_by"] = soup_art.find('div', {"style": "margin-bottom:1em"}).text
            except:
                pass
            df = pd.concat([df, pd.DataFrame([result])], axis=0)
        except Exception as e:
            error += 1
            print(f"error  on  {drivers[driver_i].current_url}   {e}")

            
    df.to_csv("../data/articles2.csv", index=False)
    print()
    print(f"{id} id done!")
    sleep(1.587)