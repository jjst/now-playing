from aggregators import PlayingItem

import requests


url = "https://www.topmusic.fr/player/widget_title.php"


def fetch(country_code, station_id):
    response = requests.get(url)
    response.encoding = 'latin_1'
    title = response.text
    return [PlayingItem(country_code='fr', station_id='top-music', type='song', title=title)]
