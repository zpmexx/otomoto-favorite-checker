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
import sys
from pathlib import Path
try:
    file_name = Path(__file__).stem
except:
    file_name = None


#get date
now = formatDateTime = formatted_date = formatDbDateTime = None
try:
    now = datetime.now()
    formatDateTime = now.strftime("%d/%m/%Y %H:%M")
    formatDbDateTime = now.strftime("%Y/%m/%d %H:%M")
    formatted_date = now.strftime("%Y-%m-%d")
except Exception as e:
    with open ('logfile.log', 'a') as file:
        file.write(f"""Problem with date - {str(e)}\n""")


#create database
try:
    conn = sqlite3.connect('cars.db')
    cursor = conn.cursor()
except Exception as e:
    with open('logfile.log', 'a') as file:
        file.write(f"{formatDateTime}  {file_name} Problem with db: {e}\n")
    sys.exit(0)

# SQL command to create the table
create_table_query = """
CREATE TABLE IF NOT EXISTS cars (
    link TEXT PRIMARY KEY,
    title TEXT,
    city TEXT,
    price REAL,
    lowest_price REAL,
    followed_since DATE,
    ended_date DATE,
    duration INTEGER,
    przebieg TEXT,
    rodzaj_paliwa TEXT,
    skrzynia_biegow TEXT,
    typ_nadwozia TEXT,
    pojemnosc_skokowa TEXT,
    moc TEXT,
    rok_produkcji TEXT,
    model_pojazdu TEXT,
    wersja TEXT,
    generacja TEXT,
    liczba_drzwi INTEGER,
    liczba_miejsc INTEGER,
    kolor TEXT
);"""


# Execute the command
cursor.execute(create_table_query)

# Commit the changes and close the connection

#load env data

try:
    load_dotenv()
    login = os.getenv('login')
    password = os.getenv('password')
    from_address = os.getenv('from_address')
    to_address = os.getenv('to_address')
    email_password = os.getenv('email_password')
except Exception as e:
    with open ('logfile.log', 'a') as file:
        file.write(f"""{formatDateTime} Problem with loading .env variables - {str(e)}\n""")


#google chrome driver instalation/settings
try:
    get_driver = GetChromeDriver()
    get_driver.install()
except Exception as e:
    with open ('logfile.log', 'a') as file:
        file.write(f"""{formatDateTime} Problem with getting a ChromeDriver - {str(e)}\n""")

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


#login data from .env file
login_data = {
    'username': {login}, 
    'password': {password} 
}

#login url
login_url = 'https://login.otomoto.pl/?cc=1&client_id=1l7s2rtc114dc9uqu87n8fm27&code_challenge=-Ejq_llaGsflALBHcGDZCPIEm2j89uoiHFvQI3twiA8&code_challenge_method=S256&redirect_uri=https%3A%2F%2Fwww.otomoto.pl%2Fapi%2Fauth%2Fcallback%2Fhciam&st=eyJzbCI6IjE4OWE2ZTBkYTgxeDFjY2Q1NDVjIiwicyI6IjE5MjlmMDM5ZTA4eDI2ZjY5OWE3In0%3D'


#selenium starts here
try:
    driver.get(login_url)
except Exception as e:
    with open ('logfile.log', 'a') as file:
        file.write(f"""{formatDateTime} Problem with  loading a login page - {str(e)}\n""")

time.sleep(5)

#clear accept cookies to log in
try:
    cookie_consent_button = driver.find_element(By.ID, "onetrust-accept-btn-handler")  
    cookie_consent_button.click()

    #login form                                 /html/body/div[1]/div/div/div/div/div[1]/div[2]/div[3]/div[2]/form/div[1]/div/div/input
    login_field = driver.find_element(By.XPATH,'//*[@id="username"]')

    login_field.send_keys(login_data['username'])
                                                  #/html/body/div[1]/div/div/div/div/div[1]/div[2]/div[3]/div[2]/form/div[2]/div/div/div/input
    password_field = driver.find_element(By.XPATH,'//*[@id="password"]')

    password_field.send_keys(login_data['password'])
                                 #/html/body/div[1]/div/div/div/div/div[1]/div[2]/div[3]/div[2]/form/button[2]/span/span
    driver.find_element(By.XPATH,'//*[@id="__next"]/div/div/div/div/div[1]/div[2]/div[3]/div[2]/form/button[2]/span/span').click()

    time.sleep(10)
except Exception as e:
    with open ('logfile.log', 'a') as file:
        file.write(f"""{formatDateTime} Problem with login - {str(e)}\n""")

#go to favorites
counter = 1
cars_dict = {}
list_items = []
while True:
    try:
        observed_link = f'https://www.otomoto.pl/obserwowane?page={counter}'
        driver.get(observed_link)
        
        time.sleep(10)
        
        favorites_objects = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div/main/main/ul')
        list_items = favorites_objects.find_elements(By.TAG_NAME, 'a')
        
        car_listings = driver.find_elements(By.CSS_SELECTOR, ".ooa-6crudm")
        for car in car_listings:
            price_element = car.find_element(By.CSS_SELECTOR, 'article .e6r213i1')  # Find the price element
            price = price_element.text.strip()  # Get the price text
            price = price.replace(',','.')     
            clean_price = re.sub(r'[^\d.]', '', price)

            # Extract car name (Peugeot 508)
            title_element = car.find_element(By.CSS_SELECTOR, 'article a[href*="oferta"]')  # Find the car name
            title = title_element.text.strip()  # Get the car name text

            # Extract location (Osobowe · Kraków)
            city_element = car.find_element(By.CSS_SELECTOR, 'article .e1m1sv334')  # Find the location element
            city = city_element.text.strip()  # Get the location text
            
            link = title_element.get_attribute('href')  # Get the href attribute from the <a> tag

            item_data = {
                "title": title,
                "city": city,
                "price": clean_price,
                "lowest_price": clean_price,
                "followed_since": formatted_date
            }
            
            print(item_data)
            cars_dict[link] = item_data
        
        
        
        counter += 1
    except NoSuchElementException:
            #print(f"No more pages after {counter}.")
            break

    except Exception as e:
        with open ('logfile.log', 'a') as file:
            file.write(f"""{formatDateTime} Problem with favorites page - {str(e)}\n""")

# #get current data from favorite's website
#     for car in list_items:
#         try:
#             link = car.get_attribute('href')
#             print(f"link: {link}")
#             title = car.find_element(By.CSS_SELECTOR, 'p a[href*="oferta"]')
#             print(f"title: {title}")
#             city = car.find_element(By.CLASS_NAME, 'e1m1sv334').text
#             print(f"city: {city}")
            
#             price = car.find_element(By.CSS_SELECTOR, 'p[data-testid="ad-price"]').text
#             print(f"price: {price}")
#             price = price.replace(',','.')     
#             clean_price = re.sub(r'[^\d.]', '', price)
            
     
            
#         except Exception as e:
#             #print(f"problem {e}")
#             with open ('logfile.log', 'a') as file:
#                 file.write(f"""{formatDateTime} Problem with single auction details - {str(e)}\n""")
                
#close selenium's connection
driver.close()  
driver.quit()


body = ''
try:
    with open('cars.log', 'a') as file:
        file.write(f"{formatDateTime} Cars: {json.dumps(cars_dict, indent=4)}\n")
except Exception as e:
    with open('logfile.log', 'a') as file:
        file.write(f"Problem with exporting to cars.log: {e}\n")

# Get links from DB
try:
    db_links_get = conn.execute("SELECT link from cars").fetchall()
    # Links with no ended date - you may want to delete them from DB (unfollowed from otomoto)
    db_active_links_get = conn.execute("SELECT link from cars where ended_date IS NULL").fetchall()
except Exception as e:
    with open('logfile.log', 'a') as file:
        file.write(f"{formatDateTime}  {file_name} Problem with getting links from db: {e}\n")

try:
    # Set correct type of links from db
    db_links = set(link[0] for link in db_links_get)
    db_active_links = set(link[0] for link in db_active_links_get)
    
    missing_favorites = [link for link in db_active_links if link not in cars_dict.keys()]
    with open ('missed_in_favorites.txt','w') as file:
        for link in missing_favorites:
            file.write(f'{link}\n')
    # Find links in cars_dict that are not in db_links
    missing_in_db = {link: cars_dict[link] for link in cars_dict if link not in db_links}
except Exception as e:
    with open('logfile.log', 'a') as file:
        file.write(f"{formatDateTime}  {file_name} Problem with comparing links from favorites and db: {e}\n")

try:
    for link,data in missing_in_db.items():
        #add new links to old file + new to db
        print(f"dodaje {link}")
        cursor.execute("""
            INSERT INTO cars (link, title, city, price, lowest_price, followed_since)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (link, data['title'], data['city'], data['price'], data['lowest_price'], data['followed_since']))
        conn.commit()
        print("dodalem link")
except Exception as e:
    with open('logfile.log', 'a') as file:
        file.write(f"{formatDateTime}  {file_name} Problem with inserting data to db: {e}\n")

conn.close()