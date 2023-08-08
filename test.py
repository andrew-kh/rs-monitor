import json
import time
import requests
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader


# jinja setup
env = Environment(loader=FileSystemLoader('./meta/'))
def to_json_filter(value):
    return json.dumps(value)
env.filters['to_json'] = to_json_filter
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

# get ad update dt
ad_update_div = ad_page.find_all('div', class_='visible-sm visible-md visible-lg')
if len(ad_update_div) == 1:
    ad_update_dt = ad_update_div[0].find('time').text.strip()

# get ad caption
ad_caption_html = ad_page.find_all(name='h1',
                                   class_='fpogl-title text-primary',
                                   itemprop='name')
if len(ad_caption_html) == 1:
    ad_caption = ad_caption_html[0].text.strip()

# get ad text
ad_text_obj=ad_page.find_all(name='div',
                                   class_='col-sm-6')

ad_text_list=[]
for div in ad_text_obj:
    ad_text_list.append(div.find_all(name='p'))

if ad_text_list[1]==[]:
    ad_text = ''.join([i.text for i in ad_text_list[0]])

# get ad price
ad_price_html=ad_page.find_all(name='h3',
                 itemprop='offers')

if len(ad_price_html)==1:
    property_price=ad_price_html[0].find(name='span',
                                         itemprop='price').text
    property_currency=ad_price_html[0].find(name='span',
                                            itemprop='priceCurrency').text


# parse table with info
div_with_table = ad_page.find_all(name='div',
                                  class_='col-sm-6')
ad_info_table=div_with_table[0]. \
                find(name='table'). \
                find_all(name='tr')
ad_info_list=[(i.find_all(name='td')[0].text.strip(),
               i.find_all(name='td')[1].text.strip()) for i in ad_info_table]
property_info={k:v for (k,v) in ad_info_list}
