# Otomoto followed auctions checker

### Scripts are using selenium framework with google driver to log in into your [OtoMoto](https://www.otomoto.pl) account, check followed auctions and send and email with information about:
-**Name and link of auction**

-**Date since you are following specific auction**

-**Place where this car is located**

-**Price of an car**

1. **Two scripts:**
	- **main.py - main script that is doing everything mentioned above**
	- **deleted_cars_mail.py - script that is sending other email with deleted auctions (not available anymore)**
2. **To run both scripts you need to:**
	- **Install requirements** `pip install -r req.txt`
	- **fill .env file with required data**
		- login = 'email address of otomoto account'
		- password = 'password of otomoto account'
		- from_address = 'email address of an account that will send an email'
		- email_password = 'password of email account that will send an email'
		- to_address = ["firstemail@email.com", "secondemail@email.com"] etc, may be just single email address but list format is required
	- **run `python main.py` file**
	- **every single exception will be stored into .log file**

<span style="color: red; font-size: 1.5em;">Scripts are working with chrome driver and outlook email account, if you would like to use other browser or email provider you will need to slightly modify the code</span>