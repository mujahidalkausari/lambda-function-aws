import re
import json
from urllib.request import Request, urlopen
#import requests
from bs4 import BeautifulSoup
import hashlib

def lambda_handler(event, context):

    rel_url = event.get("url")
    #rel_url = 'attorneys/84025-ut-jason-hunter-284784.html#client_reviews'

    url = 'https://www.avvo.com/' + "" + rel_url

    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'
    }
      
    #response = requests.get(url)
    #soup = BeautifulSoup(response.text, 'html.parser')

    with urlopen(Request(url, headers=headers)) as response:
        soup = BeautifulSoup(response.read(), features="html.parser")

        data = {}

        data["website"] = soup.title.text
        data["biz_logo_link"]  = response.url
        data["post_site_url"] = re.search('https?://([A-Za-z_0-9.-]+).*', response.url).group(1)
        data["post_review_link"]= response.url
        data["biz_favicon"] = re.search('https?://([A-Za-z_0-9.-]+).*', response.url).group(1) +""+(soup.find('link', {'rel': 'icon'})).get('href')
        data["total_reviews"]= soup.find('span', {'itemprop': 'reviewCount'}).get_text()
        data["overall_rating"]= soup.find('span', {'itemprop': 'ratingValue'}).get("content")

        reviews = []
        for tag in soup.findAll('div',{'class':'u-vertical-margin-1'}):
            try:
                title = tag.find('h3', {'itemprop': 'headline'}).get_text()
            except:
                title = ''
            try:
                date = tag.find("span",{"itemprop":"datePublished"}).string
            except:
                date = ''
            try:
                rating = tag.find('meta', {'itemprop': 'ratingValue'}).get('content')
            except:
                rating = ''
            try:
                desciption = tag.find('div', {'class': 'sidebar-box'}).get_text()
            except:
                desciption = ''
            try:
                name = tag.find("span",{"itemprop":"author"}).string
            except:
                name = ''

            item = {}

            item['name'] = name
            item['date'] = date
            item['avatar'] = ''
            item['rating'] = rating
            item['title'] = title
            item['description'] = desciption
            item['source'] = ''

            strId = f'{name}{date}'
            hash_object = hashlib.md5(strId.encode()) #assumes the default UTF-8
            item['reviewId'] = hash_object.hexdigest()

            reviews.append(item)   

        data["reviews"] = reviews
        #print(json.dumps(data, sort_keys=True, indent=2))
    
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps(data)
        }

#if __name__ == "__main__":
    #res = lambda_handler('', '')
    #print(res)
