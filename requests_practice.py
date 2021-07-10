import requests
import re
from bs4 import BeautifulSoup as bs
from usp.tree import sitemap_tree_for_homepage

domain = "www.hubilo.com"

input_urls = []
with open("test.csv") as f:
    input_urls = f.read().splitlines()


def formaturl(url):
    if not re.match('(?:http|ftp|https)://', url):
        return 'http://{}'.format(url)
    return url


# r = requests.get(formaturl(domain))
# webpage = bs(r.content)

# print(webpage.prettify())

tree = sitemap_tree_for_homepage(formaturl(input_urls[0]))
for page in tree.all_pages():
    print(page)