from datetime import datetime

from aggregators import PlayingItem

stations = {
    "france-inter": "https://www.franceinter.fr/programmes",
    "france-bleu-alsace": "https://www.francebleu.fr/grid/alsace/1623084241",
    "france-bleu-belfort-montbeliard": "https://www.francebleu.fr/grid/belfort-montbeliard/1623084381",
    "france-bleu-armorique": "https://www.francebleu.fr/grid/armorique/1623086990"
}


def fetch(session, request_type, country_code, station_id):
    url = stations[station_id]
    response = session.get(
        url=url,
        params={'xmlHttpRequest': 1, 'ignoreGridHour': 1}
    )
    now = datetime.now()
    playlist = response.json()
    for item in playlist:
        start = datetime.fromtimestamp(item['start'])
        end = datetime.fromtimestamp(item['end'])
        if now >= start and now <= end:
            if item['conceptTitle'] == item['expressionTitle']:
                title = item['conceptTitle']
            else:
                title = item['conceptTitle'] + " - " + item['expressionTitle']
            return [PlayingItem(country_code, station_id, 'programme', title, item)]
