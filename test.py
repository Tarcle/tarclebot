#https://public-api.tracker.gg/apex/v1/standard/profile/5/Tarcle
#1e913677-7f9e-491d-b16b-fb097d0456ac

#Tvtf3hsW0468tDq8n1b6D3RQrNTvjnMbDgAF1Wso
from bs4 import BeautifulSoup as BS
import ssl, urllib.request
import traceback

base_url = 'https://www.google.co.kr/search'
#: 검색조건 설정
values = {
    'q': 'light.gg 용', # 검색할 내용
    'oq': 'light.gg 용',
    'aqs': 'chrome..69i57.35694j0j7',
    'sourceid': 'chrome',
    'ie': 'UTF-8',
}

# Google에서는 Header 설정 필요
hdr = {'User-Agent': 'Mozilla/5.0'}

query_string = urllib.parse.urlencode(values)
req = urllib.request.Request(base_url + '?' + query_string, headers=hdr)
context = ssl._create_unverified_context()
try: 
    res = urllib.request.urlopen(req, context=context)
except:
    traceback.print_exc()

html_data = BS(res.read(), 'html.parser')

print(html_data)