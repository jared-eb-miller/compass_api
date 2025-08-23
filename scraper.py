from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

import requests

from utils import *

# load credentials from a secure location
with open('credentials.json') as f:
    credentials = json.load(f) 

driver = webdriver.Chrome()

# cerate default WebDriverWait instance
WAIT = WebDriverWait(driver , 10, poll_frequency=0.1)
WAIT_LONG = WebDriverWait(driver , 10, poll_frequency=1)

# Automate login (update selectors as needed)
driver.get("https://liberty-insight.symplicity.com/students/index.php?tab=sessions")
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

while not driver.current_url == 'https://liberty-insight.symplicity.com/students/index.php?s=home':
    print(int(time.time()), "Current URL:", driver.current_url)
    time.sleep(1)

print("Compass Landing URL:", driver.current_url)
driver.find_element(By.CLASS_NAME, "icn-mentor").click()
driver.find_element(By.CSS_SELECTOR, '[title="My Students"]').click()
time.sleep(2)

print("Current URL:", driver.current_url); time.sleep(2)
request_cookies = driver.get_cookies()
print("Cookies:", request_cookies)

time.sleep(500)  # Wait for login to complete

driver.quit()