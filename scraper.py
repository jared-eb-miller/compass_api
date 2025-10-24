from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import json

from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

from utils import *

# load credentials from a secure location
with open('credentials.json') as f:
    credentials = json.load(f) 

driver = webdriver.Chrome()

# cerate default WebDriverWait instance
WAIT = WebDriverWait(driver , 10, poll_frequency=0.1)
WAIT_LONG = WebDriverWait(driver , 10, poll_frequency=1)

# Automate login (update selectors as needed)
driver.get(BASE_URL + "?tab=sessions")
# Wait up to 10 seconds for the element with name "loginfmt" to appear
WAIT.until( EC.presence_of_element_located((By.NAME, "loginfmt")) )
add_email(driver, credentials)
print("Email entered")

WAIT.until( EC.presence_of_all_elements_located((By.ID, "idSIButton9")) )
WAIT.until( EC.element_to_be_clickable((By.ID, "idSIButton9")) )
driver.find_element(By.ID, "idSIButton9").click()
print("Clicked Next"); time.sleep(1)

WAIT.until( EC.presence_of_element_located((By.NAME, "passwd")) )
add_password(driver, credentials)
print("Password entered")

WAIT.until( EC.presence_of_all_elements_located((By.ID, "idSIButton9")) )
WAIT.until( EC.element_to_be_clickable((By.ID, "idSIButton9")) )
driver.find_element(By.ID, "idSIButton9").click()
print("Clicked Sign In"); time.sleep(1)

print("Waiting for URL to change... (waiting for user to complete lognin)")

while not driver.current_url == BASE_URL + '?s=home':
    print(int(time.time()), "Current URL:", driver.current_url)
    time.sleep(1)

print("Compass Landing URL:", driver.current_url)

# pass off session cookies to requests api
request_cookies = driver.get_cookies()
driver.quit()
session = requests.Session()
for cookie in request_cookies:
    session.cookies.set(cookie['name'], cookie['value'])

# navigate to 'Tutoring/Mentoring' page
response = session.get(BASE_URL + "?s=tutoring&mode=list")
print("'Tutoring/Mentoring' page Response Status Code:", response.status_code)
# navigate to 'My Students' tab
response = session.get(BASE_URL + "?tab=sessions")
print("'My Students' tab Response Status Code:", response.status_code)
# navigate to 'Approved' subtab
# response = session.get("https://liberty-insight.symplicity.com/students/index.php?subtab=list")
# print("'Approved' subtab Response Status Code:", response.status_code)
# show maximmum entries (250)
response = session.get(BASE_URL + "?_so_list_aatad2de5842cb41dd3e20ad8f9847304ae=250")
print("Maximmum Entries Response Status Code:", response.status_code)
# navigate to 'Approved' subtab
# response = session.get("https://liberty-insight.symplicity.com/students/index.php?subtab=list")

# parse the HTML content using BeautifulSoup
bs = BeautifulSoup(response.text, 'html.parser')
assert bs.find(class_='lst-rpp').find('option', selected=True).text == '250', "Error: Not showing maximum entries"

a_tags = bs.find(id="_list_form").find('ul').find_all("a")
print(f"Found {len(a_tags)} <a> tags in the #_list_form element")

# extract href attributes and ensure they are unique
hrefs: list[str] = []
for a in a_tags: hrefs.append( a.get("href") )
hrefs_df = pd.DataFrame(hrefs, columns=["href"])
hrefs_df['Tab'] = 'Approved'
assert hrefs_df['href'].is_unique, "Error: hrefs are not unique"
print("Found unique links to all appointments")

# navigate to 'Archive' subtab
response = session.get(BASE_URL + "?subtab=archived")
print("'Archive' subtab Response Status Code:", response.status_code)

# parse the HTML content using BeautifulSoup
bs = BeautifulSoup(response.text, 'html.parser')
assert bs.find(class_='lst-rpp').find('option', selected=True).text == '250', "Error: Not showing maximum entries"

form = bs.find(id="_list_form")
if form.find(class_='lst-foot') is None: 
    num_pages = 1
else: 
    num_pages = len(form.find(class_='lst-foot').find_all('option'))
a_tags = form.find('ul').find_all("a")
print(f"Found {len(a_tags)} <a> tags in the #_list_form element")

# extract href attributes and ensure they are unique
hrefs: list[str] = []
names: list[str] = []
for a in a_tags:
    hrefs.append( a.get("href").strip() )
    names.append( a.text.strip() )

# loop through remaining pages (if any)
for page_num in range(2, num_pages+1):
    response = session.get(BASE_URL + f"?_so_list_fromad2de5842cb41dd3e20ad8f9847304ae=250&_so_list_fromad2de5842cb41dd3e20ad8f9847304ae_page={page_num}&")
    print(f"'Archive' subtab Page {page_num} Response Status Code:", response.status_code)

    # parse the HTML content using BeautifulSoup
    bs = BeautifulSoup(response.text, 'html.parser')
    assert bs.find(class_='lst-rpp').find('option', selected=True).text == '250', "Error: Not showing maximum entries"

    # extract href attributes and ensure they are unique
    form = bs.find(id="_list_form")
    a_tags = form.find('ul').find_all("a")
    print(f"Found {len(a_tags)} <a> tags in the #_list_form element")
    for a in a_tags: 
        href = a.get("href").strip()
        if href not in hrefs:
            hrefs.append(href)
            names.append( a.text.strip() )
        else:
            print(f"Duplicate href found on page {page_num}: {href}")
    
hrefs_df = pd.DataFrame(data={'href': hrefs, 'Name': names})
hrefs_df['Tab'] = 'Archived'

try:
    assert hrefs_df['href'].is_unique, "Error: hrefs are not unique"
except AssertionError as e:
    hrefs_df['Duplicate'] = hrefs_df.duplicated(subset=['href'], keep=False)

print("Found unique links to all appointments")

appointment_df = hrefs_df
appointment_df[list(HEADER_MAP.values())] = np.nan

appointment_df = appointment_df.apply(retrieve_appointment_data, axis=1, session=session)

appointment_df.to_csv('appointments.csv')
appointment_df.to_parquet('appointments.pq')
