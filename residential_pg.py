# -*- coding: utf-8 -*-
"""Residential PG

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1S6hxSVsjtgj_id3auda5ejbQxrIphCLc
"""

pip install nums_from_string

import requests
from datetime import date
import nums_from_string
import csv
import json
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup

data = []
cities=['Mumbai', 'Gurgaon','Noida','Ghaziabad','Greater-Noida','Bangalore','Pune','Hyderabad','Kolkata','Chennai',
        'New-Delhi','Ahmedabad','Navi-Mumbai','Thane','Faridabad','Bhubaneswar','Bokaro-Steel-City','Vijayawada','Vrindavan', 'Bhopal',
        'Gorakhpur','Jamshedpur','Agra','Allahabad','Jodhpur''Aurangabad','Jaipur','Mangalore','Nagpur','Guntur','Navsari','Palghar','Salem','Haridwar','Durgapur',
        'Madurai','Manipal','Patna','Ranchi','Raipur','Sonipat','Kottayam','Kozhikode','Thrissur','Tirupati','Trivandrum','Trichy','Udaipur','Vapi','Varanasi',
        'Vadodara','Visakhapatnam','Surat','Kanpur','Kochi','Mysore','Goa','Bhiwadi','Lucknow','Nashik','Guwahati','Chandigarh','Indore','Coimbatore','Dehradun']

# today = datetime.datetime.today().strftime ('%Y-%m-%d')
# def get_date_posted(ago_count):
#   Previous_Date = datetime.datetime.today() - datetime.timedelta(days=ago_count)
#   previous_d_for = Previous_Date.strftime ('%d/%m/%Y')
#   return previous_d_for

def scrape(city):
  for i in range(1,2):
    
    url = "https://www.magicbricks.com/property-for-rent/residential-paying-guest?cityName=" + city;
    response = requests.get(url)
    response = response.content
    soup = BeautifulSoup(response, 'html.parser')
    cards = soup.find_all('div', class_='m-srp-card')

    posted_by = None
    sharing_type = []
    pg_for = None
    charges = None
    pg_name = None
    link = None
    locality = None
    desc = None
    date_posted = None
    today = date.today()

    for card in cards:

      # No section for date posted for PGs

      # try:
      #   posted_date = card.find(class_="mb-srp__card__photo__fig--post").text
      #   if 'today' in posted_date or 'Today' in posted_date:
      #     date_posted = get_date_posted(0)
      #   elif 'ago' in posted_date:
      #     ago_date_count = int(nums_from_string.get_nums(posted_date)[0])
      #     if 'days' in posted_date:
      #         date_posted = get_date_posted(ago_date_count)
      #     elif 'weeks' in posted_date:
      #         date_posted = get_date_posted((ago_date_count*7))
      #     else:
      #         date_posted = get_date_posted((ago_date_count*30))
      #   elif 'yesterday' in posted_date or 'Yesterday' in posted_date:
      #       date_posted = get_date_posted(1)
      #   else:
      #       date_posted = posted_date.replace('Posted: ','')
      # except:
      #     posted_date = None

      pg_for = card.find('span', class_='m-srp-card__info__gender').text

      try:
        link = card.find(attrs={'itemprop': 'url'})
        link = 'https://www.magicbricks.com/' + link.get('content')
      except:
        link = None

      res = requests.get(link)
      res = res.content
      res_soup = BeautifulSoup(res, 'html.parser')

      dep_amt = res_soup.find('div', class_='pg-prop-details__info__grid--value').text.replace('₹', '')

      try: 
        pg_name = card.find('meta', attrs={'itemprop': 'name'})
        pg_name = pg_name.get('content')
      except:
        pg_name = None
      try: 
        desc = card.find('meta', attrs={'itemprop': 'description'})
        desc = desc.get('content')
      except:
        desc = None

      charges = card.find('div', class_='m-srp-card__price').text.replace('₹', '')
      charges = charges.replace('\\n', '')
      charges = charges[0:8] + 'Onwards'

      try: 
        temp = card.find('span', attrs={'class': 'hidden'})
        posted_by = temp.get('data-advname')
        sharing_type = temp.get('data-avail').replace('\\', '')
        locality = temp.get('data-pglocality')
      except:
        pass

      try:
          data.append([link, pg_name, posted_by, city, locality, pg_for, charges, dep_amt, sharing_type, desc])
      except:
        pass
  df = pd.DataFrame(data, columns=['Link', 'PG Name', 'Posted By', 'City', 'Locality', 'For', 'Charges', 'Deposit Amount', 'Sharing', 'Description'])
  df.to_csv('Data_{0}_PG.csv'.format(str(city)), index=False)
  df.drop_duplicates(subset='Link', keep='first', inplace=True)
  df.insert(loc=0, column='No', value=np.arange(len(df)))
  try:
    df.drop(index=df.index[0], axis=0, inplace=True)
  except:
    df = df.fillna(0)
  df.to_csv('{0}_{1}_PG.csv'.format(str(city), today), index=False)

  # Function to convert a CSV to JSON
  def make_json(csvFilePath, jsonFilePath):
    
    data = {}
    
    with open(csvFilePath, encoding='utf-8') as csvf:
      csvReader = csv.DictReader(csvf)

      for rows in csvReader:

        key = rows['No']
        data[key] = rows

    with open(jsonFilePath, 'w', encoding='utf-8') as jsonf:
      jsonf.write(json.dumps(data, indent=4))

  csvFilePath = r'{0}_{1}_PG.csv'.format(str(city), today)
  jsonFilePath = r'{0}_{1}_PG.json'.format(str(city), today)

  make_json(csvFilePath, jsonFilePath)

for city in cities:
  scrape(city)