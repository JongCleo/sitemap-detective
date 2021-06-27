import sys

########################################################
# Get Scraper input and prep everything into memory
path_to_csv = input('What is your file called?\n').strip()
path_to_csv = path_to_csv + ".csv" if ".csv" not in path_to_csv else path_to_csv

term_list = [x.strip() for x in input(
    'Enter comma separated terms to look for:\n').split(",")]
page_list = [x.strip() for x in input(
    'Enter comma separated page names to look for:\n').split(",")]


with open(path_to_csv) as f:
    input_urls = f.readlines()

print(input_urls)

########################################################
# Prep output file

########################################################
# Process


# browser context amanger
