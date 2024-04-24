from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import pandas as pd

#Block of code with function definition. Function-specific comments where needed,
#most functions only differ by used XPATH and error prompt.

#Simple way to drop duplicates and get unique entries
def drop_dupes(ls):
    return list(dict.fromkeys(ls))

#This is used to generate a library of urls to parse for data. Getting a list of publications to parse
#beforehand is a better option in terms of computation time and code structure, though may be not
#optimal for large datasets or continuous parsing. Takes itr (number of items to retrieve) as argument,
#retrieves urls from listing and swithces to next page until itr requirement is satisfied.
def get_urls(itr):
    urls = []
    try:
        while len(urls) < itr:
            elements = browser.find_elements(By.CLASS_NAME, 'a-more-detail')
            hrefs = []
            for i in elements:
                hrefs.append(i.get_attribute("href"))
            uniques = drop_dupes(hrefs)
            urls.extend(uniques)
            next_page = browser.find_element(By.XPATH, '/html/body/main/div[8]/div/div[1]/ul/li[4]/a')
            next_page.click()
            time.sleep(2)
    except:
        print("something went wrong at get_urls")
    urls = urls[:itr]
    return urls

#Finds requested element by CSS_SELECTOR, retrieves text and appends it to master list.
def get_title(ls):
    try:
        title = browser.find_element(By.CSS_SELECTOR, '[data-id="PageTitle"]').text
        ls.append(title)
    except:
        print("something went wrong at get_title()")
        ls.append("null")

#Finds full address, subsets a region entry from it and appends both to the master list.
#Has a counter and if-statement to ensure integrity of master list structure in case of error.
def get_region_address(ls):
    try:
        address = browser.find_element(By.CLASS_NAME, "pt-1").text
        words = address.split(", ")
        region = words[-2] + ", " + words[-1]
        c = 0
        ls.append(region)
        c+=1
        ls.append(address)
        c+=1
    except:
        print("something went wrong at get_address()")
        if c == 0:
            ls.append("none")
            ls.append("none")
        elif c == 1:
            ls.append("none")
        else:
            ls.append("something went terribly wrong")

#Many publications don't have description. This does not affect function, but it is good to be aware of this.
def get_description(ls):
    try:
        description = browser.find_element(By.CSS_SELECTOR, '[itemprop="description"]').text
        ls.append(description)
    except:
        print("something went wrong at get_description()")
        ls.append("null")

def get_price(ls):
    try:
        price = browser.find_element(By.XPATH, '//*[@id="overview"]/div[1]/div[1]/div/div[2]/div[1]/span[4]').text
        ls.append(price)
    except:
        print("something went wrong at get_price()")
        ls.append("null")

def get_area(ls):
    try:
        area = browser.find_element(By.XPATH, '//*[@id="overview"]/div[3]/div[1]/div[6]/div[1]/div[2]/span').text
        ls.append(area)
    except:
        print("something went wrong at get_area()")
        ls.append("null")

#Listed studios often have no bedroom descriptor, I took liberty to classify them as 1 bedroom appartments.        
def get_bedrooms(ls):
    try:
        bedrooms = browser.find_element(By.XPATH, '//*[@id="overview"]/div[3]/div[1]/div[4]/div[2]').text
        if len(bedrooms) != 0:
            ls.append(bedrooms)
        else:
            ls.append("1 bedroom")
    except:
        print("something went wrong at get_bedrooms()")
        ls.append("null")

#Opens page with all photos of publication, goes through them and retrieves image links.
def get_img_links(ls):
    try:
        img_button = browser.find_element(By.XPATH, '//*[@id="overview"]/div[2]/div[1]/div/div[3]/button')
        img_button.click()
        time.sleep(2)
        img_nb = browser.find_element(By.XPATH, '//*[@id="gallery"]/div[2]/div[2]/strong').text
        img_nb = int(img_nb.split("/")[-1])
        img_links = []
        for i in range(img_nb):
            img_el = browser.find_element(By.XPATH, '//*[@id="fullImg"]')
            img_link = img_el.get_attribute('src')
            img_links.append(img_link)
            next_button = browser.find_element(By.XPATH, '//*[@id="gallery"]/div[2]/div[1]')
            next_button.click()
            time.sleep(1)
        ls.append(img_links)
    except:
        print("something went wrong at get_img_links()")
        ls.append("null")    

#This is just a filler fucntion as I found no way of getting publication date. There is no such data
#on this site (headers, metadata, timestamps, external page dating tools - none return anything of relevance).
#I found a way to date new entries, but this is way too complex to implement in context of this task.
#Please check the idea in "date.py"
def get_date(ls):
    try:
        pub_date = "no date"
        ls.append(pub_date)
    except:
        print("something went wrong at get_date()")
        ls.append("null")    


#Setting up the browser
options = Options()
options.add_experimental_option("detach", True)
browser = webdriver.Chrome(options = options)

#Creating a dataframe of required structure and setting number of pages to be parsed (itr)
df = pd.DataFrame(columns = ["link", "title", "region", "address", "description", "img_links", "date", "price", "nb_rooms", "area"])
itr = 60

#Initiating scraping
url = "https://realtylink.org/en/properties~for-rent?view=Thumbnail"
browser.get(url)
time.sleep(2)

#Getting list of urls to be parsed
urls = get_urls(itr)

#Going through the list and retrieving necessary data through functions declared above.
#Execution order is key for proper filling of the dataframe.
#Dataframe is updated with a new row through each iteration.
#Resets url once, after image links retrieval. Could be implemented with opening and closing
#another tab, but that would require redeclaring main tab, which doesn't seem worth the trouble
#for this task.
#Takes ~30 seconds for an iteration
for i in urls:
    ls = []
    browser.get(i)
    time.sleep(2)
    ls.append(i)
    get_title(ls)
    get_region_address(ls)
    get_description(ls)
    get_img_links(ls)
    browser.get(i)
    time.sleep(2)
    get_date(ls)
    get_price(ls)
    get_bedrooms(ls)
    get_area(ls)
    df.loc[len(df.index)] = ls

#Saving the result in desired format and checking briefly for data integrity.
df.to_json('realty_link.json', orient = 'records')
print(df.head())
print(df.isnull())




