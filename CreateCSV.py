"""
This script will pull in all of the relevant data from BeyondTrust and SNOW
and export it into a CSV that we can import into XTAM
"""

import requests
import json
import os
import mysql.connector 
import pymysql
import csv
import configparser
from requests import cookies
import urllib3
from urllib3.exceptions import SystemTimeWarning
urllib3.disable_warnings()
import logging
import re
import sys

# Import config file
config = configparser.ConfigParser()
config.read('config')
APIKey = config['BTCore']['APIKEY']
User = config['BTCore']['USER']
ServerIP = config['BTCore']['BTServerIP']
DBhost = config['DB']['DBHost']
DBUser = config['DB']['DBUser']
DBPass = config['DB']['DBPass']

# Parent,Name,Description,Type,Host,Port,URL,User,Password,Reference,ReferenceID,Secret
#csvHeader = ["BT System Name", "System ID", "BT Domain", "BT Device Description", "SNOW CI Name", "SNOW Asset Name", "SNOW CI IP", "SL1 Region", "SNOW CID","SNOW Customer Name","Match Source","NA"]
csvHeader = ["Parent", "Name", "Description", "Type", "Host", "Port", "URL", "User", "Password", "Reference", "ReferenceID", "Secret"]
output = open('sekrets.csv', 'w')
writer = csv.writer(output)
writer.writerow(csvHeader)

conn = pymysql.connect(
    user=DBUser,
    password=DBPass,
    host=DBhost,
    port=33306,
    database="btmerge"
)

cur = conn.cursor()

# Setup Logging
logging.basicConfig(filename='csv.log', level=logging.DEBUG)

#def ConvertPlatform(BTPlatformName):
    # This will take the Platform Name from BeyondTrust and convert it to the Platform Name we need in XTAM

#def GetPassword(SysID,AcctName):
#    statement = "Select AccountPass from passwords where SysName = (%s) and AccountName = (%s)"
#    data = (SysID,AcctName)
#    cur.execute(statement, data)
#    row = cur.fetchone()
#    Password = row[0]
#    return(Password)

def GetAccounts(SysID):
    statement = "Select AccountName,AccountPass,PlatformName from passwords where SysID = (%s)"
    data = (SysID)
    cur.execute(statement, data)
    results = cur.fetchall()
    return(results)


def WriteCSV(ciName,Region,CustomerName,CustomerID,Description,IP,UserName,UserPass,Platform,Archive):
    #print(f"Customers/{Region}/{CustomerName} - {CID},{ciName},{Description},{Platform},{IP},<Port>,,{UserName},{Password},,,")
    #csvOut = [BTSystemName,SystemID,DomainName,DeviceDescription,"NULL","NULL","NULL","NULL","NULL","NULL","Unknown","Help Me2"]    
    ###
    ### Important
    ### Put the Platform variable back in, you replaced it with "Unix Host" for testing
    #name = str(tmpName) + " - " + str(userName)
    name = str(ciName) + " - " + str(UserName)
    # Some customers have a "/" in their name and it messes up the way XTAM imports records via CSV. 
    # This next line removes that "/"
    NewCustomerName = re.sub('/', '',CustomerName)
    if Archive == "False":
        csvOut = ["Customers/" +str(Region)+ "/" +str(NewCustomerName),name,Description,Platform,IP,"22","",UserName,(UserPass),"","",""]
    else:
        csvOut = ["BTArchives/" +str(NewCustomerName),name,Description,"Unix Host",IP,"22","",UserName,(UserPass),"","",""]
    writer.writerow(csvOut)

def WriteCustomers():
    statement = "Select distinct CustomerName,snowCID,sl1Region from combinedlist order by snowCID ASC LIMIT 500"
    cur.execute(statement)
    results = cur.fetchall()
    for customers in results:
        tmpCustomerName = customers[0]
        # Some customers have a "/" in their name and it messes up the way XTAM imports records via CSV. 
        # This next line removes that "/"
        CustomerName = re.sub('/', '',tmpCustomerName)
        CustomerID = customers[1]
        Region = customers[2]
        csvOut = ["Customers/" +str(Region),CustomerName,CustomerID,"Folder","","","","","","","",""]
        writer.writerow(csvOut)
    statement = "Select distinct BTCustomerName from btassets where Status = 'New'"
    cur.execute(statement)
    results2 = cur.fetchall()
    for customers2 in results2:
        tmpCustomerName = customers2[0]
        CustomerName = re.sub('/', '',tmpCustomerName)
        csvOut = ["BTArchives/",CustomerName,"Archive Customer","Folder","","","","","","","",""]
        writer.writerow(csvOut)

def CreateArchives(TestMode):
    statement = "Select * from btassets where Status = 'New'"
    cur.execute(statement)
    results = cur.fetchall()
    for devices in results:
        SysName = devices[0]
        SysID = devices[1]
        AcctID = devices[2]
        CustomerName = devices[3]
        DevDescription = devices[4]

        Accounts = GetAccounts(SysID)
        for row in Accounts:
            UserName = row[0]
            UserPass = row[1]
            Password = UserPass[1:-1]
            Platform = row[2]
            if TestMode == "True":
                Password = "abc123"
            WriteCSV(SysName,"Archives",CustomerName,"Unknown CID",DevDescription,"0.0.0.0",UserName,Password,Platform,"True")

def ConvertPlatform(PlatformName):
    if PlatformName == "Checkpoint":
        xPlatform = "Unix Host"
    elif PlatformName == "Linux":
        xPlatform = "Unix Host"
    elif str(PlatformName) == "Palo Alto Networks":
        xPlatform = "Palo Alto Networks"
    elif PlatformName == "Fortinet":
        xPlatform = "Unix Host"
    elif PlatformName == "Cisco":
        xPlatform = "Cisco"
    elif PlatformName == "Generic Platform":
        xPlatform = "Unix Host"
    elif PlatformName == "Juniper":
        xPlatform = "Juniper"
    elif PlatformName == "Big-IP (F5)":
        xPlatform = "Unix Host"
    elif PlatformName == "vSphere Web API":
        xPlatform = "WEB Portal"
    elif PlatformName == "Windows":
        xPlatform = "Active Directory User"
    elif PlatformName == "SonicOS":
        xPlatform = "Unix Host"
    elif PlatformName == "HP Comware":
        xPlatform = "Unix Host"
    elif PlatformName == "Cisco Secret":
        xPlatform = "Unix Host"
    else:
        xPlatform = "Unix Host"
    return(xPlatform)



def main(TestMode):
    try:
        statement = "SELECT * from combinedlist ORDER BY snowCID ASC LIMIT 500"
        #data = (sysName)
        #cur.execute(statement, data)
        cur.execute(statement)
        conn.commit()
        data = cur.fetchall()
    except pymysql.Error as e:
        print(f"Error connecting to combined database: {e}")

    CurrCID = "0"
    
    for device in data:
        SysName = device[0]
        SysID = device[1]
        Description = device[3]
        ciName = device[4]
        IP = device[6]
        Region = device[7]
        CID = device[8]
        CustomerName = device[9]

        Accounts = GetAccounts(SysID)
        #print(Accounts)
        for row in Accounts:
            UserName = row[0]
            UserPass = row[1]
            Password = UserPass[1:-1]
            Platform = row[2]
            if TestMode == "True":
                Password = "abc123"
            NewPlatform = ConvertPlatform(Platform)
        # XTAM Headers for Import
        # Parent,Name,Description,Type,Host,Port,URL,User,Password,Reference,ReferenceID,Secret
        # Type can be Folder or Record (Windows, SSH, AD etc)
        #(ciName,Region,CustomerName,CustomerID,Description,IP,UserName,UserPass,Platform)
            WriteCSV(ciName,Region,CustomerName,CID,Description,IP,UserName,Password,NewPlatform,"False")
        #print(f"Customers/{Region}/{CustomerName} - {CID},{ciName},{Description},{Platform},{IP},<Port>,,{UserName},{Password},,,")

#TestMode = "Unknown"
n = len(sys.argv)
if str(n) == "2":
    if sys.argv[1] == "test":
        TestMode = "True"
        print("Test Mode Enabled")
else:
        TestMode = "False"

# Create Folder Structure
#csvOut = ["Import Testing/Customers/" +str(Region),CustomerName,CustomerID,"Folder","","","","","","","",""]
csvOut = ["","Customers","","Folder","","","","","","","",""]
writer.writerow(csvOut)
csvOut = ["","BTArchives","","Folder","","","","","","","",""]
writer.writerow(csvOut)
csvOut = ["Customers","US","","Folder","","","","","","","",""]
writer.writerow(csvOut)
csvOut = ["Customers","DE","","Folder","","","","","","","",""]
writer.writerow(csvOut)
csvOut = ["Customers","SG","","Folder","","","","","","","",""]
writer.writerow(csvOut)
csvOut = ["Customers","AU","","Folder","","","","","","","",""]
writer.writerow(csvOut)
csvOut = ["Customers","JP","","Folder","","","","","","","",""]
writer.writerow(csvOut)
csvOut = ["Customers","IN","","Folder","","","","","","","",""]
writer.writerow(csvOut)
csvOut = ["Customers","PPT","","Folder","","","","","","","",""]
writer.writerow(csvOut)

WriteCustomers()
main(TestMode)
CreateArchives(TestMode)
