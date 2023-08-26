import time
import argparse
import requests
import rsm_utils as rs
from bs4 import BeautifulSoup

TEMPLATE_PATH='./meta/'
TEMPLATE_NAME='oglasi_schema.txt'
WEBSITE='https://www.oglasi.rs'
AD_PATH='/nekretnine/prodaja-stanova/beograd?p=1&i=96'

parser = argparse.ArgumentParser()
parser.add_argument('--ad_number', type=int, required=True)
args = parser.parse_args()

# set up template
ad_template = rs.make_json_template(template_path=TEMPLATE_PATH,template_name=TEMPLATE_NAME)

# get single ad page
meta_website = WEBSITE
ad_list_path = AD_PATH
ad_list_url = meta_website + ad_list_path
response = requests.get(ad_list_url)
soup = BeautifulSoup(response.text, "html.parser")

ads = soup.find_all("article")

# get list of links to each ad listed on the page
ad_links = []
for ad in ads:
    ad_link_object = ad.find_all('a', class_='fpogl-list-title')
    ad_link = ad_link_object[0]['href']
    ad_links.append(ad_link)


# get html of a single ad page
ad_url = meta_website + ad_links[args.ad_number]
ad_page = BeautifulSoup(requests.get(ad_url).text, "html.parser")

# fill in info for a single ad
meta_retrieval_ts = int(time.time())

# parse breadcrumb of an ad page
breadcrumb_html = ad_page.find('ol', class_='breadcrumb')
breadcrumb_items = breadcrumb_html.find_all('li')

# get infro from breadcrumb
ad_type = breadcrumb_items[2].find('a').text.strip()

property_city = breadcrumb_items[3].find('a').text.strip()
property_district = breadcrumb_items[4].find('a').text.strip()
property_location = breadcrumb_items[5].find('a').text.strip()

print(property_location)