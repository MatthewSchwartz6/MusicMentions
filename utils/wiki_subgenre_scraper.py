from os import path
import json
import requests
import grequests
from bs4 import BeautifulSoup


base_path = path.dirname(__file__)
file_path = path.abspath(path.join(base_path, "..", "assets/genres.json"))


"""
This is a utility function to create a json file that maps genres to subgenres.
Only call to generate `genres.json`
See ../assets/genres.json
"""
def wiki_subgenre_scraper():
    genres = {}
    base_url = "https://en.wikipedia.org"
    rel_path = '/wiki/Category:Musical_subgenres_by_genre'
    category_class = {"class": "CategoryTreeLabel CategoryTreeLabelNs14 CategoryTreeLabelCategory"}
    resp = requests.get("{}{}".format(base_url,rel_path))
    soup = BeautifulSoup(resp.content,'html.parser')
    a_tags = soup.findAll("a", category_class)
    if len(a_tags) > 0:
        responses = grequests.map([grequests.get("{}{}".format(base_url,a_tag['href']),timeout=4) for a_tag in a_tags])
        for response in responses:
            if response is not None and response.status_code == 200:
                soup = BeautifulSoup(response.content,'html.parser')
                genre = filter_for_genre(soup.find(id='firstHeading').get_text())
                genres[genre] = []
                sub_genres_div = soup.findAll('div', class_='mw-category-group')
                for div in sub_genres_div:
                    sub_genre_a_tags = div.findChildren('a')
                    for sub_g_tag in sub_genre_a_tags:
                        genres[genre].append(filter_for_genre(sub_g_tag.get_text()))
            else:
                print('Failed to get genre resource. Response: {}'.format(response.status_code))

    else:
        print('Failed to get top level resources. Response: {}'.format(resp.status_code))
        exit(1)
    genres_json = json.dumps(genres, indent=4)
    with open(file_path,'w') as f:
        f.write(str(genres_json))


def filter_for_genre(genre):
    if 'Category:' in genre:
        genre = genre[len('Category:'):len(genre)]
    if 'genres' in genre:
        genre = genre[0:len(genre) - len(' genres')]
    if 'music' in genre:
        genre = genre[0:len(genre) - len(' music')]
    if 'styles' in genre:
        genre = genre[0:len(genre) - len(' styles')]
    return genre


if __name__ == '__main__':
    wiki_subgenre_scraper()
