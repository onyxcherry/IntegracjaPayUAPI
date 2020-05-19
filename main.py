#!/usr/bin/env python

from UserInterface import UserInterface


def main():
  interface = UserInterface()
  interface.print_exchange_rates()

  while (True):
    interface.print_avaible_options()
    try:
      user_choice = int(input('Hello! What do you want to do?\n'))
    except ValueError:
      print('I don\'t understand!')
      interface.quit_from_shop()
    else:
      # print(user_choice)
      # print(type(user_choice))
      interface.get_user_choice(user_choice)


if __name__ == "__main__":
  main()
