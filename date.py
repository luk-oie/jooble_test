#As far as I can see, there is no way to get publication date directly or otherwise for
#the given web-source. Though, if such piece of data is truly required, there is a way to 
#track and record it for the new listings.
#The approach would require a script that is constantly running - updating the listing page, checking
#for new publications, and recording the date-time of their discovery. It would not represent
#the exact date-time of publication, as precision would be determined by the period of a cycle.
#Data retrieved should be stored separately in pairs "ID":"date-time", where ID could be URL of the page.
#Later on, date-time could be merged into the master dataframe using URL as pairing condition.

#Below is a sketch of such a script. I HAVE NOT TESTED IT PROPERLY, so please take care if you decide to
#give it a run.

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from datetime import datetime
import pandas as pd

options = Options()
options.add_experimental_option("detach", True)
browser = webdriver.Chrome(options = options)

url = "https://realtylink.org/en/properties~for-rent?view=Thumbnail"
df = pd.DataFrame(columns = ["URL", "Date-time"])
period = 300

while True:
    browser.get(url)
    elements = browser.find_elements(By.CLASS_NAME, 'a-more-detail')
    hrefs = []
    for i in elements:
        hrefs.append(i.get_attribute("href"))
    for i in hrefs:
        if i in df["URL"][-1:-12]:
            hrefs.remove(i)
    if len(hrefs) == 0:
        time.sleep(period)
        continue
    for i in hrefs:
        ls = [i, datetime.now().strftime("%d/%m/%Y %H:%M:%S")]
        df.loc[len(df.index)] = ls
    time.sleep(period)