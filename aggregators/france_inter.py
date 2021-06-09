from datetime import datetime

from aggregators import PlayingItem
import logging

url = "https://www.franceinter.fr/programmes"


def fetch(session, request_type):
    return fetch_url(session, url)


def fetch_url(session, url):
    response = session.get(
        url=url,
        params={'xmlHttpRequest': 1, 'ignoreGridHour': 1}
    )
    now = datetime.now()
    playlist = response.json()
    print(playlist)
    for item in playlist:
        start = datetime.fromtimestamp(item['start'])
        end = datetime.fromtimestamp(item['end'])
        if now <= end:
            logging.debug(f'{start} -> {end}: {item["conceptTitle"]} - {item["expressionTitle"]}')
            print(now >= start)
        if now >= start and now <= end:
            if item['conceptTitle'] == item['expressionTitle']:
                title = item['conceptTitle']
            else:
                title = item['conceptTitle'] + " - " + item['expressionTitle']
            return [PlayingItem('programme', title, item)]
