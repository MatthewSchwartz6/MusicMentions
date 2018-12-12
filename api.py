from json import load
from flask import Flask, jsonify,request,abort
app = Flask(__name__)

with open('assets/sample.json') as f:
    all_entries = load(f)

@app.route('/get_all')
def get_all():
    return jsonify(all_entries)


@app.route('/get_genres')
def get_specific_genres():
    genres = request.args.get('genres')
    if genres is not None:
        return find_genres(genres)
    else:
        return abort(404)


@app.route('/get_specified_subgenres')
def get_specified_subgenres():
    with open('assets/sample.json') as f:
        music_mentions = load(f)

    specified_genres = request.args.get('genres')
    if ',' in specified_genres:
        specified_genres = specified_genres.split(",")
        specified_genres = [s.lower() for s in specified_genres]
        specified_genres = [s.lstrip() for s in specified_genres]
    else:
        specified_genres = specified_genres.lower()
        specified_genres = specified_genres.lstrip()

    if specified_genres is not None:
        for entry in music_mentions['music_mentions']:
            for subg in entry['genre']['subgenres']:
                if subg['name'].lower() not in specified_genres:
                    del subg['name']
                    del subg['total']
                    del subg['date_mentioned']
                    del subg['artists']
            del entry['genre']['artists_mentioned']
            del entry['genre']['date_mentioned']
            del entry['genre']['total']
            entry['genre']['subgenres'] = [i for i in entry['genre']['subgenres'] if len(i) != 0]
            if len(entry['genre']['subgenres']) == 0:
                del entry['genre']
        music_mentions['music_mentions'] = [i for i in music_mentions['music_mentions'] if len(i) != 0]
        return jsonify(music_mentions)
    else:
        return abort(404)


def find_genres(query):
    queries = query.split(",")
    if len(queries) > 1:
        queries = [q.lower() for q in queries]
        found = [entry for entry in all_entries['music_mentions'] if entry['genre']['name'].lower() in queries]
    elif len(queries) == 1:
        single_query = queries[0].lower()
        found = [entry for entry in all_entries['music_mentions'] if entry['genre']['name'].lower() == single_query]
    response = {"music_mentions": found}
    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=False)