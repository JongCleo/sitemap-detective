import sys
import csv
import requests
from bs4 import BeautifulSoup as bs
import uuid

########################################################
# Get Scraper input and prep everything into memory
path_to_csv = input('What is your file called?\n').strip()
path_to_csv = path_to_csv + ".csv" if ".csv" not in path_to_csv else path_to_csv

term_list = [
    x.strip()
    for x in input('Enter comma separated terms to look for:\n').split(",")
]
page_list = [
    x.strip() for x in input(
        'Enter comma separated page names to look for:\n').split(",")
]

with open(path_to_csv) as f:
    input_urls = f.readlines()

########################################################
# Prep output CSV

output_name = "output_csv_" + str(uuid.uuid1()) + ".csv"
header = ['sites'] + term_list + page_list

with open('output/' + output_name, 'w') as f:
    writer = csv.writer(f)
    writer.writerow(header)

########################################################
# browser context amanger
