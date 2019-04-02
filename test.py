#https://public-api.tracker.gg/apex/v1/standard/profile/5/Tarcle
#1e913677-7f9e-491d-b16b-fb097d0456ac

import discord
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import json
url = "http://"+urllib.parse.quote("www.mhwdb.kr/apis/weapons/쌍검")
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8')
monsters = json.loads(html)
print(monsters)