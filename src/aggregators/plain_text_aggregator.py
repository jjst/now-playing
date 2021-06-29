from aggregators import AggregationResult, PlayingItem, Source


def fetch(session, request_type, url, encoding, item_type='song'):
    response = session.get(url)
    response.encoding = encoding
    title = response.text
    return AggregationResult(
        items=[PlayingItem(type=item_type, title=title)],
        sources=[Source(type='text', data=response.text)]
    )
