import urllib.request
import json
#import requests

TOKEN = "69a58187ab3f5fc0d0d32c4b9de13e35b4633023"
ROOT_URL = "https://api-ssl.bitly.com"
SHORTEN = "/v3/shorten?access_token={}&longUrl={}"
headers = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/json',
}


class BitlyHelper:

    def shorten_url(self, longurl):
        try:
            url = ROOT_URL + SHORTEN.format(TOKEN, longurl)
            response = urllib.request.urlopen(url).read()
            #data = '{ "long_url": longurl, "domain": "bit.ly", "group_guid": "Ba1bc23dE4F" }'
            #response = requests.post('https://api-ssl.bitly.com/v4/shorten', headers=headers, data=data)
            jr = json.loads(response)
            return jr['data']['url']
        except Exception as e:
            print (e)



