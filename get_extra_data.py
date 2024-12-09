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
from tables import observed_table, deleted_table, promo_table
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
    db_links = cursor.execute("SELECT link from cars where ended_date IS NULL").fetchall()
except Exception as e:
    with open ('logfile.log', 'a') as file:
        file.write(f"""{formatDateTime} {file_name} Problem with getting data from db - {str(e)}\n""")
        sys.exit(0)
#selenium starts here

# Map otomoto data keys with database columns
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

# Iterate over links(auctions) in db
promo_dict = {}
try:
    updated_count = deleted_count = 0
    for link in db_links:
        try:
            driver.get(link[0])
        except Exception as e:
            with open ('logfile.log', 'a') as file:
                file.write(f"""{formatDateTime} {file_name} Problem with loading page - {str(e)}\n""")
                
        data_dict = {}
        
        # Get most importat data "Najważniejsze"
        try:
            details = driver.find_elements(By.XPATH, '//div[@data-testid="detail"]')
            for detail in details:
                try:
                    key = detail.find_element(By.XPATH, './/p[contains(@class, "ooa-rlgnr")]').text
                    value = detail.find_element(By.XPATH, './/p[contains(@class, "ooa-1rcllto")]').text
                    data_dict[key] = value
                except Exception as e:
                    with open ('logfile.log', 'a') as file:
                        file.write(f"""{formatDateTime} {file_name} Problem with loading specifc data from most important - {str(e)}\n""")
        except Exception as e:
            with open ('logfile.log', 'a') as file:
                file.write(f"""{formatDateTime} {file_name} Problem with loading most important data - {str(e)}\n""")
                
        price = None 
        try:
            # price from website
            price = driver.find_element(By.CLASS_NAME, "offer-price__number").text.replace(" ", "")
        except Exception as e:
            with open ('logfile.log', 'a') as file:
                file.write(f"""{formatDateTime} {file_name} Problem with loading price - {str(e)}\n""")
                
        

        # Get details data "Szczegóły"
        try:
            basic_info = driver.find_element(By.XPATH, '//div[@data-testid="basic_information"]')
            details = basic_info.find_elements(By.XPATH, './/div[contains(@data-testid, "")]')
            for detail in details:
                try:
                    key = detail.find_element(By.CLASS_NAME, "eim4snj7").text
                    value = detail.find_element(By.CLASS_NAME, "eim4snj8").text
                    data_dict[key] = value
                except Exception as e:
                    with open ('logfile.log', 'a') as file:
                        file.write(f"""{formatDateTime} {file_name} Problem with loading specifc data from details- {str(e)}\n""")
        except Exception as e:
            with open ('logfile.log', 'a') as file:
                file.write(f"""{formatDateTime} {file_name} Problem with loading details data- {str(e)}\n""")

        try:
            set_clause = ", ".join(f"{key_mapping[key]} = ?" for key in data_dict if key in key_mapping)
            set_clause += ", ended_date = NULL, duration = NULL" # Sometimes auctions are not shown (e.g. not payed) and then come back with the same link 
            values = [data_dict[key] for key in data_dict if key in key_mapping]
            values.append(link[0])  # Append the link value for the WHERE clause
            sql_query = f"UPDATE cars SET {set_clause} WHERE link = ?"
            cursor.execute(sql_query, values)
            conn.commit()
            updated_count += 1
            
            # Set promo price
            try:
                sql_query = f"select price, title, city from cars WHERE link = ?"
                db_data = cursor.execute(sql_query, (link[0],))
                # Db price
                db_data = db_data.fetchone()
                db_price, db_title, db_city = db_data
                db_price = db_data[0]
                if float(price) < float(db_price):
                    promo_dict[link[0]] = {
                        'old_price': db_price,
                        'new_price': price,
                        'difference': float(db_price) - float(price),
                        'title': db_title,
                        'city': db_city
                    }
                    cursor.execute("""UPDATE  cars set lowest_price = ? where link = ?""", (price, link[0]))
                    cursor.commit()
            except Exception as e:
                with open ('logfile.log', 'a') as file:
                    file.write(f"""{formatDateTime} {file_name} Problem with setting update price - {str(e)}\n""")
            
        except:
            #auction is no longer avaliable
            result = cursor.execute("SELECT followed_since, ended_date, duration FROM cars WHERE link = ?",(link[0],)).fetchone()
            followed_since, ended_date, duration = result
            duration = (datetime.strptime(formatted_date, "%Y-%m-%d") - datetime.strptime(followed_since, "%Y-%m-%d")).days
            cursor.execute("UPDATE cars SET old_ended_date = ended_date, old_duration = duration, ended_date = ?, duration = ? WHERE link = ?", (formatted_date, duration, link[0]))

            conn.commit()
            deleted_count += 1
except Exception as e:
    with open ('logfile.log', 'a') as file:
        file.write(f"""{formatDateTime} {file_name} Problem with db links - {str(e)}\n""")        

driver.close()  
driver.quit()

# Send mail section
try:
    conn.row_factory = sqlite3.Row  # Enable dictionary-like access for rows
    cursor = conn.cursor()
    observed_data = cursor.execute("""SELECT link, title, followed_since, city, price, przebieg, rodzaj_paliwa,
                                        skrzynia_biegow, typ_nadwozia, pojemnosc_skokowa,moc,rok_produkcji,model_pojazdu
                                        from cars where ended_date is NULL order by price""").fetchall()

    deleted_data = cursor.execute("""SELECT link, title, city, followed_since, ended_date, duration, price, lowest_price,
                                        przebieg, rodzaj_paliwa, skrzynia_biegow, typ_nadwozia, pojemnosc_skokowa,
                                        moc, rok_produkcji, model_pojazdu from cars where ended_date IS NOT NULL order by duration desc""").fetchall()

except Exception as e:
    with open ('logfile.log', 'a') as file:
        file.write(f"""{formatDateTime} {file_name} Problem with db database conection - {str(e)}\n""")
        
try:     
    observed_dict = {
        row["link"]: {
            "title": row["title"],
            "followed_since": row["followed_since"],
            "city": row["city"],
            "price": row["price"],
            "przebieg": row["przebieg"],
            "rodzaj_paliwa": row["rodzaj_paliwa"],
            "skrzynia_biegow": row["skrzynia_biegow"],
            "typ_nadwozia": row["typ_nadwozia"],
            "pojemnosc_skokowa": row["pojemnosc_skokowa"],
            "moc": row["moc"],
            "rok_produkcji": row["rok_produkcji"],
            "model_pojazdu": row["model_pojazdu"],
        }
        for row in observed_data
    }

    deleted_dict = {
        row["link"]: {
            "title": row["title"],
            "city": row["city"],
            "followed_since": row["followed_since"],
            "ended_date": row["ended_date"],
            "duration": row["duration"],
            "price": row["price"],
            "lowest_price": row["lowest_price"],
            "przebieg": row["przebieg"],
            "rodzaj_paliwa": row["rodzaj_paliwa"],
            "skrzynia_biegow": row["skrzynia_biegow"],
            "typ_nadwozia": row["typ_nadwozia"],
            "pojemnosc_skokowa": row["pojemnosc_skokowa"],
            "moc": row["moc"],
            "rok_produkcji": row["rok_produkcji"],
            "model_pojazdu": row["model_pojazdu"],
        }
        for row in deleted_data
    }

except Exception as e:
    with open ('logfile.log', 'a') as file:
        file.write(f"""{formatDateTime} {file_name} Problem with converting db data to dict - {str(e)}\n""")

try:
    observed_body = observed_table(observed_dict)
    deleted_body = deleted_table(deleted_dict)
except Exception as e:
    with open ('logfile.log', 'a') as file:
        file.write(f"""{formatDateTime} {file_name} Problem with creating tables - {str(e)}\n""")


body = f"""
<h1>Observed auctions: {len(observed_dict)}, deleted auctions: {len(deleted_dict)}, updated data: {updated_count}, deleted data: {deleted_count}</h1>
"""
# Promotions are shown at the top
if promo_dict:
    promo_body = promo_table(promo_dict)
    body += promo_body

if observed_body:
    body += "<h2>Observed auctions</h2>"
    body += observed_body 
if deleted_body:
    body += "<h2>Deleted auctions</h2>"
    body += deleted_body   
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

conn.close()