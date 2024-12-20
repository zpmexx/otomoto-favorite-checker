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



#create database
conn = sqlite3.connect('cars.db')
cursor = conn.cursor()

# SQL command to create the table
create_table_query = """
CREATE TABLE IF NOT EXISTS cars (
    link TEXT PRIMARY KEY,
    title TEXT,
    city TEXT,
    price REAL,
    followed_since DATE,
    ended_date DATE,
    duration INTEGER
);
"""

# Execute the command
cursor.execute(create_table_query)

# Commit the changes and close the connection


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


#previos car's state
try:
    with open('old_cars.json', 'r') as json_file:
        old_cars_dict = json.load(json_file)
except Exception as e:
    old_cars_dict = {}
    with open ('logfile.log', 'a') as file:
        file.write(f"""{formatDateTime} Problem with reading old_cars.json - {str(e)}\n""")

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
        counter += 1
    except NoSuchElementException:
            #print(f"No more pages after {counter}.")
            break

    except Exception as e:
        with open ('logfile.log', 'a') as file:
            file.write(f"""{formatDateTime} Problem with favorites page - {str(e)}\n""")

#get current data from favorite's website
    
    for car in list_items:
        try:
            link = car.get_attribute('href')
            title = car.get_attribute('title')
            city = car.find_element(By.CSS_SELECTOR, 'p.e8o52ta6.ooa-1po1g1j').text
            
            price = car.find_element(By.CSS_SELECTOR, 'p[data-testid="ad-price"]').text
            price = price.replace(',','.')     
            clean_price = re.sub(r'[^\d.]', '', price)
            
            item_data = {
                "title": title,
                "city": city,
                "price": clean_price,
                "followed_since": formatted_date
            }

            cars_dict[link] = item_data
            
        except Exception as e:
            with open ('logfile.log', 'a') as file:
                file.write(f"""{formatDateTime} Problem with single auction details - {str(e)}\n""")
                
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

#finished auctions
deleted_cars = {}

# Run rest of a script only if there ware any auctions (protect from website changes)
if len(list_items) > 0:
    try:
    #delete no longer observed auctions from old data
        for link in list(old_cars_dict.keys()):
            if link not in cars_dict:
                deleted_cars[link] = old_cars_dict[link]
                deleted_cars[link]['ended_date'] = formatted_date
                deleted_cars[link]['duration'] = (datetime.strptime(formatted_date, "%Y-%m-%d") - datetime.strptime(deleted_cars[link]['followed_since'], "%Y-%m-%d")).days
                
                #update db
                cursor.execute("""
                        UPDATE cars SET ended_date = ?, duration = ? WHERE link = ?""", (formatted_date, deleted_cars[link]['duration'],link))
                conn.commit()
                del old_cars_dict[link]
            
        #compare old and new data, prepare email's body

        for link, data in cars_dict.items():
            #add new links to old file + new to db
            if link not in old_cars_dict:
                old_cars_dict[link] = data
                cursor.execute("""
                    INSERT INTO cars (link, title, city, price, followed_since)
                    VALUES (?, ?, ?, ?, ?)
                    """, (link, data['title'], data['city'], data['price'], data['followed_since']))
            else:
                old_price = float(old_cars_dict[link]['price'])
                new_price = float(data['price'])
                #update to lower price and add to emails' body
                if float(old_price) > float(new_price):
                    body += f"""<h3><a href="{link}">{data['title']}</a> price change from {old_price} to {new_price} <p style="color: red;">difference: {old_price - new_price}</p></h3>"""
                    old_cars_dict[link]['price'] = data['price']
                    cursor.execute("""
                        UPDATE cars SET price = ? WHERE link = ?""", (price, link))
            conn.commit()
    except Exception as e:
        with open ('logfile.log', 'a') as file:
            file.write(f"""{formatDateTime} Problem with comparing new and old data - {str(e)}\n""")

#sort cars by price, date
cars_dict = dict(sorted(cars_dict.items(), key=lambda item: (float(item[1]['price']), datetime.strptime(item[1]['followed_since'], '%Y-%m-%d'))))
old_cars_dict = dict(sorted(old_cars_dict.items(), key=lambda item: (float(item[1]['price']), datetime.strptime(item[1]['followed_since'], '%Y-%m-%d'))))

#sort by follow date, price
# cars_dict = dict(sorted(cars_dict.items(), key=lambda item: (datetime.strptime(item[1]['followed_since'], '%Y-%m-%d'), float(item[1]['price']))))
# old_cars_dict = dict(sorted(old_cars_dict.items(), key=lambda item: (datetime.strptime(item[1]['followed_since'], '%Y-%m-%d'), float(item[1]['price']))))  

#close db
conn.close()

if not cars_dict:
    body = "No auctions observed (check log file)."
else:
    body += f"<h2>Number of followed auctions: {len(old_cars_dict)}</h2>"
    body += """
    <table border="1" cellpadding="10" cellspacing="0" style="width: 100%; border-collapse: collapse;">
        <thead>
            <tr>
                <th style="text-align: center;">Name</th>
                <th style="text-align: center;">Followed since</th>
                <th style="text-align: center;">City</th>
                <th style="text-align: center;">Price</th>
            </tr>
        </thead>
        <tbody>
    """

# Dynamically generating table rows
    for link, data in old_cars_dict.items():
        body += f"""
            <tr>
                <td style="text-align: center;"><a href="{link}">{data['title']}</a></td>
                <td style="text-align: center;">{data['followed_since']}</td>
                <td style="text-align: center;">{data['city']}</td>
                <td style="text-align: center;">{data['price']}</td>
            </tr>
        """
        
    # End of the table
    body += """
        </tbody>
    </table>
    """

# New table for deleted auctions  only if there ware any auctions (protect from website changes)
if deleted_cars and len(list_items) > 0:
    body += "<h4>Auctions that have been deleted:</h4>"
    body += """
    <table border="1" cellpadding="10" cellspacing="0" style="width: 100%; border-collapse: collapse; background-color: red;">
        <thead>
            <tr style="background-color: #ff9999;">
                <th style="text-align: center; color: white;">Name</th>
                <th style="text-align: center; color: white;">Followed since</th>
                <th style="text-align: center; color: white;">City</th>
                <th style="text-align: center; color: white;">Price</th>
            </tr>
        </thead>
        <tbody>
    """

    # Dynamically generating table rows
    for link, data in deleted_cars.items():
        body += f"""
            <tr style="background-color: #ffcccc;">
                <td style="text-align: center;"><a href="{link}" style="color: black;">{data['title']}</a></td>
                <td style="text-align: center; color: black;">{data['followed_since']}</td>
                <td style="text-align: center; color: black;">{data['city']}</td>
                <td style="text-align: center; color: black;">{data['price']}</td>
            </tr>
        """
    # End of the table
    body += """
        </tbody>
    </table>"""
if not old_cars_dict:
    old_cars_dict = cars_dict
try:
    #dump data
    if old_cars_dict:
        with open('old_cars.json', 'w') as json_file:
            json.dump(old_cars_dict, json_file, indent=4)
    if cars_dict:
        with open('new_cars.json', 'w') as json_file:
            json.dump(cars_dict, json_file, indent=4)
    if deleted_cars:
        with open('deleted_cars.json', 'a') as json_file:
            json.dump(deleted_cars, json_file, indent=4)
except Exception as e:
    with open ('logfile.log', 'a') as file:
        file.write(f"""{formatDateTime} Problem with dumping data to json - {str(e)}\n""")

try:
    #send and email
    to_address_loaded = json.loads(to_address)

    try:
        msg = MIMEMultipart()
        msg['From'] = from_address
        msg["To"] = ", ".join(to_address_loaded)
        msg['Subject'] = f"{formatDateTime} Otomoto status"
        
    except Exception as e:
        with open ('logfile.log', 'a') as file:
            file.write(f""" Problem z wysłaniem email - {str(e)}\n""")

    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP('smtp-mail.outlook.com', 587)
        server.starttls()
        server.login(from_address, email_password)
        text = msg.as_string()
        server.sendmail(from_address, to_address_loaded, text)
        server.quit()    
    except Exception as e:
        with open ('logfile.log', 'a') as file:
            file.write(f"""{formatDateTime} Problem z wysłaniem maila - {str(e)}\n""")
except Exception as e:
    with open ('logfile.log', 'a') as file:
        file.write(f"""{formatDateTime} Problem with sending an email - {str(e)}\n""")