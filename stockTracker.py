# Author: Andrew Simonds
# Imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from twilio.rest import Client
import os.path
from simple_chalk import chalk


def getPrice(prevPrice):
    # Grab updated price
    driver.refresh()
    try:
        time.sleep(3)
        # Find price using xpath
        newPrice = driver.find_element_by_xpath(
            '/html/body/div[1]/div[3]/div[1]/div/div[1]/div/div[2]/div[1]/span').text
        newPrice = float(newPrice[1:])
        return round(newPrice, 2)
    except:
        print('Error getting price, returning previous price...')
        return prevPrice


def buyOrSell():
    print("\nAre you monitoring to BUY or SELL: ")
    for idx, element in enumerate([chalk.green('BUY'), chalk.green('SELL')]):
        print('{}) {}'.format(idx+1, element))
    i = input('Enter Number: ')
    try:
        if i == '1':
            return 'BUY'
        elif i == '2':
            return 'SELL'
        else:
            return 'ERROR'
    except:
        print('Error: Invalid Option')
        return None


def changeTicker():
    print("If you wish to change the ticker symbol to watch, type it below")
    print("Otherwise, press " + chalk.green.bold("ENTER"))
    i = input(chalk.green('Enter Ticker Symbol: '))
    if i == '':
        pass
    else:
        global tickerSymbol
        tickerSymbol = i
        os.remove('twilioInfo.txt')
        infoFile = open('twilioInfo.txt', 'a')
        writeInfo = (
            'Account Number: {}Account Token: {}Twilio Number: {}My Number: {}Ticker Symbol: {}'.format(userID, authToken, twilioNumber, myNumber, tickerSymbol))
        infoFile.write(writeInfo)
        infoFile.close()


# Initialize some information values
if (os.path.isfile('./twilioInfo.txt')):
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
    # Ticker Symbol being watched
    tickerSymbol = (info[4].split(': ', 1))[1]
    infoFile.close()
else:
    infoFile = open('twilioInfo.txt', 'a')
    userID = input('Enter Twilio user ID: ')
    authToken = input('Enter Twilio authentication token: ')
    twilioNumber = input('Enter Twilio Phone number: ')
    myNumber = input('Enter your phone number: ')
    tickerSymbol = input('Enter Ticker Symbol to watch: ')
    writeInfo = (
        'Account Number: {}\nAccount Token: {}\nTwilio Number: {}\nMy Number: {}\nTicker Symbol: {}'.format(userID, authToken, twilioNumber, myNumber, tickerSymbol))
    infoFile.write(writeInfo)
    infoFile.close()

# Change stock to watch?
print('\nCurrently watching prices of {}...'.format(chalk.green(tickerSymbol)))
changeTicker()
# Choose if waiting to buy or sell
buyingOrSelling = buyOrSell()
# Set price to watch for
lowPrice = float(input(chalk.red('\nLow price to watch for?: ')))
highPrice = float(input(chalk.green('High price to watch for?: ')))

# Initialize Twilio Client
client = Client(userID, authToken)

# Initialize selenium settings
DRIVER_PATH = 'C:/webdrivers/chromedriver.exe'

options = Options()
options.headless = True
options.add_argument("--window-size=1920,1200")
options.add_argument("--log-level=3")  # Supress warning logs for visibility

# Start webpage
driver = webdriver.Chrome(
    options=options, executable_path=DRIVER_PATH)
driver.get('https://money.tmx.com/en/quote/{}'.format(tickerSymbol))

# Instantiate first watch price
price = getPrice(None)

# Check for new price twice every minute
while True:
    # Wait for price drop
    if(price < lowPrice):
        print(chalk.green.bold('Sending text to ' + buyingOrSelling))
        client.messages.create(to=myNumber, from_=twilioNumber,
                               body="Price dropped below ${:.2f}! Time to {} some shares of {}!".format(lowPrice, buyingOrSelling, tickerSymbol))
        break
    # Wait for price increase
    elif(price > highPrice):
        print(chalk.green.bold('Sending text to ' + buyingOrSelling))
        client.messages.create(to=myNumber, from_=twilioNumber,
                               body="Price increased above ${:.2f}! Time to {} your shares of {}!".format(highPrice, buyingOrSelling, tickerSymbol))
        break
    else:
        # price = chalk.green("$" + price)
        print(chalk.magenta('Current price: ') + chalk.green('$' + str(price)) + chalk.magenta(
            ' Continuing to monitor ') + chalk.magenta.bold(tickerSymbol) + chalk.magenta(' prices...'))

    time.sleep(30)
    price = getPrice(price)

# Shut down driver
driver.quit()
