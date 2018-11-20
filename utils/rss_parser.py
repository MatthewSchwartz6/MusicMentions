#coding=utf8
from time import strftime
import feedparser
import grequests
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from utils.rss_utils import get_rss_master_dict, get_rss_urls


class rss_parser:

    def __init__(self):
        self.titles = []
        self.time_format = "%d-%m-%Y %H:%M:%S"

    def get_titles(self):
        return self.titles

    def parse(self, limit):
        print("\nGetting headlines from {} RSS feeds.".format(limit))
        try:
            j = get_rss_master_dict()
        except FileNotFoundError:
            get_rss_urls()
            j = get_rss_master_dict()
        urls = list(j.keys())
        urls = urls[0:limit]
        retries = Retry(total=5,backoff_factor=0.2,status_forcelist=[500,502,503,504], raise_on_redirect=True, raise_on_status=True)
        sessions = [Session() for i in range(limit)]
        for s in sessions:
            s.mount('http://', HTTPAdapter(max_retries=retries))
            s.mount('https://', HTTPAdapter(max_retries=retries))

        i = 0
        timeout = 2
        reqs = []
        for url in urls:
            reqs.append(grequests.get(url, callback=self.callback,timeout=timeout,session=sessions[i % limit]))
            i += 1

        grequests.map(reqs, size=limit*2)

    def callback(self, resp, **kwargs):
        if resp.status_code == 200 and resp is not None:
            feed = feedparser.parse(resp.content)
            # try:
            #     print(feed['feed']['title'])
            # except KeyError:
            #     print('title key error')
            for entry in feed['entries']:
                try:
                    title_date = strftime(self.time_format, entry['updated_parsed'])
                    self.titles.append({"title_name":entry['title'], "title_date": title_date})
                except AttributeError:
                    pass
                except KeyError:
                    pass


if __name__ == '__main__':
    rss = rss_parser()
    rss.parse(187)
    print(rss.get_titles())
