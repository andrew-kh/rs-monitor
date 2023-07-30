import requests
from bs4 import BeautifulSoup

url = "https://www.oglasi.rs/nekretnine/prodaja-stanova/beograd"

response = requests.get(url)

soup = BeautifulSoup(response.text, "html.parser")
articles = soup.find_all("article")