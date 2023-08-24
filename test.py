import re
import json
import time
import requests
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader


# jinja setup
env = Environment(loader=FileSystemLoader('./meta/'))
template = env.get_template('oglasi_schema.txt')
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

ad_descr_text=ad_page.find_all(
    name='div',
    itemprop='description')[0].text.strip()

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
ad_info_list=[(i.find_all(name='td')[0].text.strip().strip(":"),
               i.find_all(name='td')[1].text.strip()) for i in ad_info_table]
property_info={k:v for (k,v) in ad_info_list}

# get number of views
num_of_view_block = ad_page.find(name='div',
                               string=re.compile('Broj pregleda')).text.strip()


# get number of images in an ad
ad_num_of_images = len(ad_page.find_all(name='figure')[0].find_all(name='img'))

# get advertiser info pt 1
div_with_adv_info_table = ad_page.find_all(
    name='div',
    class_='default-widget')

adv_info_blocks_names=['Šifra oglasa', 'Agencijska šifra']
adv_info_blocks_values=[]

for block in adv_info_blocks_names:
    val = ad_page.find(name='div',
                       string=re.compile(block)).text.strip()
    adv_info_blocks_values.append(val)

ad_advertiser_info={k:v for (k,v) in [tuple(i.split(': ')) for i in adv_info_blocks_values]}

# ad_num_of_views 
ad_num_of_views_raw = ad_page.find(name='div',
                                   string=re.compile('Broj pregleda')).text.strip()
ad_num_of_views=ad_num_of_views_raw.replace('Broj pregleda: ','')

# get advertiser info pt 2
div_panel_body=ad_page.find_all(
    name='div',
    class_='panel-body')

if len(div_panel_body)==1:
    panel_body=div_panel_body[0]

panel_divs=panel_body.find_all(
    name='div',
    style='margin-bottom:12px'
)

# advertiser name
advertiser_name_div = panel_divs[0].find_all(
    name='div',
    style='display:inline-block'
)

if advertiser_name_div:
    advertiser_name=advertiser_name_div[0].text.strip()

# advertiser contact
contact_block=panel_divs[1].find_all(
    name='a',
    href=re.compile("tel:")
)

if contact_block:
    advertiser_contact=contact_block[0].text.strip()

# advertiser num of ads
num_of_ads_block=panel_body.find_all(
    name='div',
    style='display:inline-block'
)

if num_of_ads_block[-1]:
    pattern = re.compile(r"\((\d+)\)")
    num_of_ads=num_of_ads_block[-1].find_all(name='a')[0].text
    num_of_ads=pattern.findall(num_of_ads)[0]
    advertiser_ads_url=num_of_ads_block[-1].find_all(name='a')[0]['href']

ad_advertiser_info['advertiser_contact']=advertiser_contact
ad_advertiser_info['advertiser_num_of_ads']=num_of_ads
ad_advertiser_info['advertiser_ads_url']=advertiser_ads_url

ad_object = template.render(
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
    ad_num_of_views=ad_num_of_views
)