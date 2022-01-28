from operator import contains
from selenium import webdriver
from getpass import getpass
from time import sleep
#from bs4 import BeautifulSoup
#import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
#from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys

# Prompt user for credentials
user = input('Enter Email ID:')
pwd = getpass('Enter Password:')

driver = webdriver.Firefox()
driver.get("https://defense-prod05.conferdeploy.net/settings/connectors")
print("Opening Browser")
sleep(1)

# Enter Email Address
username_box = driver.find_element(By.ID, 'email')
username_box.send_keys(user)

sleep(1)

# Enter Password
password_box = driver.find_element(By.ID, 'password')
password_box.send_keys(pwd)

sleep(1)

# Click Submit
login_box = driver.find_element(By.ID, 'submit-log-in')
login_box.click()
print("Logging In")

sleep(1)

print("Gathering Credentials")

# Parse out the OrgID and OrgKey
OrgID = driver.find_element(By.XPATH, "/html/body/div/div/div/div[2]/div[2]/div/div[2]/div[1]/dl/dd[2]")
OrgKey = driver.find_element(By.XPATH, "/html/body/div/div/div/div[2]/div[2]/div/div[2]/div[1]/dl/dd[1]")
print(f" - Org ID is {OrgID.text}")
print(f" - Org Key is {OrgKey.text}")

print("Adding API Key - SIEM")
add_api = driver.find_element(By.XPATH, '/html/body/div/div/div/div[2]/div[2]/div/div[2]/div[1]/div/div/button[2]')
add_api.click()
api_name_box = driver.find_element(By.XPATH, '/html/body/div[2]/div[3]/div/div[2]/div/div[1]/div/input')
# Fill in API Name
API_Name = "Test API from Selenium"
api_name_box.send_keys(API_Name)
# Select API Type
driver.find_element(By.XPATH,'/html/body/div[2]/div[3]/div/div[2]/div/div[3]/div/div').click()
driver.find_element(By.XPATH,'/html/body/div[3]/div[3]/ul/li[1]/span[1]').click()
driver.find_element(By.XPATH,'/html/body/div[2]/div[3]/div/div[3]/button[1]').click()
sleep(2)
API_ID = driver.find_element(By.XPATH,'/html/body/div[2]/div[3]/div/div[2]/div[1]/div[1]')
API_Key = driver.find_element(By.XPATH,'/html/body/div[2]/div[3]/div/div[2]/div[2]/div[1]')
print(f" - API ID is: {API_ID.text}")
print(f" - API Key is: {API_Key.text}")
sleep(1)
# Close API Credentials Box
driver.find_element(By.XPATH,'/html/body/div[2]/div[3]/div/div[1]/button').click()
print("Creating Custom Role for second API")
# Create Custom Role
# Click on "Access Levels" tab
driver.find_element(By.XPATH,'/html/body/div/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div/div/button[2]').click()
driver.find_element(By.XPATH,'/html/body/div/div/div/div[2]/div[2]/div/div[2]/button').click()
roleName_box = driver.find_element(By.XPATH,'//*[@id="orgRoleName"]')
roleName_box.send_keys("MSSP Custom Access")
roleDescription_box = driver.find_element(By.XPATH,'//*[@id="orgRoleDescription"]')
roleDescription_box.send_keys("Allows pulling of security data")

# Alerts - Read Only
driver.find_element(By.XPATH,'/html/body/div[2]/div[3]/div/div[2]/div[2]/div/div/div[2]/div/div[2]/div[2]/div[1]/div[6]/span/span[1]/input').click()
# Custom Detections - Read Only
driver.find_element(By.XPATH,'/html/body/div[2]/div[3]/div/div[2]/div[2]/div/div/div[2]/div/div[2]/div[11]/div[1]/div[6]/span/span[1]/input').click()
# Device - Read Only
driver.find_element(By.XPATH,'/html/body/div[2]/div[3]/div/div[2]/div[2]/div/div/div[2]/div/div[2]/div[19]/div[1]/div[6]/span/span[1]/input').click()
# Search - Read Only
driver.find_element(By.XPATH,'/html/body/div[2]/div[3]/div/div[2]/div[2]/div/div/div[2]/div/div[2]/div[32]/div[1]/div[6]/span/span[1]/input').click()
# Click 'Save'
print("Saving custom role")
driver.find_element(By.XPATH,'/html/body/div[2]/div[3]/div/div[3]/button[1]').click()
sleep(3)

# Go back to the 'API Keys' tab
#driver.find_element(By.XPATH,'/html/body/div/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div/div/button[1]').click
driver.refresh()
sleep(3)
# Create second API key based on custom role
print("Adding API Key - Custom Role")
add_api = driver.find_element(By.XPATH, '/html/body/div/div/div/div[2]/div[2]/div/div[2]/div[1]/div/div/button[2]')
add_api.click()
api_name_box = driver.find_element(By.XPATH, '/html/body/div[2]/div[3]/div/div[2]/div/div[1]/div/input')
# Fill in API Name
api_name_box.send_keys("MSSP Access API")
# Select API Type
driver.find_element(By.XPATH,'/html/body/div[2]/div[3]/div/div[2]/div/div[3]/div/div').click()
driver.find_element(By.XPATH,'/html/body/div[3]/div[3]/ul/li[4]').click()
element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'/html/body/div[2]/div[3]/div/div[2]/div/div[3]/div[2]/div')))
element.click()
#if driver.find_element(By.XPATH,"/html/body/div[3]/div[3]/ul/li[contains(text(), 'MSSP')]"):
try:
    driver.find_element(By.XPATH,"//*[contains(text(), 'MSSP')]").click()
except:
    print("Unable to find MSSP in dropdown")
    input('Press any key to rollback')
    rollback()
    driver.quit()
    sys.exit()
# Save Custom API
driver.find_element(By.XPATH,'/html/body/div[2]/div[3]/div/div[3]/button[1]').click()
sleep(2)
API2_ID = driver.find_element(By.XPATH,'/html/body/div[2]/div[3]/div/div[2]/div[1]/div[1]')
API2_Key = driver.find_element(By.XPATH,'/html/body/div[2]/div[3]/div/div[2]/div[2]/div[1]')
print(f" - API ID is: {API2_ID.text}")
print(f" - API Key is: {API2_Key.text}")
sleep(1)
# Close API Credentials Box
driver.find_element(By.XPATH,'/html/body/div[2]/div[3]/div/div[1]/button').click()

#input('Press anything to quit: ')
print("Closing Browser")
#sleep(5)
driver.quit()
