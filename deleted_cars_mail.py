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

      
try:
    with open('deleted_cars.json', 'r') as json_file:
        deleted_cars_dict = json.load(json_file)
except Exception as e:
    deleted_cars_dict = {}
    with open ('logfile.log', 'a') as file:
        file.write(f"""{formatDateTime} Problem with reading deleted_cars.json - {str(e)}\n""")

#sort by duration desc
deleted_cars_dict = dict(sorted(deleted_cars_dict.items(), key=lambda item: item[1]['duration'], reverse=True))

body = ''
if not deleted_cars_dict:
    body = "No deleted auctions (check log file)."
else:
    body += f"<h2>Number of deleted auctions: {len(deleted_cars_dict)}</h2>"
    body += """
    <table border="1" cellpadding="10" cellspacing="0" style="width: 100%; border-collapse: collapse;">
        <thead>
            <tr>
                <th style="text-align: center;">Name</th>
                <th style="text-align: center;">City</th>
                <th style="text-align: center;">Followed since</th>
                <th style="text-align: center;">Ended date</th>
                <th style="text-align: center;">Auction duration (days)</th>
                <th style="text-align: center;">Price</th>
            </tr>
        </thead>
        <tbody>
    """

# Dynamically generating table rows
    for link, data in deleted_cars_dict.items():
        body += f"""
            <tr>
                <td style="text-align: center;">{data['title']}</td>
                <td style="text-align: center;">{data['city']}</td>
                <td style="text-align: center;">{data['followed_since']}</td>
                <td style="text-align: center;">{data['ended_date']}</td>
                <td style="text-align: center;">{data['duration']}</td>
                <td style="text-align: center;">{data['price']}</td>
            </tr>
        """
        
    # End of the table
    body += """
        </tbody>
    </table>
    """

try:
    #send and email
    to_address_loaded = json.loads(to_address)

    try:
        msg = MIMEMultipart()
        msg['From'] = from_address
        msg["To"] = ", ".join(to_address_loaded)
        msg['Subject'] = f"{formatDateTime} Otomoto deleted auctions status"
        
    except Exception as e:
        with open ('logfile.log', 'a') as file:
            file.write(f"""Problem z wysłaniem email - {str(e)}\n""")


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