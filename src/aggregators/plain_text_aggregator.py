from aggregators import PlayingItem


def fetch(session, request_type, url, encoding, item_type='song'):
    response = session.get(url)
    response.encoding = encoding
    title = response.text
    return [PlayingItem(type=item_type, title=title)]
