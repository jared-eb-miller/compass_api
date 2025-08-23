import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

def add_email(driver, credentials):
    trys = 1
    while trys < 20:
        try:
            driver.find_element(By.NAME, "loginfmt").send_keys(credentials["email"])
        except selenium.common.exceptions.ElementNotInteractableException:
            print("Email input not interactable, waiting and retrying...")
            time.sleep(1)
            print("Retrying to find email input...")
            continue
        break

def add_password(driver, credentials):
    trys = 1
    while trys < 20:
        try:
            driver.find_element(By.NAME, "passwd").send_keys(credentials["password"])
        except selenium.common.exceptions.ElementNotInteractableException:
            print("Password input not interactable, waiting and retrying...")
            time.sleep(1)
            print("Retrying to find password input...")
            continue
        break
 