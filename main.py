import sqlite3
import pyinputplus as pyip
import random
import sys 
import os
import time

db_name = 'banking_app.db'

#Simulates connecting to the database. Not actually needed, but it makes the program feel a bit more realistic
connection = sqlite3.connect(db_name)
print("Initiating database connection...")
time.sleep(2)
print("Connected to the database.")#just to let me know that the function is working
time.sleep(3)
os.system('clear')
cur = connection.cursor()
cur.execute("DROP TABLE IF EXISTS accounts")
cur.execute("CREATE TABLE IF NOT EXISTS accounts(account_id, pin, username, email)")
cur.execute("CREATE TABLE IF NOT EXISTS account_balance(account_id, balance)")#the balance of the account is set to 0 by default the the vairable 'money' is set to 5000 to make it possible to test the program
cur.execute("INSERT INTO accounts VALUES(?, ?, ?, ?)", (1, 9779233314, "admin", "admin@admin.com"))
#makes the admin account beforehand so that only they can see certain options in the main menu


accounts = []
admin_accounts = [1]#this is for the accounts who are allowed to see the admin options in the main menu
money = 5000.0
admin_flag = False
temp_account = 0#lets me know what account is currently being used
temp_pin = 0 #lets me know what pin is currently being used


def cs():#makes it easier to clear the screen when needed and makes a little pause before actually clearing the screen
  time.sleep(1.75)
  os.system('clear')

def account_to_lists():#makes it easier to check if an account exists or not
  accounts = []
  i = 0
  for row in cur.execute("SELECT account_id FROM accounts"):
    accounts.append(row[i])
    i += 1


def create_account():
  global temp_pin
  global temp_account
  account_number = random.randint(1000, 9999)#these numbers are for how many different accounts the bank can have. In reality, these numbers would be much larger, but for this project, I have set them to be much smaller in scale. 
  if account_number in accounts:
    create_account()
  else:
    temp_account = account_number
    try:
      pin = int(input("Enter your pin(must be 6 digits long): "))
      if pin < 100000:
        print("Pin must be at least 6 digits long")
        cs()
        create_account()
    except ValueError:
      print("Pin must be a number")
      cs()
      create_account()
    else:
      temp_pin = pin
      pass
    username = input("Enter your username: ")
    email = input("Enter your email: ")
    print("Your account has been successfully created")
    print("Your account number is: ", account_number, " and your pin is: ", pin, "Please remember these for future use")
    cur.execute("INSERT INTO accounts VALUES(?, ?, ?, ?)", (account_number, pin, username, email))
    time.sleep(5)
    sign_in_menu()

def deposit():
  global money
  deposit_amount = float(input(f"You have {money} $. How much would you like to deposit? "))
  if deposit_amount > money:
    print("You don't have that much money")
    cs()
    deposit()
  else:
    money -= deposit_amount
    cur.execute("UPDATE account_balance SET balance = balance + ? WHERE account_id = ?", (deposit_amount, temp_account))
    print("You have deposited ", deposit_amount, "$")
    print("Your new balance is: ", cur.execute("SELECT balance FROM account_balance WHERE account_id = ?", (temp_account,)), "$")

def withdraw():
  global money
  try:
    withdraw_amount = float(input(f"You have {money} $. How much would you like to withdraw? "))
  except ValueError:
    print("You must enter a number")
    cs()
    withdraw()
  else:
    money += withdraw_amount
    cur.execute("UPDATE account_balance SET balance = balance - ? WHERE account_id = ?", (withdraw_amount, temp_account))

def manage_accounts():
  print("---------------------------------------")
  print("1. View Accounts")
  print("2. Delete Account")
  print("3. Back to main menu")
  try:
    option = int(input("Enter your option: "))
    if option not in [1, 2, 3]:
      print("Invalid option")
      cs()
      manage_accounts()
  except ValueError:
    print("You must enter a number")
    cs()
    manage_accounts()
  if option == 1:
    for row in cur.execute("SELECT * FROM accounts"):
      print(row)
  elif option == 2:
    print("What account would you like to delete?")
    account = int(input("Enter account number: "))
    print("Are you sure you want to delete this account?(this action cannot be undone)")
    print("1. Yes")
    print("2. No")
    try:
      option = int(input("Enter your option: "))
      if option not in [1, 2]:
        print("Invalid option")
        cs()
        manage_accounts()
    except ValueError:
      print("You must enter a number")
      cs()
      manage_accounts()
    if option == 1:
      print("Removing account...")
      cur.execute("DELETE FROM accounts WHERE account_id = ?", (account,))
      time.sleep(5)
      print("Account sucessfully removed")
    elif option == 2:
      print("Account not removed")
      cs()
      manage_accounts()


def sign_in_menu():
  global temp_account
  global temp_pin
  pin = 0
  print("---------------------------------------")
  print("Welcome to Banking for you")
  print("1. Sign in")
  print("2. Create account")
  try:
    option = int(input("Enter your option: "))
    if option == 1:
      account_to_lists()
      print(accounts)
      id = str(input("What is your Account id? "))
      for i in range(len(accounts)):
        if id == accounts[i]:
          temp_account = id
        else:
          print("that id doesn't exist")
          cs()
          sign_in_menu()
      print("Account found")
      pin = int(input("What is your pin?"))
      print(cur.execute("SELECT pin FROM accounts WHERE account_id = ?", (temp_account,)))
      check = cur.fetchone()
      check_pin = check[0]
      print(check_pin)
      if int(pin) == check_pin:
        print("Correct pin")
        print("Signing in...")
        cs()
        main_menu()
      else:
        print("Incorrect pin")
        cs()
        sign_in_menu()
    elif option == 2:
      create_account()
    else:
      print("Invalid option")
      cs()
      sign_in_menu()
  except ValueError:
    print("That is not a valid option")
    cs()
    sign_in_menu()

def edit_account():
  global temp_account
  print("Welcome to the account editor. What would you like to do?")
  print("1. Change username")
  print("2. Change email")
  print("3. Change pin")
  print("4. Delete account")
  print("5. Back to main menu")
  try:
    option = int(input("Enter your option: "))
    if option not in [1, 2, 3, 4, 5]:
      print("Invalid option")
      cs()
      edit_account()
    elif option == 1:
      username = input("Enter your new username: ")
      cur.execute("UPDATE accounts SET username = ? WHERE account_id = ?", (username, temp_account))
    elif option == 2:
      email = input("Enter your new email: ")
      cur.execute("UPDATE accounts SET email = ? WHERE account_id = ?", (email, temp_account))
    elif option == 3:
      pin = int(input("Enter you new pin: "))
      conf_pin = int(input("Confirm your new pin: "))
      if pin == conf_pin:
        cur.execute("UPDATE accounts SET pin = ? WHERE account_id = ?", (pin, temp_account))
        print("Pin successfully changed")
        cs()
        edit_account()
      else:
        print("Pins do not match. Please try again")
        cs()
        edit_account()
    elif option == 4:
      print("Are you sure you want to delete this account?(this action cannot be undone)")
      print("1. Yes")
      print("2. No")
      try:
        option = int(input("Enter your option: "))
        if option not in [1, 2]:
          print("Invalid option")
          cs()
          edit_account()
      except ValueError:
        print("You must enter a number")
        cs()
        edit_account()
      if option == 1:
        print("Removing account...")
        cur.execute("DELETE FROM accounts WHERE account_id = ?", (temp_account,))
        time.sleep(5)
        print("Account sucessfully removed")
        cs()
        temp_account = 0
        sign_in_menu()
      elif option == 2:
        print("Account not removed")
        cs()
        edit_account()
    elif option == 5:
      print("Returning to main menu...")
      cs()
      main_menu()
  except ValueError:
    print("That is not a valid option")
    cs()
    edit_account()

def main_menu():
  print("---------------------------------------")
  print("Welcome to Banking for you")
  print("1. Deposit")
  print("2. Withdraw")
  print("3. Check balance")
  print("4. Sign out")
  if temp_account == 1:
    print("5. View/delete account(s)")
    print("---------------------------------------")
  option = int(input("Enter your option: "))
  if option == 1:
    cs()
    deposit()
  elif option == 2:
    cs()
    withdraw()
  elif option == 3:
    cs()
    balance = cur.execute("SELECT balance FROM account_balance WHERE account_id = ?", (temp_account,))
    print("Your balance is: ", balance, "$")
  elif option == 4:
    edit_account()
  elif option == 5:
    print("Have a good day!")
    print("Signing out...")
    cs()
    sign_in_menu()
  elif option == 6 and temp_account == 1:
    manage_accounts()
    cs()
  else:
    print("Invalid option")
    cs()
    main_menu()




sign_in_menu()





