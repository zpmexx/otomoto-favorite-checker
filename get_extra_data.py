import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from get_chrome_driver import GetChromeDriver
import json
import re
import os
from dotenv import load_dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from datetime import datetime
import sqlite3
from pathlib import Path
import sys
try:
    file_name = Path(__file__).stem
except:
    file_name = None
# Connect database
conn = sqlite3.connect('cars.db')
cursor = conn.cursor()


#get date
now = formatDateTime = formatted_date = formatDbDateTime = None
try:
    now = datetime.now()
    formatDateTime = now.strftime("%d/%m/%Y %H:%M")
    formatDbDateTime = now.strftime("%Y/%m/%d %H:%M")
    formatted_date = now.strftime("%Y-%m-%d")
except Exception as e:
    with open ('logfile.log', 'a') as file:
        file.write(f"""{file_name} - Problem with date - {str(e)}\n""")

#load env data

try:
    load_dotenv()
    from_address = os.getenv('from_address')
    to_address = os.getenv('to_address')
    email_password = os.getenv('email_password')
except Exception as e:
    with open ('logfile.log', 'a') as file:
        file.write(f"""{formatDateTime}  {file_name} - Problem with loading .env variables - {str(e)}\n""")

#google chrome driver instalation/settings
try:
    get_driver = GetChromeDriver()
    get_driver.install()
except Exception as e:
    with open ('logfile.log', 'a') as file:
        file.write(f"""{formatDateTime} {file_name} Problem with getting a ChromeDriver - {str(e)}\n""")

options = webdriver.ChromeOptions()
options.add_argument("disable-infobars")
options.add_argument("start-maximized")
options.add_argument("disable-dev-shm-usage")
options.add_argument("no-sandbox")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_argument("disable-blink-features=AutomationControlled")

service = Service()
try:
    driver = webdriver.Chrome(options=options, service=service)
except:
    driver = webdriver.Chrome(service=service)
    

try:
    db_links = cursor.execute("SELECT link from cars where ended_date IS NOT NULL").fetchall()
except Exception as e:
    with open ('logfile.log', 'a') as file:
        file.write(f"""{formatDateTime} Problem with  loading a login page - {str(e)}\n""")
        sys.exit(0)
#selenium starts here

key_mapping = {
    'Przebieg': 'przebieg',
    'Rodzaj paliwa': 'rodzaj_paliwa',
    'Skrzynia biegów': 'skrzynia_biegow',
    'Typ nadwozia': 'typ_nadwozia',
    'Pojemność skokowa': 'pojemnosc_skokowa',
    'Moc': 'moc',
    'Rok produkcji': 'rok_produkcji',
    'Model pojazdu': 'model_pojazdu',
    'Wersja': 'wersja',
    'Generacja': 'generacja',
    'Liczba drzwi': 'liczba_drzwi',
    'Liczba miejsc': 'liczba_miejsc',
    'Kolor': 'kolor'
}

for link in db_links:
    try:
        driver.get(link[0])
    except Exception as e:
        with open ('logfile.log', 'a') as file:
            file.write(f"""{formatDateTime} {file_name} Problem with loading page - {str(e)}\n""")
            
    data_dict = {}
    # Get most imoportant data

    most_important_keys = driver.find_elements(By.CLASS_NAME, "e1ho6mkz3.ooa-rlgnr.er34gjf0")
        
    most_important_values = driver.find_elements(By.CLASS_NAME, "e1ho6mkz2.ooa-1rcllto.er34gjf0")
    
    
    for key, value in zip(most_important_keys,most_important_values):
        data_dict[key.text] = value.text

    # Basic data
    sections = driver.find_elements(By.XPATH, "//div[contains(@class, 'ooa-arbkbm')]")
    for section in sections:
        try:
            # Extract the label (key)
            key = section.find_element(By.XPATH, ".//p[1]").text.strip()
            # Extract the value
            value = section.find_element(By.XPATH, ".//p[2]").text.strip()
            # Add to dictionary
            data_dict[key] = value
        except Exception as e:
            # Handle missing data gracefully
            print(f"Error extracting section: {e}")

    try:
        set_clause = ", ".join(f"{key_mapping[key]} = ?" for key in data_dict if key in key_mapping)
        values = list(data_dict.values())
        values.append(link[0])  # Append the link value for the WHERE clause
        
        sql_query = f"UPDATE cars SET {set_clause} WHERE link = ?"

        # Execute the query
        cursor.execute(sql_query, values)
        conn.commit()
    except:
        #auction is no longer avaliable
        followed_since = cursor.execute("select followed_since from cars where link = ?", (link[0],)).fetchone()[0]
        duration = (datetime.strptime(formatted_date, "%Y-%m-%d") - datetime.strptime(followed_since, "%Y-%m-%d")).days
        cursor.execute("UPDATE cars SET ended_date = ?, duration = ? WHERE link = ?",(formatted_date, duration, link[0]))
        conn.commit()
        


driver.close()  
driver.quit()

conn.close()