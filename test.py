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
print(parsing_dir)

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


for ad_object, file_name in zip(result_list, ad_links):

    json_name=file_name.replace(WEBSITE,'')[1:].replace('/','_')+'_'+str(int(time.time()))+'.json'
    file_path=parsing_dir+json_name[:200]

    with open(file_path, "w") as json_file:
        json_file.write(ad_object)