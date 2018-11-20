from sys import getsizeof
from time import time
from json import loads,dumps
from utils.rss_parser import rss_parser
from lastfm.lastfm_wrapper import lastfm_wrapper
from utils.wiki_subgenre_scraper import wiki_subgenre_scraper


MAX_LIMIT = 187
LIMIT = 187


def build_json_schema():
    try:
        with open('assets/genres.json','r') as f:
            genre_j = f.read()
    except FileNotFoundError:
            wiki_subgenre_scraper()
            with open('assets/genres.json','r') as f:
                genre_j = f.read()
    genre_super_dict = loads(genre_j)

    # build json schema
    music_mentions = {"music_mentions":[]}
    for genre in list(genre_super_dict.keys()):
        g_schema = {"genre":{"name":"","total":0,"date_mentioned":[],"artists_mentioned":[],"subgenres":[]}}
        g_schema["genre"]["name"] = genre
        for sub_g in genre_super_dict[genre]:
            s_g_schema = {"name":"","total":0,"date_mentioned":[]}
            s_g_schema["name"] = sub_g
            g_schema["genre"]["subgenres"].append(s_g_schema)
        music_mentions["music_mentions"].append(g_schema)
    return music_mentions


def add_entries_to_json(artist_mentioned, music_mentions):
    # add entries to json schema
    for artist in artist_mentioned:
        try:
            name = artist['name']
            date = artist['date']
            genres = artist['genres']
            for genre in genres:
                for i in range(len(music_mentions["music_mentions"])):
                    mm_g = music_mentions['music_mentions'][i]
                    if mm_g["genre"]["name"].lower() == genre.lower():
                        mm_g['genre']['total'] += 1
                        mm_g['genre']['date_mentioned'].append(date)
                        mm_g['genre']['artists_mentioned'].append({"artist_name": name, "date_mentioned": date})
                        break
                    else:
                        for g in mm_g["genre"]["subgenres"]:
                            if g['name'].lower() == genre.lower():
                                g["total"] += 1
                                g["date_mentioned"].append(date)
                                mm_g['genre']['total'] += 1
                                if date not in mm_g['genre']['date_mentioned']:
                                    mm_g['genre']['date_mentioned'].append(date)
                                am = {"artist_name": name, "date_mentioned": date}
                                if am not in mm_g['genre']['artists_mentioned']:
                                    mm_g['genre']['artists_mentioned'].append(am)
                                break
        except KeyError:
            pass
    return music_mentions


def remove_empty(music_mentions):
    # remove empty k,v pairs and array elements
    for genre in music_mentions["music_mentions"]:
        if genre["genre"]["total"] == 0:
            del genre["genre"]
        else:
            for subgenre in genre["genre"]["subgenres"]:
                if subgenre["total"] == 0:
                    del subgenre["name"]
                    del subgenre["total"]
                    del subgenre["date_mentioned"]
            genre["genre"]["subgenres"] = [i for i in genre["genre"]["subgenres"] if len(i) != 0]
    music_mentions["music_mentions"] = [i for i in music_mentions["music_mentions"] if len(i) != 0]
    return music_mentions

def main():
    limit = LIMIT
    if limit > MAX_LIMIT:
        limit = MAX_LIMIT

    parser = rss_parser()
    parser.parse(limit)
    titles = parser.get_titles()
    lastfm = lastfm_wrapper()
    lastfm.get_tags_from_titles(titles)
    artist_mentioned = lastfm.get_artists()

    music_mentions = build_json_schema()
    music_mentions = add_entries_to_json(artist_mentioned=artist_mentioned,music_mentions=music_mentions)
    music_mentions = remove_empty(music_mentions)

    jmm = dumps(music_mentions, separators=(",",":"))
    with open("assets/sample.json",'w') as f:
        f.write(str(jmm))

    total_totals = 0
    for mm in music_mentions["music_mentions"]:
        total_totals += mm["genre"]["total"]
    print("Total number of entries from maximum of {} blog feed(s): {}"
          .format(LIMIT if LIMIT < MAX_LIMIT else MAX_LIMIT,total_totals))
    print("Size of json data: {} bytes".format(getsizeof(jmm)))


if __name__ == '__main__':
    start = time()
    main()
    print("\nTotal runtime for {} feed(s) was {} seconds."
          .format(LIMIT if LIMIT < MAX_LIMIT else MAX_LIMIT,round(time() - start, 2)))
