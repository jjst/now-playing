from aggregators import PlayingItem

url = "https://www.cheriefm.fr/onair"


def fetch(session, request_type):
    response = session.get(url)
    data = response.json()
    station_id = "190"
    station = next(station for station in data if station['id'] == station_id)
    song = next(item['song'] for item in station['playlist'] if item['song']['id'] != 0)
    title = f"{song['title']} - {song['artist']}"
    return [PlayingItem(type='song', title=title)]
