from lxml import html
import requests
import string
import json

url = 'http://genius.com'
alpha = list(string.ascii_lowercase)

links = []

for letter in alpha:
    i = 1
    while True:
        full_url = url+'/artists-index/'+letter+'/all' + ('?page='+str(i) if i > 1 else '')
        page = requests.get(full_url)
        tree = html.fromstring(page.content)
        results = tree.xpath('//*[@class="artists_index_list"]//a/@href')
        if results:
            links.append(results)
        else:
            break
        print full_url
        i += 1

with open('data.json', 'w') as fp:
    json.dump({'artists': links}, fp)

'''
artists = tree.xpath('')
while setA '''

'''id, url, artists, producer, title, lyrics, annotations, youtube link'''
