from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader, Template

def make_json_template(template_path:str, template_name:str) -> Template:
    """return jinja2 Template to render ad jsons"""

    env = Environment(loader=FileSystemLoader(template_path))
    template = env.get_template(template_name)
    
    return template

def parse_breadcrumb(ad_page:BeautifulSoup) -> tuple:
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