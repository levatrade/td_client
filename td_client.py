import time
import urllib
import requests
from aiohttp import web
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

td_account_questions = ['What was the name of your junior high school?', 'What was the name of your first pet?', 'What is your best friend\'s first name?', 'In what city was your high school?']
td_account_question_answers = ['Como West', 'Danny', 'Robert', 'Sydney']

async def main_handler(request):
        params = await request.json()

        username = params['username']
        account_number = params['account_number']
        password = params['password']
        client_id = params['client_id']

        # --------------------- AUTHENTICATION AUTOMATION --------------------------

        # define the location of the Chrome Driver - CHANGE THIS!!!!!
        #executable_path = {'executable_path': r'/Users/Wiggum/Documents/WebDriver/chromedriver'}

        # Create a new instance of the browser, make sure we can see it (Headless = False)
        #browser = Browser('chrome', **executable_path, headless=False)
        #browser = webdriver.Chrome()
        browser = webdriver.Chrome(ChromeDriverManager().install())

        # define the components to build a URL
        method = 'GET'
        url = 'https://auth.tdameritrade.com/auth?'
        client_code = client_id + '@AMER.OAUTHAP'
        payload = {'response_type':'code', 'redirect_uri':'http://localhost', 'client_id':client_code}

        # build the URL and store it in a new variable
        p = requests.Request(method, url, params=payload).prepare()
        myurl = p.url

        # go to the URL
        browser.get(myurl)

        # define items to fillout form
        payload = {'username': username,
                'password': password}

        # fill out each part of the form and click submit
        username = browser.find_element_by_id("username0").send_keys(payload['username'])
        password = browser.find_element_by_id("password").send_keys(payload['password'])
        submit = browser.find_element_by_id("accept").click()
        By.XPATH, '//button[text()="Some text"]'
        text_message_label = browser.find_element(By.XPATH, '//summary[text()="Can\'t get the text message?"]').click()
        question_hyperlink = browser.find_element_by_name('init_secretquestion').click() 
        
        question_index = 0
        for question in td_account_questions:
                try:
                        print ('Searching for question', question)
                        label = browser.find_element(By.XPATH, '//*[text()[contains(., \'?\')]]')
                        # slowing down input behaviour
                        if question.lower() in label.text.lower():
                                question_answer = td_account_question_answers[question_index]
                                answer = browser.find_element_by_name("su_secretquestion").send_keys(question_answer)
                                break
                        question_index += 1
                except:
                        print ('Question not found', question)

        # click the Accept terms button
        browser.find_element_by_id("accept").click() 

        # trust page
        radio = browser.find_element_by_xpath(".//input[@type='radio' and @value='1']")
        browser.execute_script("arguments[0].click();", radio)
        browser.find_element_by_id("accept").click() 
        browser.find_element_by_id("accept").click() 

        # give it a second, then grab the url
        time.sleep(1)
        new_url = browser.current_url

        # grab the part we need, and decode it.
        decoded_code = urllib.parse.unquote(new_url.split('code=')[1])

        # close the browser
        browser.quit()

        # THE AUTHENTICATION ENDPOINT

        # define the endpoint
        url = r"https://api.tdameritrade.com/v1/oauth2/token"

        # define the headers
        headers = {"Content-Type":"application/x-www-form-urlencoded"}

        # define the payload
        payload = {'grant_type': 'authorization_code', 
                'access_type': 'offline',
                'code': decoded_code, 
                'client_id':client_id, 
                'redirect_uri':'http://localhost'}

        # post the data to get the token
        authReply = requests.post(r'https://api.tdameritrade.com/v1/oauth2/token', headers = headers, data=payload)

        # convert it to a dictionary
        decoded_content = authReply.json()     
        decoded_content['code'] = decoded_code                  

        # grab the access_token
        print (decoded_content)

        '''access_token = decoded_content['access_token']
        headers = {'Authorization': "Bearer {}".format(access_token)}

        # THE DAILY PRICES ENDPOINT 

        # define an endpoint with a stock of your choice, MUST BE UPPER
        endpoint = r"https://api.tdameritrade.com/v1/marketdata/{}/pricehistory".format('GOOG')

        # define the payload
        payload = {'apikey':client_id,
                'periodType':'day',
                'frequencyType':'minute',
                'frequency':'1',
                'period':'2',
                'endDate':'1556158524000',
                'startDate':'1554535854000',
                'needExtendedHoursData':'true'}

        # make a request
        content = requests.get(url = endpoint, params = payload)

        # convert it dictionary object
        data = content.json()'''

        return web.json_response(decoded_content)

'''

# THE QUOTE ENDPOINT 

# define an endpoint with a stock of your choice, MUST BE UPPER
endpoint = r"https://api.tdameritrade.com/v1/marketdata/{}/quotes".format('GOOG')

# define the payload
payload = {'apikey':client_id}

# make a request
content = requests.get(url = endpoint, params = payload)

# convert it dictionary object
data = content.json()

# THE QUOTES ENDPOINT 

# define an endpoint with a stock of your choice, MUST BE UPPER
endpoint = r"https://api.tdameritrade.com/v1/marketdata/quotes"

# define the payload
payload = {'apikey':client_id,
           'symbol':'GOOG,MSFT,AAPL'}

# make a request
content = requests.get(url = endpoint, params = payload)

# convert it dictionary object
data = content.json()



# THE MOVERS ENDPOINT 

# define an endpoint with a stock of your choice, MUST BE UPPER
endpoint = r"https://api.tdameritrade.com/v1/marketdata/{}/movers".format('$SPX.X')

# define the payload
payload = {'apikey':client_id,
           'direction':'up',
           'change':'value'}

# make a request
content = requests.get(url = endpoint, params = payload)

# convert it dictionary object
data = content.json()



# ACCOUNT ENDPOINT

# define an endpoint with a stock of your choice, MUST BE UPPER
endpoint = r"https://api.tdameritrade.com/v1/accounts/{}".format('426496649')

# define the payload
payload = {'apikey':client_id}

# make a request
content = requests.get(url = endpoint, headers = headers)

# convert it dictionary object
data = content.json()



# SEARCH INSTURMENTS - CUSIP

# define a CUSIP
CUSIP = '594918104'

# define an endpoint with a stock of your choice, MUST BE UPPER
endpoint = r"https://api.tdameritrade.com/v1/instruments/{}".format(CUSIP)

# define the payload
payload = {'apikey':client_id}

# make a request
content = requests.get(url = endpoint, params = payload, headers = headers)

# convert it dictionary object
data = content.json()



# SEARCH INSTURMENTS

# define an endpoint with a stock of your choice, MUST BE UPPER
endpoint = r"https://api.tdameritrade.com/v1/instruments"

# define the payload
payload = {'apikey':client_id,
           'projection':'fundamental',
           'symbol':'MSFT'}

# make a request
content = requests.get(url = endpoint, params = payload, headers = headers)

# convert it dictionary object
data = content.json()



# MARKET HOURS - SINGLE

# define an endpoint with a stock of your choice, MUST BE UPPER
endpoint = r"https://api.tdameritrade.com/v1/marketdata/{}/hours".format("FUTURE")

# define the payload
payload = {'apikey':client_id,
           'date': '2019-04-29'}

# make a request
content = requests.get(url = endpoint, params = payload, headers = headers)

# convert it dictionary object
data = content.json()



# MARKET HOURS - MULTIPLE

# define an endpoint with a stock of your choice, MUST BE UPPER
endpoint = r"https://api.tdameritrade.com/v1/marketdata/hours"

# define the payload
payload = {'apikey':client_id,
           'markets':'FUTURE',
           'date': '2019-04-29'}

# make a request
content = requests.get(url = endpoint, params = payload, headers = headers)

# convert it dictionary object
data = content.json()



# ACCOUNTS ENDPOINT

# define an endpoint with a stock of your choice, MUST BE UPPER
endpoint = r"https://api.tdameritrade.com/v1/accounts"

# make a request
content = requests.get(url = endpoint, headers = headers)

# convert it dictionary object
data = content.json()

# grab the account id
account_id = data[0]['securitiesAccount']['accountId']



# SAVED ORDERS ENDPOINT - POST

# define our headers
header = {'Authorization':"Bearer {}".format(access_token),
          "Content-Type":"application/json"}

# define the endpoint for Saved orders, including your account ID
endpoint = r"https://api.tdameritrade.com/v1/accounts/{}/savedorders".format(account_id)

# define the payload, in JSON format
payload = {'orderType':'MARKET',
           'session':'NORMAL',
           'duration':'DAY',
           'orderStrategyType':'SINGLE',
           'orderLegCollection':[{'instruction':'Buy','quantity':1,'instrument':{'symbol':'PINS','assetType':'EQUITY'}}]}


# make a post, NOTE WE'VE CHANGED DATA TO JSON AND ARE USING POST
content = requests.post(url = endpoint, json = payload, headers = header)

# show the status code, we want 200
content.status_code



# SAVED ORDERS ENDPOINT - GET ALL

# define our headers
header = {'Authorization':"Bearer {}".format(access_token)}

# define the endpoint for Saved orders, including your account ID
endpoint = r"https://api.tdameritrade.com/v1/accounts/{}/savedorders".format(account_id)

# make a post, NOTE WE ARE USING GET
content = requests.get(url = endpoint, headers = header)

# show the status code, we want 200
content.status_code

# parse the data sent back to us
data = content.json()

# grab the order ID
order_id = data[0]['savedOrderId']



# SAVED ORDERS ENDPOINT - GET SINGLE

# define our headers
header = {'Authorization':"Bearer {}".format(access_token)}

# define the endpoint for Saved orders, including your account ID
endpoint = r"https://api.tdameritrade.com/v1/accounts/{}/savedorders/{}".format(account_id, order_id)

# make a post, NOTE WE ARE USING GET
content = requests.get(url = endpoint, headers = header)

# show the status code, we want 200
content.status_code

# parse the json string
data = content.json()

# grab the order ID
order_id = data['savedOrderId']



# SAVED ORDERS ENDPOINT - DELETE

# define our headers
header = {'Authorization':"Bearer {}".format(access_token)}

# define the endpoint for Saved orders, including your account ID
endpoint = r"https://api.tdameritrade.com/v1/accounts/{}/savedorders/{}".format(account_id, order_id)

# make a post, NOTE WE ARE USING DELETE NOW
content = requests.delete(url = endpoint, headers = header)

# show the status code, we want 200
content.status_code'''

app = web.Application()
app.add_routes([web.post("/auth", main_handler)])
web.run_app(app, port=5000)