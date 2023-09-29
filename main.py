import os
# import re
import time
import random
# import argparse
import requests
import rsm_utils as rs
from bs4 import BeautifulSoup

TEMPLATE_PATH='./meta/'
TEMPLATE_NAME='oglasi_schema_test.txt'
WEBSITE='https://www.oglasi.rs'
DATA_LOCATION='./data/landing/oglasi/sale/'

# parser = argparse.ArgumentParser()
# parser.add_argument('--ad_from', type=int, required=True)
# parser.add_argument('--ad_to', type=int, required=True)
# args = parser.parse_args()

# set up template
ad_template = rs.make_json_template(template_path=TEMPLATE_PATH,template_name=TEMPLATE_NAME)
page_number=1
# get single ad page
meta_website = WEBSITE
ad_list_path = f'/nekretnine/prodaja-stanova/beograd?p={page_number}&i=96'
ad_list_url = meta_website + ad_list_path
response = requests.get(ad_list_url)
soup = BeautifulSoup(response.text, "html.parser")

num_pages=rs.get_num_of_ad_pages(soup)

parsing_dir = DATA_LOCATION+f'{str(int(time.time()))}/'

if not os.path.exists(parsing_dir):
    os.makedirs(parsing_dir)
    
with open('./data/logs/rs-monitor-logs.txt', 'a') as file:

    for page_number in range(1,num_pages+1):

        ads = soup.find_all("article")

        # print(f'----PARSING PAGE #{page_number} of {num_pages}------')


        # get list of links to each ad listed on the page
        ad_links = []
        for ad in ads:
            ad_link_object = ad.find_all('a', class_='fpogl-list-title')
            ad_link = ad_link_object[0]['href']
            ad_links.append(ad_link)

        
        for ad_number in range(len(ad_links)):

            # get html of a single ad page
            ad_url = meta_website + ad_links[ad_number]

            ad_object = rs.parse_ad_page(ad_url)

            json_name=ad_links[ad_number][1:].replace('/','_')+'_'+str(int(time.time()))+'.json'

            file_path=parsing_dir+json_name[:200]

            with open(file_path, "w") as json_file:
                json_file.write(ad_object)

            file.write(f'saved file {file_path}')

            time.sleep(random.uniform(0.5, 1.2))

        ad_list_path = f'/nekretnine/prodaja-stanova/beograd?p={page_number}&i=96'
        ad_list_url = meta_website + ad_list_path
        response = requests.get(ad_list_url)
        soup = BeautifulSoup(response.text, "html.parser")