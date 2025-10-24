import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

from bs4 import BeautifulSoup

HEADER_MAP = {
    'Liberty ID Number': 'LUID',
    "Student's Preferred Name": 'Preferred Name',
    'Tutor/Mentor': 'Tutor/Mentor',
    'Appointment Type': 'Course',
    'Date': 'Date',
    'Time': 'Time',
    'Length (in minutes)': 'Length (min)',
    'Location': 'Location',
    'Purpose of Appointment': 'Purpose',
    'Student Notes': 'Notes',
    'Appointment Approved?': 'Approved?',
    'Appointment Rejected by Administrator?': 'Rejected by Admin?',
    'Admin Notes': 'Admin Notes',
    'Reason for Cancellation': 'Reason for Cancellation',
    'Reason for Cancellation (Comments)': 'Reason for Cancellation (Comments)',
    'Appointment Attendance': 'Attendance'
}
BASE_URL = "https://liberty-insight.symplicity.com/students/index.php"


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

def retrieve_appointment_data(row, session):
    href = row.at['href']
    _hash = href.split('=')[-1]
    print(f"Retrieving data for appointment {_hash}...")
    print(BASE_URL + href)
    response = session.get(BASE_URL + href)
    print(f"Appointment {_hash} Response Status Code:", response.status_code)
    bs = BeautifulSoup(response.content, 'html.parser')
    field_group = bs.find(id='_fieldgroup__default_section')
    items = list(field_group.children)[1:-1:2]
    for field in items:
        label = field.find(class_='field-label').text.strip()
        assert label in HEADER_MAP.keys(), f"Unexpected label '{label}' found"
        value = field.find(class_='field-widget').text.strip()
        row.at[HEADER_MAP[label]] = value

    return row