# Otomoto followed auctions checker

### Scripts are using selenium framework with google driver to log in into your [OtoMoto](https://www.otomoto.pl) account, check followed auctions and send and email with information about:

- **Auction link, date of follow, city, price, mileage of car, fuel type, gearbox type, body type, engine displacement, horsepower, year, model**

1. **Two scripts:**
	- **get_favorites.py - Script that log into your account, checks for new auctions and inserts them into the database.**
	- **get_extra_data.py - Script that checks each auction, collects additional data (or marks the auction as ended if it has finished). It also sends an email with a summary.**
2. **To run both scripts you need to:**
	- **Install requirements** `pip install -r req.txt`
	- **fill .env file with required data**
		- login = 'otomoto email address'
		- password = 'otomoto password'
		- from_address = 'email address of account that will send an email'
		- email_password = 'password of email account that will send an email'
		- to_address = ["firstemail@email.com", "secondemail@email.com"] etc, may be just single email address but list format is required
	- **Run or schedule automatic runs of the `get_favorites.py` file to insert new auctions into the database. This script must always be executed before `get_extra_data.py` to ensure the newest auctions are included in the summary. This scripts also creates a file with auctions that are no longer observed at otomoto, but are still active, also in db.**
	- **Run or schedule automatic runs of the `get_extra_data.py` file to collect more specific data and send a summary**
	- **pass auction's link to delete_link_from_db.py script to delete it completely from database (probably no longer observed auction in otomoto account but still visible into db and summary).**
### !!! These scripts work with Chrome Driver and an Outlook email account. If you want to use a different browser or email provider, you will need to slightly modify the code.
