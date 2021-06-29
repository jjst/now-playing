from aggregators import AggregationResult, PlayingItem, Source

url = "https://www.radiomeuh.com/player/rtdata/tracks.json"


def fetch(session, request_type):
    response = session.get(url)
    data = response.json()
    song = data[0]
    title = song['artist'] + " - " + song['titre']
    return AggregationResult(
        items=[PlayingItem('song', title)],
        sources=[Source(type='json', data=data)]
    )
