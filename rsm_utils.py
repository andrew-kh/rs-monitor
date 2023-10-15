import re
import time
import requests
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader, Template

TEMPLATE_PATH='./meta/'
TEMPLATE_NAME='oglasi_schema_test.txt'

def make_json_template(template_path:str, template_name:str) -> Template:
    """return jinja2 Template to render ad jsons"""

    env = Environment(loader=FileSystemLoader(template_path))
    template = env.get_template(template_name)
    
    return template

ad_template=make_json_template(template_path=TEMPLATE_PATH,template_name=TEMPLATE_NAME)

def parse_breadcrumb(ad_page:BeautifulSoup) -> tuple[str,str,str,str]:
    """return ad type (sale/rent) and location from
    ad page's breadcrumb
    """
    # parse breadcrumb of an ad page
    breadcrumb_html = ad_page.find('ol', class_='breadcrumb')
    breadcrumb_items = breadcrumb_html.find_all('li')
    # get infro from breadcrumb
    ad_type = breadcrumb_items[2].find('a').text.strip()
    property_city = breadcrumb_items[3].find('a').text.strip()
    property_district = breadcrumb_items[4].find('a').text.strip()
    property_location = breadcrumb_items[5].find('a').text.strip()
    return ad_type, property_city, property_district, property_location


def parse_ad_update_dt(ad_page:BeautifulSoup) -> str:
    """return ad update date and time"""

    ad_update_div = ad_page.find_all('div', class_='visible-sm visible-md visible-lg')
    
    if len(ad_update_div) == 1:
        ad_update_dt=ad_update_div[0].find('time').text.strip()
    else:
        ad_update_dt=''

    return ad_update_dt


def parse_ad_caption(ad_page:BeautifulSoup) -> str:
    """return ad caption"""
    ad_caption_html = ad_page.find_all(name='h1',
                                    class_='fpogl-title text-primary',
                                    itemprop='name')

    if len(ad_caption_html) == 1:
        ad_caption = ad_caption_html[0].text.strip()
    else:
        ad_caption=''
    
    return replace_symbols(ad_caption)


def parse_ad_text(ad_page:BeautifulSoup) -> str:
    """return ad text stored in 'More Info' section"""

    ad_text_obj=ad_page.find_all(name='div',
                                class_='col-sm-6')

    ad_text_list=[]

    if ad_text_obj:
        for div in ad_text_obj:
            ad_text_list.append(div.find_all(name='p'))

        if ad_text_list[1]==[]:
            ad_text = ''.join([i.text.strip().replace('\n','') for i in ad_text_list[0]])

    else:
        ad_text=''

    return replace_symbols(ad_text)


def parse_ad_description_text(ad_page:BeautifulSoup) -> str:
    """return ad text stored in 'Ad Text' section"""

    ad_descr_text_block=ad_page.find_all(name='div',itemprop='description')
    
    if ad_descr_text_block:
        ad_descr_text=ad_descr_text_block[0].text.strip().replace('\n','')
    else:
        ad_descr_text=''
    
    return replace_symbols(ad_descr_text)


def parse_price(ad_page:BeautifulSoup) -> tuple[str,str]:
    """return property price and currency"""

    ad_price_html=ad_page.find_all(
        name='h3',
        itemprop='offers')

    if len(ad_price_html)==1:
        property_price=ad_price_html[0].find(name='span',
                                            itemprop='price').text
        property_currency=ad_price_html[0].find(name='span',
                                                itemprop='priceCurrency').text
    else:
        property_price=''
        property_currency=''

    return property_price, property_currency


def parse_property_info(ad_page:BeautifulSoup) -> dict:
    """return property info section"""

    div_with_table = ad_page.find_all(name='div',
                                    class_='col-sm-6')
    ad_info_table=div_with_table[0]. \
                    find(name='table'). \
                    find_all(name='tr')
    ad_info_list=[(i.find_all(name='td')[0].text.strip().strip(":"),
                i.find_all(name='td')[1].text.strip()) for i in ad_info_table]
    property_info={k:v for (k,v) in ad_info_list}
    
    return property_info


def parse_num_of_images(ad_page:BeautifulSoup) -> int:
    """return number of images on the ad page"""

    try:
        ad_num_of_images=len(ad_page.find_all(name='figure')[0].find_all(name='img'))
    except IndexError:
        ad_num_of_images=0        

    return ad_num_of_images


def parse_num_of_views(ad_page:BeautifulSoup) -> str:
    """return number of views from ad page"""

    ad_num_of_views_raw = ad_page.find(name='div',
                                    string=re.compile('Broj pregleda')).text.strip()
    ad_num_of_views=ad_num_of_views_raw.replace('Broj pregleda: ','')
    
    return ad_num_of_views


def parse_advertiser_info(ad_page:BeautifulSoup) -> dict:
    """return advertiser info section"""

    adv_info_blocks_names=['Šifra oglasa', 'Agencijska šifra']
    adv_info_block_lbls=['ad_code_number', 'ad_advertiser_code']
    adv_info_blocks_values=[]

    for block in adv_info_blocks_names:
        val_block = ad_page.find_all(name='div',
                        string=re.compile(block))

        val_block=[i for i in val_block if i.get('itemprop')!='description'][0]
        if val_block:
            val=val_block.text.strip().split(': ')[1]
        else:
            val=''
        adv_info_blocks_values.append(val)

    ad_advertiser_info={k:v for k,v in zip(adv_info_block_lbls, adv_info_blocks_values)}

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
    try:
        contact_block=panel_divs[1].find_all(
            name='a',
            href=re.compile("tel:")
        )
        if contact_block:
            advertiser_contact=contact_block[0].text.strip()
        else:
            advertiser_contact=''
    except IndexError:
        advertiser_contact=''   


    # advertiser num of ads
    num_of_ads_block=panel_body.find_all(
        name='div',
        style='display:inline-block'
    )

    if num_of_ads_block[-1]:
        pattern = re.compile(r"\((\d+)\)")
        num_of_ads=num_of_ads_block[-1].find_all(name='a')[0].text
        if pattern.findall(num_of_ads):
            num_of_ads=pattern.findall(num_of_ads)[0]
        else:
            num_of_ads=''
        advertiser_ads_url=num_of_ads_block[-1].find_all(name='a')[0]['href']

    ad_advertiser_info['advertiser_contact']=replace_symbols(advertiser_contact)
    ad_advertiser_info['advertiser_num_of_ads']=replace_symbols(num_of_ads)
    ad_advertiser_info['advertiser_ads_url']=replace_symbols(advertiser_ads_url)
    ad_advertiser_info['advertiser_name']=replace_symbols(advertiser_name)

    return ad_advertiser_info


def get_num_of_ad_pages(main_page:BeautifulSoup) -> int:
    """return total number of pages with ads from the main page"""

    num_pages_block=main_page.find_all(name='div',class_='form-group visible-sm-inline-block')
    if num_pages_block:
        num_pages=num_pages_block[0].text.strip().split('/')[1]
        num_pages = int(re.findall(r'\d+', num_pages)[0])
        
    return num_pages


def parse_ad_page(ad_url:str,ad_template:Template=ad_template) -> str:
    """returns an json object with data from an ad_url"""

    meta_website=re.search("https.*?(?:[^@\/\n]+@)?([^:\/\n]+)", ad_url)[0]

    ad_page = BeautifulSoup(requests.get(ad_url).text, "html.parser")

    # fill in info for a single ad
    meta_retrieval_ts = int(time.time())

    try:

        # # get infro from breadcrumb
        ad_type,property_city,property_district,property_location=parse_breadcrumb(ad_page)

        # get ad update dt
        ad_update_dt = parse_ad_update_dt(ad_page)

        # get ad caption
        ad_caption = parse_ad_caption(ad_page)

        # get ad text
        ad_text=parse_ad_text(ad_page)

        ad_descr_text=parse_ad_description_text(ad_page)

        # get ad price
        property_price, property_currency = parse_price(ad_page)

        # parse table with info
        property_info=parse_property_info(ad_page)

        # get number of images in an ad
        ad_num_of_images = parse_num_of_images(ad_page)

        # ad_num_of_views 
        ad_num_of_views=parse_num_of_views(ad_page)

        ad_advertiser_info=parse_advertiser_info(ad_page)

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

        return ad_object
    
    except:

        print(f'error while processing the link {ad_url}')


def replace_symbols(text:str) -> str:
    """replaces a set of sybmols for json format"""

    symbols_dict={
        '"':'',
        "'":"",
        "\n": " ",
        "\r": " ",
        "\t": " ",
        "\\": ""
    }

    translation_table = str.maketrans(symbols_dict)

    clean_text = text.translate(translation_table)

    return clean_text