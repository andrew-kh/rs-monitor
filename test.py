import time
import requests
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader


# jinja setup
env = Environment(loader=FileSystemLoader('./meta/'))
template = env.get_template('oglasi_schema.json')
ad_object = template.render()

# parser block

# get single page with multiple ad highlights
meta_website = 'https://www.oglasi.rs'
ad_list_path = '/nekretnine/prodaja-stanova/beograd?i=96'
ad_list_url = meta_website + ad_list_path
response = requests.get(ad_list_url)
soup = BeautifulSoup(response.text, "html.parser")

# get list of all ad highlights on the page
ads = soup.find_all("article")

# get list of links to each ad listed on the page
ad_links = []
for ad in ads:
    ad_link_object = ad.find_all('a', class_='fpogl-list-title')
    ad_link = ad_link_object[0]['href']
    ad_links.append(ad_link)

# get html of a single ad page
ad_url = meta_website + ad_links[0]
ad_page = BeautifulSoup(requests.get(ad_url).text, "html.parser")

# fill in info for a single ad
meta_retrieval_ts = int(time.time())
meta_website = 'www.oglasi.rs'

# parse breadcrumb of an ad page
breadcrumb_html = ad_page.find('ol', class_='breadcrumb')
breadcrumb_items = breadcrumb_html.find_all('li')

# get infro from breadcrumb
ad_type = breadcrumb_items[2].find('a').text.strip()

property_city = breadcrumb_items[3].find('a').text.strip()
property_district = breadcrumb_items[4].find('a').text.strip()
property_location = breadcrumb_items[5].find('a').text.strip()