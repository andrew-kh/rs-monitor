import os
import time
import random
import requests
import rsm_utils as rs
from bs4 import BeautifulSoup
from multiprocessing import Pool

TEMPLATE_PATH='./meta/'
TEMPLATE_NAME='oglasi_schema_test.txt'
WEBSITE='https://www.oglasi.rs'
DATA_LOCATION='./data/landing/oglasi/sale/'

ad_template = rs.make_json_template(template_path=TEMPLATE_PATH,template_name=TEMPLATE_NAME)
page_number=1
meta_website = WEBSITE
ad_list_path = f'/nekretnine/prodaja-stanova/beograd?p={page_number}&i=96'
ad_list_url = meta_website + ad_list_path
response = requests.get(ad_list_url)
soup = BeautifulSoup(response.text, "html.parser")

num_pages=rs.get_num_of_ad_pages(soup)

parsing_dir = DATA_LOCATION+f'{str(int(time.time()))}/'

if not os.path.exists(parsing_dir):
    os.makedirs(parsing_dir)

ads = soup.find_all("article")

ad_links = []
for ad in ads:
    ad_link_object = ad.find_all('a', class_='fpogl-list-title')
    ad_link = ad_link_object[0]['href']
    ad_links.append(WEBSITE+ad_link)


with Pool(10) as p:
    result_list = p.map(rs.parse_ad_page, ad_links)
