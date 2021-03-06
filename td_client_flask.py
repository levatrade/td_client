import time
import urllib
import requests
from splinter import Browser

from flask import Flask, make_response, request, current_app, jsonify, send_file
import json
import subprocess
import getopt
import sys
 
from flask_restful import Resource, Api, reqparse
from functools import update_wrapper
from datetime import timedelta
from functools import update_wrapper
from flask_cors import CORS, cross_origin

# api app
flask_app = Flask(__name__)
api = Api(flask_app)
CORS(flask_app)

parser = reqparse.RequestParser()
parser.add_argument('task')

class TDConfiguration(Resource):
    def get(self):
        return "Welcome to the TD API!"
    def post(self):
        params = request.get_json(force=True)
        username = params['username']
        account_number = params['account_number']
        password = params['password']
        client_id = params['client_id']

        # --------------------- AUTHENTICATION AUTOMATION --------------------------

        # define the location of the Chrome Driver - CHANGE THIS!!!!!
        executable_path = {'executable_path': r'/usr/bin/chromedriver'}

        # Create a new instance of the browser, make sure we can see it (Headless = False)
        browser = Browser('chrome', **executable_path, headless=True)

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

        # click the Accept terms button
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

        return decoded_content

api.add_resource(TDConfiguration, '/auth') # Route_1

ip = '0.0.0.0'

if __name__ == '__main__':
    flask_app.run(host=ip, debug=True, port=5000)