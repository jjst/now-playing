from aggregators import PlayingItem

url = "https://www.topmusic.fr/player/widget_title.php"


def fetch(session, request_type, country_code, station_id):
    response = session.get(url)
    response.encoding = 'latin_1'
    title = response.text
    return [PlayingItem(country_code='fr', station_id='top-music', type='song', title=title)]
