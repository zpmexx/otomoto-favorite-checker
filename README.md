# Otomoto followed auctions checker

### Scripts are using selenium framework with google driver to log in into your [OtoMoto](https://www.otomoto.pl) account, check followed auctions and send and email with information about:

- **Auction link, date of follow, city, price, mileage of car, fuel type, gearbox type, body type, engine displacement, horsepower, year, model**

1. **Two scripts:**
	- **get_favorites.py - a script that logs into your account, checks for new auctions, and inserts them into the database.**
	- **get_extra_data.py - a script that checks each auction, collects additional data, or marks the auction as ended if it has finished. It also sends an email with a summary.**
2. **To run both scripts you need to:**
	- **Install requirements** `pip install -r req.txt`
	- **fill .env file with required data**
		- login = 'email address of otomoto account'
		- password = 'password of otomoto account'
		- from_address = 'email address of an account that will send an email'
		- email_password = 'password of email account that will send an email'
		- to_address = ["firstemail@email.com", "secondemail@email.com"] etc, may be just single email address but list format is required
	- **Run or schedule automatic runs of the `get_favorites.py` file to insert auctions into the database. This script must always be executed before `get_extra_data.py` to ensure the newest auctions are included in the summary."**
	- **Run or schedule automatic runs of the `get_extra_data.py` file to collect more specific data and send a summary**
### !!! These scripts work with Chrome Driver and an Outlook email account. If you want to use a different browser or email provider, you will need to slightly modify the code.
