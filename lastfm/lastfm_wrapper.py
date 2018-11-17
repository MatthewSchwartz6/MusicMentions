import urllib.parse as urllib
import grequests
import spacy
from requests import Session


class lastfm_wrapper:

    def __init__(self):
        self._artists = []
        self._titles = []
        self.API_KEY = 'a3d6db89e70d991a60933bd16ebfee06'
        self.lastfm_root = "http://ws.audioscrobbler.com/2.0/"

    def get_artists(self):
        return self._artists

    def add_artist(self, artist):
        self._artists.append(artist)

    def filter_title_before_chars(self,title):
        if ':' in title:
            title= title[0:title.find(':')]
        if '\'' in title:
            title = title[0:title.find('\'')]
        if '\"' in title:
            title = title[0:title.find('\"')]
        if "-" in title:
            title = title[0:title.find('-')]
        if '\u2018' in title:
            title = title[0:title.find('\u2018')]
        if '\u2019' in title:
            title = title[0:title.find('\u2019')]
        if '\u201C' in title:
            title = title[0:title.find('\u201C')]
        if '\u201D' in title:
            title = title[0:title.find('\u201D')]
        return title

    def get_tags_from_titles(self, titles):
        print("\nGetting artists,genres,and dates from headlines.")
        num_requests_at_once = 100
        num_sessions = 20
        timeout = 2
        name = None

        search_reqs = []
        tag_reqs = []
        title_query_dict = {}
        date_query_dict = {}

        search_sessions = [Session() for i in range(num_sessions)]
        tag_sessions = [Session() for i in range(num_sessions)]

        """
        Just in case spacy fails when filtering for proper nouns.
        Found by counting popular words in headlines from 187 RSS feeds.
        """
        filter = ['New', 'new', 'with', 'Shares', 'Share', 'Song', 'Music', 'Perform', 'Stream','Remix','NSFW','Download'
            ,'Watch','a','&','to','The','Album','Video','Review','ft.','Introducing','Track','Best','Release','EP']

        """
        Map each request of artist searches( j )  to title name for quick dictionary lookup later 
        in order to double check for false positives.
        """
        j = 0
        nlp = spacy.load('en')
        for t in titles:
            title_name = t["title_name"]
            date = t["title_date"]
            title_name = self.filter_title_before_chars(title_name)
            doc = nlp(title_name)
            propns = [str(n) for n in doc
                      if n.pos_ == "PROPN"
                      and n.text not in filter]
            i = 0
            for query in propns:
                title_query_dict[j] = title_name
                date_query_dict[j] = date
                search_reqs.append(grequests.get("{0}?method=artist.search&limit=3&artist={1}&api_key={2}&format=json"
                    .format(self.lastfm_root, urllib.quote(query), self.API_KEY)
                        ,session=search_sessions[i % num_sessions],timeout=timeout))
                i += 1
                j += 1

        responses = grequests.map(search_reqs,size=num_requests_at_once)
        j = 0
        for resp in responses:
            if resp is not None and resp.status_code == 200:
                resp_dict = resp.json()
                try:
                    if int(resp_dict['results']['opensearch:totalResults']) > 0:
                        max = -1
                        for artist in resp_dict['results']['artistmatches']['artist']:
                            if int(artist['listeners']) > max:
                                max = int(artist['listeners'])
                                name = artist['name']
                    else:
                        pass
                except KeyError:
                    pass
            else:
                if resp is not None:
                    print("Status code: {}".format(resp.status_code))
            if name is not None:
                if name in title_query_dict[j]:
                    n_d_dict = {"name": name, "date": date_query_dict[j],"source_headline":title_query_dict[j]}
                    if n_d_dict not in self._artists:
                        self.add_artist(n_d_dict)
            j += 1

        print("\nNumber of search queries: {}".format(j))
        print("Number of searched headlines: {}".format(len(titles)))
        print("Number of artists found: {}".format(len(self._artists)))

        j = 0
        for entry in self.get_artists():
            artist = entry["name"]
            tag_reqs.append(grequests.get("{0}?method=artist.getTopTags&artist={1}&autocorrect=1&api_key={2}&format=json"
                .format(self.lastfm_root, urllib.quote(artist), self.API_KEY)
                    ,session=tag_sessions[j % num_sessions], callback=self.tag_callback, timeout=timeout))
            j += 1
        grequests.map(tag_reqs, size=num_requests_at_once)

    def tag_callback(self, resp, **kwargs):
        if resp is not None and resp.status_code == 200:
            r_json = resp.json()
            try:
                artist_name = r_json['toptags']['@attr']['artist']
                tags = []
                i = 0
                for tag in r_json['toptags']['tag']:
                    tags.append(tag['name'])
                    i += 1
                    if i > 5:
                        break

                for i in range(len(self._artists)):
                    if self._artists[i]["name"] == artist_name:
                        self._artists[i]["genres"] = tags
            except KeyError:
                pass


if __name__ == '__main__':
    sample = ['Missy Elliott, Mariah Carey, John Prine, More Nominated for Songwriters Hall of Fame'
        ,'Smashing Pumpkins Share New Song “Knights of Malta”: Listen','Tyler, the Creator to Live Stream Camp Flog Gnaw 2018 on YouTube'
        ,'Tekashi 6ix9ine’s Manager Charged With Gang Assault and Weapon Possession','Conor Oberst Shares 2 New Songs: Listen'
        , 'DAWN Announces New Album new breed, Shares Song: Listen','Watch Ariana Grande Perform “thank u, next” on “Ellen”'
        , 'Erykah Badu Shares New Song: Listen']
    l = lastfm_wrapper()
    l.get_tags_from_titles(sample)
    print(l.get_artists())
