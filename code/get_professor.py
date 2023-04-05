import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import winsound

driver = webdriver.Firefox()

df = pd.read_csv("../data/universities.csv")
df.replace('', pd.NA, inplace=True)
df_org = df[df.org_id.notnull()]
df_org.reset_index(drop=True, inplace=True)

#TODO if file exists
profs_df = pd.read_csv("../data/professors.csv")
last_uni = profs_df["uni"].iloc[-1]
iter_df = df_org.iterrows()
FirstLoad = True

for row in iter_df:
    idx,row = row[0],row[1]
    uni = row[1]
    if FirstLoad and uni != last_uni:
        continue
    FirstLoad = False
    if uni == last_uni:
        continue
    driver.get(f"https://scholar.google.com/citations?view_op=view_org&hl=en&org={row[3]}")
    profs = {"name":[], "uni":[], "link":[], "aff":[], "v_email_at":[], "cited_by":[], "interests":[]}
    while True:
        soup = BeautifulSoup(driver.page_source)
        while not soup.find("div", attrs={"class": "gsc_1usr"}):
            #Tell them I'am not a robot! :)
            winsound.Beep(440, 1000)
            sleep(30)
            soup = BeautifulSoup(driver.page_source)
        users = soup.find_all("div", attrs={"class": "gsc_1usr"})
        for user in users:
            name = user.find("h3", attrs={"class": "gs_ai_name"}).find("a").string
            link = user.find("a", attrs={"class": "gs_ai_pho"})["href"]
            aff = user.find("div", attrs={"class": "gs_ai_aff"}).next
            v_email_at = user.find("div", attrs={"class": "gs_ai_eml"}).next
            cited = user.find("div", attrs={"class": "gs_ai_cby"}).contents
            intrests = [a.next for a in user.find("div", attrs={"class": "gs_ai_int"}).find_all("a")]
            results = [name, uni, link, aff, v_email_at, None if cited == [] else cited[0], intrests]
            for i,key in enumerate(profs.keys()):
                profs[key].append(results[i])
        b = driver.find_element(By.XPATH, "//button[@class='gs_btnPR gs_in_ib gs_btn_half gs_btn_lsb gs_btn_srt gsc_pgn_pnx']")
        if not b.is_enabled():
            break
        b.click()
    profs_df = pd.concat([profs_df, pd.DataFrame(profs)], axis=0)
    if idx % 5 == 0:
        profs_df.to_csv("../data/professors.csv", index=False)
    print(f"{uni} is done")
profs_df.to_csv("../data/professors.csv", index=False)
