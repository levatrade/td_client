import time
import urllib
import requests
from splinter import Browser
from aiohttp import web

td_account_questions = ['What is your paternal grandfather\'s first name', 'What is your paternal grandmother\'s first name', 'What was your high school mascot', 'In what city was your high school']
td_account_question_answers = ['Charles', 'Mary', 'Rebel', 'Bakersfield']

def main_handler(request):
        #params = request.json()

        username = request['username']
        account_number = request['account_number']
        password = request['password']
        client_id = request['client_id']

        # --------------------- AUTHENTICATION AUTOMATION --------------------------

        # define the location of the Chrome Driver - CHANGE THIS!!!!!
        executable_path = {'executable_path': r'/usr/bin/chromedriver'}

        # Create a new instance of the browser, make sure we can see it (Headless = False)
        browser = Browser('chrome', **executable_path, headless=False)

        # define the components to build a URL
        method = 'GET'
        url = 'https://auth.tdameritrade.com/auth?'
        client_code = client_id + '@AMER.OAUTHAP'
        payload = {'response_type':'code', 'redirect_uri':'http://localhost', 'client_id':client_code}

        # build the URL and store it in a new variable
        p = requests.Request(method, url, params=payload).prepare()
        myurl = p.url

        # go to the URL
        browser.visit(myurl)

        # define items to fillout form
        payload = {'username': username,
                'password': password}

        # fill out each part of the form and click submit
        username = browser.find_by_id("username").first.fill(payload['username'])
        password = browser.find_by_id("password").first.fill(payload['password'])
        submit = browser.find_by_id("accept").first.click()
        text_message_label = browser.find_by_text("Can't get the text message?").first.click()
        question_hyperlink = browser.find_by_value("Answer a security question").first.click()

        question_index = 0
        for question in td_account_questions:
                try:
                        print ('Searching for question', question)
                        p_labels = browser.find_by_tag('p')
                        if question in p_labels[2].text:
                        question_answer = td_account_question_answers[question_index]
                        answer = browser.find_by_name("su_secretquestion").first.fill(question_answer)
                except:
                        print ('Question not found', question)

        question_index += 1

        # click the Accept terms button
        browser.find_by_id("accept").first.click() 
        browser.find_by_id("accept").first.click() 

        # give it a second, then grab the url
        time.sleep(1)
        new_url = browser.url

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