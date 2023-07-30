import requests
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader

url = "https://www.oglasi.rs/nekretnine/prodaja-stanova/beograd?i=96"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")
articles = soup.find_all("article")

env = Environment(loader=FileSystemLoader('./meta/'))
template = env.get_template('oglasi_schema.json')
