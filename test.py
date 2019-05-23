# https://public-api.tracker.gg/v2/apex/standard/search
# ab63b204-0d80-42b9-8d4d-7ef89ee5bf56

#Tvtf3hsW0468tDq8n1b6D3RQrNTvjnMbDgAF1Wso
from bs4 import BeautifulSoup as BS
import urllib.request, json

base_url = 'https://public-api.tracker.gg/v2/apex/standard/profile/origin/Tarcle/sessions'
#: 검색조건 설정
values = {
    
}

# Google에서는 Header 설정 필요
hdr = {
    'User-Agent': 'Mozilla/5.0',
    'TRN-Api-Key': 'ab63b204-0d80-42b9-8d4d-7ef89ee5bf56'
}

query_string = urllib.parse.urlencode(values)
req = urllib.request.Request(base_url + '?' + query_string, headers=hdr)
res = urllib.request.urlopen(req)

html_data = json.loads(res.read())

print(html_data)