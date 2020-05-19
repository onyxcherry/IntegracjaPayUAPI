#!/usr/bin/env python

import getpass
import json
import os
import platform
import random
import sys

import bcrypt

from RestApi import RestApi

random_value = random.random() + 3
exrate_buy = round(random_value, 3)
exrate_sell = round(random_value - (random.random() / 5), 3)

print(exrate_sell, exrate_buy)

real_dir = os.path.dirname(os.path.abspath(__file__))

with open(real_dir + '/secrets.json', 'r') as secrets:
  json_data = json.load(secrets)

  client_id = json_data['oauth_creds']['posId']
  client_secret = json_data['oauth_creds']['client_secret']

with open(real_dir + '/config.json', 'r') as config:
  json_data = json.load(config)

  authorize_url = json_data['urls']['authorize_url']

  insurance_unitprice = json_data['price']['insurance_unitprice']
  pycoins_unitprice = json_data['price']['pycoins_unitprice']


class UserInterface(RestApi):

  def __init__(self):
    self.exrate_sell = exrate_sell
    self.exrate_buy = exrate_buy
    self.user_authenticated = False

  def print_redirect_link(self, response_redirect_url):
    print(f'Correctly!\n'
          f'Pay at: {response_redirect_url}')

  def show_help(self):
    print('_' * 30)
    print(f'\nWelcome to Python shop!\n'
          f'In our shop you can buy and sell pretty coins.\n'
          f'We accept payment using PayU!\n'
          f'For instance:')
    self.print_exchange_rates()

  def print_thanks_to_user(self, order_id):
    print(f'Thank for buying our product.\n'
          f'Your order {order_id} will be realized as fast as '
          f'we could do it')

  def add_pycoins_quantity(self, username, pycoins_quantity):
    with open("newusers.json", "r+") as users:
      json_data = json.load(users)

    json_data[username]['pycoins'] += pycoins_quantity

    with open("newusers.json", "w") as users:
      json.dump(json_data, users, indent=2)

  def get_quantity(self, what):
    try:
      pycoins_quantity = int(input(f'How many PyCoins do you want to '
                                   f'{what}?\n'))
    except ValueError:
      sys.exit("No valid integer.")

    if pycoins_quantity > 0:
      return pycoins_quantity
    sys.exit('No valid integer.')

  def calculate_total_amount(self, pycoins_quantity):
    total_amount = round(insurance_unitprice
                         + pycoins_quantity * pycoins_unitprice)

    if 0 < total_amount <= 99999999:
      return total_amount
    sys.exit('No valid amount.')

  def buy(self):

    pycoins_quantity = self.get_quantity('buy')
    total_amount = self.calculate_total_amount(pycoins_quantity)
    access_token = self.authorize()

    redirect_uri, order_id = self.send_request(access_token,
                                               pycoins_unitprice,
                                               pycoins_quantity,
                                               insurance_unitprice,
                                               total_amount)

    self.print_redirect_link(redirect_uri)
    if self.check_if_user_paid(access_token, order_id):
      self.login()
      self.add_pycoins_quantity(self.username, pycoins_quantity)

  def check_if_user_paid(self, access_token, order_id):

    user_paid = input("Did you pay? (yes)/(no) ")
    if user_paid.casefold() == "yes":
      if (self.get_order_status(access_token, order_id)):
        self.print_thanks_to_user(order_id)
        return True
      else:
        print("Do not lie!")
        return False
    else:
      print("Why not?")
      return False

  def sell(self):
    print('Selling module')
    self.print_exchange_rates()
    pycoins_quantity = self.get_quantity('sell')
    print(f'Do you want to sell {pycoins_quantity} PyCoins?')

  def get_user_password(self):
    user_platform = platform.system()
    if user_platform == 'Linux':
      user_password = getpass.getpass(prompt='Your password:')
    else:
      user_password = input('Your password: ')

    # user_password_hashed = hashlib.sha256(bytes(user_password,
    #                                            "utf-8")).hexdigest()
    # salt = bcrypt.gensalt(rounds=12)
    # hashed_password = bcrypt.hashpw(user_password, salt)
    # tutaj będzie trzeba dopisać moduł rejestracji lub logowania
    # dlatego powyższe nie powinno znaleźć się tutaj - a w innej funkcji odpowiedzialnej za logowanie/rejestrację

    # if user_password_hashed == user_password_hash:
    #  return True

    # return False
    return user_password

  def check_if_passwords_match(self, user_password, hashed):

    if bcrypt.checkpw(user_password.encode(), hashed.encode()):
      return True
    return False

  def load_password_hash(self, user_id):
    with open("newhashes.json", "r") as hashes:
      json_data = json.load(hashes)
      hashed = json_data[f'{user_id}']['hash']

    return hashed

  def get_username(self):
    username = input("Your login: ")
    return username

  def load_user_id(self, username):

    with open("newusers.json", "r") as users:
      json_data = json.load(users)

    if username in json_data:
      user_id = json_data[f'{username}']['id']
      return user_id
    sys.exit("Invalid username")

  def login(self):

    if self.user_authenticated:
      return True

    # attempts_count = 3
    # while (attempts_count):
    username = self.get_username()
    user_id = self.load_user_id(username)
    user_password = self.get_user_password()
    hashed = self.load_password_hash(user_id)

    if self.check_if_passwords_match(user_password, hashed):
      self.user_authenticated = True
      self.username = username
      return True
    # return False

  def print_account_balance(self):

    if self.login():
      print('Logged in.')
      account_balance = self.check_account_balance()
      print(f'Your account balance: {account_balance}')
    else:
      print('Access denied!')

  def check_account_balance(self):
    print('Checking account balance module')
    with open("newusers.json", "r") as users:
      json_data = json.load(users)
      account_balance = json_data[f'{self.username}']['pycoins']

    return account_balance

  def logout(self):
    self.user_authenticated = False
    print('Logged out.')

  def quit_from_shop(self):
    print('See you later!')
    sys.exit(0)

  def print_avaible_options(self):
    print('_' * 30)
    print('0 - Show help\n'
          '1 - Buy\n'
          '2 - Sell\n'
          '3 - Check account balance\n'
          '4 - Logout\n'
          '5 - Exit\n')

  def print_exchange_rates(self):

    print(f'Current exchange rate:\n'
          f'Sell: {exrate_sell}\n'
          f'Buy: {exrate_buy}')

  def get_user_choice(self, user_choice):
    user_choice = user_choice
    switcher = {
      0: self.show_help,
      1: self.buy,
      2: self.sell,
      3: self.print_account_balance,
      4: self.logout,
      5: self.quit_from_shop,
    }

    switcher.get(user_choice, self.quit_from_shop)()
