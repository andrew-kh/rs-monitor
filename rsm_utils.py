from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader, Template

def make_json_template(template_path:str, template_name:str) -> Template:
    """return jinja2 Template to render ad jsons"""

    env = Environment(loader=FileSystemLoader(template_path))
    template = env.get_template(template_name)
    
    return template


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
    
    return ad_caption


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

    return ad_text


def parse_ad_description_text(ad_page:BeautifulSoup) -> str:
    """return ad text stored in 'Ad Text' section"""

    ad_descr_text_block=ad_page.find_all(name='div',itemprop='description')
    
    if ad_descr_text_block:
        ad_descr_text=ad_descr_text_block[0].text.strip().replace('\n','')
    else:
        ad_descr_text=''
    
    return ad_descr_text