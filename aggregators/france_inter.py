import requests
from datetime import datetime
from zoneinfo import ZoneInfo

from aggregators import PlayingItem

url = "https://www.franceinter.fr/programmes"


def fetch():
    response = requests.get(
        url=url,
        params={'xmlHttpRequest': 1, 'ignoreGridHour': 1}
    )
    now_fr = datetime.now(ZoneInfo("Europe/Paris"))
    now = datetime.now()
    playlist = response.json()
    for item in playlist:
        start = datetime.fromtimestamp(item['start'])
        end = datetime.fromtimestamp(item['end'])
        if now >= start and now <= end:
            title = item['conceptTitle'] + " - " + item['expressionTitle']
            return [PlayingItem('fr', 'france-inter', 'programme', title, item)]
