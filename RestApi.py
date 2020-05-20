#!/usr/bin/env python

import json
import os
import sys

import requests

real_dir = os.path.dirname(os.path.abspath(__file__))

with open(real_dir + '/secrets.json', 'r') as secrets:
  json_data = json.load(secrets)

client_id = json_data['oauth_creds']['posId']
client_secret = json_data['oauth_creds']['client_secret']

with open(real_dir + '/config.json', 'r') as config:
  json_data = json.load(config)

order_url = json_data['urls']['order_url']
authorize_url = json_data['urls']['authorize_url']
notify_url = json_data['urls']['notify_url']


class RestApi:

  def __init__(self):
    pass

  def authorize(self):
    authorize_data = {
      'grant_type': 'client_credentials',
      'client_id': f'{client_id}',
      'client_secret': f'{client_secret}'
    }

    authorize_response = requests.post(authorize_url, data=authorize_data)
    json_response = json.loads(authorize_response.text)

    if authorize_response.status_code == 200:
      if json_response['access_token']:
        access_token = json_response['access_token']
      else:
        sys.exit('No access token in OAuth response.')
    else:
      sys.exit('Status code different than 200.')

    return access_token

  def send_request(self, access_token, pycoins_unitprice,
                   pycoins_quantity, insurance_unitprice, total_amount):

    order_headers = {
      'Content-Type': 'application/json',
      'Authorization': f'Bearer {access_token}',
    }

    data = {
      'notifyUrl': f'{notify_url}',
      'customerIp': '127.0.0.1',
      'merchantPosId': f'{client_id}',
      'description': 'PyCoins',
      'currencyCode': 'PLN',
      'totalAmount': f'{total_amount}',
      'buyer': {
        'email': 'john.doe@example.com',
        'phone': '654111654',
        'firstName': 'John',
        'lastName': 'Doe',
        'language': 'pl'
      },
      'settings': {
        'invoiceDisabled': 'true'
      },
      'products': [
        {
          'name': 'PyCoins',
          'unitPrice': f'{pycoins_unitprice}',
          'quantity': f'{pycoins_quantity}'
        },
        {
          'name': 'Insurance',
          'unitPrice': f'{insurance_unitprice}',
          'quantity': '1'
        }
      ]
    }

    response = requests.post(order_url, headers=order_headers,
                             data=json.dumps(data), allow_redirects=False)

    # Note that PayU REST API sends json data with statusCode,
    # redirectUri and orderId (with HTTP 302 Found status code)
    # and then redirect to redirectUri, so firstly we get 302

    if response.status_code == 302:
      response_to_json = json.loads(response.text)
      json_statusCode = response_to_json['status']['statusCode']

      if json_statusCode == 'SUCCESS':
        redirect_link = response_to_json['redirectUri']
        order_id = response_to_json['orderId']

        return redirect_link, order_id

      else:
        sys.exit('Status code different than SUCCESS.')
    else:
      sys.exit('Status code different 302.')

  def get_order_status(self, access_token, order_id):

    headers = {'Authorization': f'Bearer {access_token}'}
    url = order_url + '/' + order_id
    response = requests.get(url, headers=headers)

    json_data = json.loads(response.text)
    status_code = json_data['status']['statusCode']
    order_status = json_data['orders'][0]['status']

    if status_code == 'SUCCESS' and order_status == 'COMPLETED':
      return True

    return False
