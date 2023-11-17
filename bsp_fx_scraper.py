#!/usr/bin/env python3
import csv
import os
import time
import sys
from datetime import datetime
from sys import platform

try:
  from bs4 import BeautifulSoup
  import requests
except:
  sys.exit(sys.argv[0] +
           " maybe 'pip install requests bs4 lxml' first, then try again.\n")

url = "http://www.bsp.com.pg/International/Exchange-Rates/Exchange-Rates.aspx"

if platform == "linux" or platform == "linux2":
  home = os.environ['HOME']
  data, country_code, csv_file, csv_codes = {}, {}, home + os.sep + ".bsp_rates.csv", home + os.sep + ".cc.csv"
  clear = 'clear'
#else: #platform == "win32":
#home = os.environ['USERPROFILE']
#data, country_code, csv_file, csv_codes = {}, {}, home + os.sep +  ".bsp_rates.csv", home + os.sep + ".cc.csv"
#clear = 'cls'


def get_fx_rates():
  # The main function that saves the rates and codes
  try:
    r = requests.get(url, timeout=15)
  except:
    sys.exit("Check Internet Connection")

  soup = BeautifulSoup(r.text, 'lxml')
  table = soup.find('table', attrs={'class': 'table-striped'}).find('tbody')
  table_body = table.find_all('tr')

  for _, rate in enumerate(table_body):
    rate = rate.text.strip().split('\n')
    c_code, country, value = rate[4], rate[3], rate[1]
    data[c_code] = float(value)
    country_code[c_code.lower()] = country


def save_csv_rates():
  # Save rates to HD so we dont keep fetching rate from the net
  with open(csv_file, "w", newline="\n") as f:
    fields = ['country', 'rate']
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    for _, country in enumerate(data):
      w.writerow({'country': country.lower(), 'rate': data[country]})


def save_csv_country_codes():
  # Save country codes
  with open(csv_codes, "w", newline="\n") as f:
    fields = ['code', 'country']
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    for _, code in enumerate(country_code):
      w.writerow({'code': code, 'country': country_code[code]})


def read_csv_rate():
  with open(csv_file, "r") as f:
    reader = csv.DictReader(f)
    for _, rate in enumerate(reader):
      data[rate['country']] = float(rate['rate'])


def read_csv_country_codes():
  with open(csv_codes, "r") as f:
    reader = csv.DictReader(f)
    for _, code in enumerate(reader):
      country_code[code['code']] = code['country']


def init():
  if not os.path.isfile(csv_file):
    print(f"Getting fresh rates...")
    get_fx_rates()
    save_csv_rates()
    save_csv_country_codes()

  todays_date = time.time()
  creation_date = os.path.getmtime(csv_file)
  last_updated_at = datetime.utcfromtimestamp(creation_date).strftime(
    '%Y-%m-%d %H:%M:%S')
  # 86400: the number of seconds in a day
  if todays_date - creation_date > 86400:
    print(f"Rates last updated: {last_updated_at}... Updating...")
    get_fx_rates()
    save_csv_rates()
  read_csv_rate()


def convert(c_code, amt):
  if not valid_c_code(c_code):
    sys.exit(f"\n\n** Invalid Country Code! **\n{usage}")
  os.system(clear)
  print(f"{amt} {c_code.upper()} to PGK")
  for _, cc in enumerate(data):
    if c_code == cc:
      print(f"Rate today: {data[cc]}")
      print("Converted: K{:.2f}".format(float(amt) / data[cc]))
      print(
        "Source: [http://www.bsp.com.pg/International/Exchange-Rates/Exchange-Rates.aspx]"
      )


def show_codes():
  if not os.path.isfile(csv_codes):
    get_fx_rates()
    save_csv_country_codes()
  read_csv_country_codes()
  print("\nCode:\tCountry:")
  print("================================")
  for i, code in enumerate(country_code):
    print(f"{code}\t{country_code[code]}")


def valid_c_code(code):
  read_csv_country_codes()
  if not country_code:
    get_fx_rates()
    save_csv_country_codes()
    read_csv_country_codes()

  if code in country_code:
    return True
  return False


usage = f'''
USAGE:
======\n
    > python {sys.argv[0]} <country code> <amount in foreign currency>

    eg:
    > python {sys.argv[0]} usd 1999.19

NOTE:
=====\n
    > To get valid country codes, just type:
    > python {sys.argv[0]} codes
'''

if __name__ == '__main__':
  length = len(sys.argv)
  if length == 2:
    if sys.argv[1] == 'codes':
      show_codes()
      exit(0)
    else:
      print("\n** Need Help **")
      print(usage)
  elif length == 3:
    country = sys.argv[1]
    pgk = sys.argv[2].replace(',', '')
    pgk = float(pgk)
    init()
    convert(country, pgk)
    exit(0)
  else:
    print(usage)

