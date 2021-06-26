from string import Template
from aggregators import PlayingItem

# FIXME: pass these ids as config values straight from the config file
stations = {
    'fr/fip': 7,
    'fr/fip-rock': 64,
    'fr/fip-jazz': 65,
    'fr/fip-groove': 66,
    'fr/fip-pop': 78,
    'fr/fip-electro': 74,
    'fr/fip-monde': 69,
    'fr/fip-reggae': 71,
    'fr/fip-nouveautes': 70
}
persisted_query_hash = "151ca055b816d28507dae07f9c036c02031ed54e18defc3d16feee2551e9a731"

API_URL = 'https://www.fip.fr/latest/api/graphql'

# Using template to avoid complicated shenanigans with {}
vars_template = Template('{"stationIds":$ids}')
extensions_template = Template('{"persistedQuery":{"version":1,"sha256Hash":"$hash"}}')


def build_title(song):
    if song is None:
        return None
    return f"{', '.join(song['interpreters'])} - {song['title']}"


def fetch(session, request_type, station_id):
    ids_str = "[" + str(stations[station_id]) + "]"
    response = session.get(
        url=API_URL,
        params={
            'operationName': 'NowList',
            'variables': vars_template.substitute(ids=ids_str),
            'extensions': extensions_template.substitute(hash=persisted_query_hash)
        }
    )
    json_body = response.json()
    now_playing_list = json_body['data']['nowList']
    songs = [item['song'] for item in now_playing_list]
    playing_items = [
        PlayingItem(type='song', title=build_title(song), metadata=song)
        for song in songs
    ]
    return playing_items
