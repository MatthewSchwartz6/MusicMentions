from os import path
import json
import requests
from bs4 import BeautifulSoup

base_path = path.dirname(__file__)
file_path = path.abspath(path.join(base_path, "..", "assets/rss_master.json"))

def get_rss_urls():
    rss ={}
    rss_master_url = 'https://blog.feedspot.com/music_rss_feeds/'
    resp = requests.get(rss_master_url)
    soup = BeautifulSoup(resp.content, 'html.parser')
    data = soup.findAll("div", {"class":"data"})
    for d in data:
        rss.update({d.findChild('a')['href']: d.findChild('p', attrs={'class': 'd'}).get_text()})
    with open(file_path,'w') as f:
        json.dump(rss,f)


def get_rss_master_dict():
    j = {}
    with open(file_path, 'r') as f:
        j = json.loads(f.read())
    return j


if __name__ == '__main__':
    print(get_rss_master_dict())



