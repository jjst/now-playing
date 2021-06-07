import requests
from aggregators import PlayingItem

url = "https://www.radiomeuh.com/player/rtdata/tracks.json"


def fetch(country_code, station_id):
    response = requests.get(url)
    data = response.json()
    song = data[0]
    title = song['artist'] + " - " + song['titre']
    return [PlayingItem('fr', 'radiomeuh', 'song', title, song)]
