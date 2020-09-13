# Author: Andrew Simonds
# Imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from twilio.rest import Client

# Change prices here for what you wanna watch for
highPrice = float(8.75)
lowPrice = float(8)

# Change which stock symbol you want to monitor
tickerSymbol = 'CGX'

# Get Twilio Info
infoFile = open('twilioInfo.txt', 'r')
info = infoFile.readlines()
# Parse info from text file into usable variables
# UserID info from Twilio; Format in file -> Account Number: ###########
userID = (info[0].split(': ', 1))[1]
# Token from twilio; Format in file -> Account Token: ###########
authToken = (info[1].split(': ', 1))[1]
# Twilio Phone Number; Format in file -> Twilio Number: +##########
twilioNumber = (info[2].split(': ', 1))[1]
# User Phone Number; Format in file -> My Number: +##########
myNumber = (info[3].split(': ', 1))[1]

# Initialize Twilio Client
client = Client(userID, authToken)

# Initialize selenium settings
DRIVER_PATH = 'C:/webdrivers/chromedriver.exe'

options = Options()
options.headless = True
options.add_argument("--window-size=1920,1200")

# Start webpage
driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
driver.get('https://money.tmx.com/en/quote/{}'.format(tickerSymbol))


def getPrice():
    # Grab updated price
    driver.refresh()
    try:
        time.sleep(3)
        # Find price using xpath
        price = driver.find_element_by_xpath(
            '/html/body/div[1]/div[3]/div[1]/div/div[1]/div/div[2]/div[1]/span').text
        price = float(price[1:])
        return price
    except:
        print('Error getting price')


# Check for new price twice every minute
while True:
    price = getPrice()
    # Wait for price drop to notify a buy
    if(price < lowPrice):
        print('Sending text to buy')
        client.messages.create(to=myNumber, from_=twilioNumber,
                               body="Price dropped below ${:.2f}! Time to buy some shares of {}!".format(lowPrice, tickerSymbol))
        break
    # Wait for price increase to notify a sell
    elif(price > highPrice):
        print('Sending text to sell')
        client.messages.create(to=myNumber, from_=twilioNumber,
                               body="Price increased above ${:.2f}! Time to sell your shares of {}!".format(highPrice, tickerSymbol))
        break
    else:
        print('Current price: ${}.  Continuing to monitor {} prices...'.format(
            price, tickerSymbol))
    time.sleep(30)

# Shut down driver
driver.quit()
