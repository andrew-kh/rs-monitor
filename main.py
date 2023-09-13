import os
import re
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

# ad_from = args.ad_from
# ad_to = args.ad_to

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
    
for page_number in range(1,num_pages+1):

    ads = soup.find_all("article")

    print(f'----PARSING PAGE #{page_number} of {num_pages}------')


    # get list of links to each ad listed on the page
    ad_links = []
    for ad in ads:
        ad_link_object = ad.find_all('a', class_='fpogl-list-title')
        ad_link = ad_link_object[0]['href']
        ad_links.append(ad_link)

    
    for ad_number in range(len(ad_links)):

        # get html of a single ad page
        ad_url = meta_website + ad_links[ad_number]
        ad_page = BeautifulSoup(requests.get(ad_url).text, "html.parser")

        # print(f'\nattempting to parse:\n{ad_url}\n')

        # fill in info for a single ad
        meta_retrieval_ts = int(time.time())

        # # get infro from breadcrumb
        ad_type,property_city,property_district,property_location=rs.parse_breadcrumb(ad_page)

        # get ad update dt
        ad_update_dt = rs.parse_ad_update_dt(ad_page)

        # get ad caption
        ad_caption = rs.parse_ad_caption(ad_page)

        # get ad text
        ad_text=rs.parse_ad_text(ad_page)

        ad_descr_text=rs.parse_ad_description_text(ad_page)

        # get ad price
        property_price, property_currency = rs.parse_price(ad_page)

        # parse table with info
        property_info=rs.parse_property_info(ad_page)

        # get number of images in an ad
        ad_num_of_images = rs.parse_num_of_images(ad_page)

        # ad_num_of_views 
        ad_num_of_views=rs.parse_num_of_views(ad_page)

        ad_advertiser_info=rs.parse_advertiser_info(ad_page)

        ad_object = ad_template.render(
            meta_retrieval_ts=meta_retrieval_ts,
            meta_website=meta_website,
            ad_url=ad_url,
            ad_type=ad_type,
            property_city=property_city,
            property_district=property_district,
            property_location=property_location,
            ad_update_dt=ad_update_dt,
            ad_caption=ad_caption,
            ad_text=ad_text,
            ad_descr_text=ad_descr_text,
            property_price=property_price,
            property_currency=property_currency,
            ad_advertiser_info=ad_advertiser_info,
            property_info=property_info,
            ad_num_of_views=ad_num_of_views,
            ad_num_of_images=ad_num_of_images
        )

        json_name=ad_links[ad_number][1:].replace('/','_')+'_'+str(meta_retrieval_ts)+'.json'

        file_path=parsing_dir+json_name[:200]

        with open(file_path, "w") as json_file:
            json_file.write(ad_object)

        # print(f'saved file {file_path}')

        time.sleep(random.uniform(0.5, 2.3))

    ad_list_path = f'/nekretnine/prodaja-stanova/beograd?p={page_number}&i=96'
    ad_list_url = meta_website + ad_list_path
    response = requests.get(ad_list_url)
    soup = BeautifulSoup(response.text, "html.parser")