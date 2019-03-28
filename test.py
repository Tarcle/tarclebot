#https://public-api.tracker.gg/apex/v1/standard/profile/5/Tarcle

import discord
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import json

search = "Tarcle"
req = urllib.request.Request("https://public-api.tracker.gg/apex/v1/standard/profile/5/"+search, headers={'User-Agent': 'Mozilla/5.0', 'TRN-Api-Key': '1e913677-7f9e-491d-b16b-fb097d0456ac'})
html = urllib.request.urlopen(req).read().decode('utf-8')
# soup = BeautifulSoup(html, 'html.parser')

data = json.loads(html)
print(data)