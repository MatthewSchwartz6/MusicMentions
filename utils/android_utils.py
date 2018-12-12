#coding=utf8
import json
from os import path

base_path = path.dirname(__file__)
file_path = path.abspath(path.join(base_path, "..", "assets/genres.json"))


def format_genres_for_android_strings():
    """
    Utils script to generate Android string resources
    """
    with open(file_path) as f:
        genres = json.load(f)
    print('<string-array name="genres">')
    for genre in list(genres.keys()):
        print ("<item>{}</item>".format(genre))
    print("</string-array>")
    print('<array name = "subgenres">')
    for genre in genres:
        print('<item>')
        print('<array name="{}">'.format(str(genre).replace(' ', '_')))
        for subgenre in genres[genre]:
            print("<item>{}</item>".format(subgenre))
            print("<item>//</item>")
        print("</array>")
        print('</item>')
    print('</array>')


if __name__ == '__main__':
    format_genres_for_android_strings()
