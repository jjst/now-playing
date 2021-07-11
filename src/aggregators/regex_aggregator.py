from aggregators import AggregationResult, Song, Programme, Source
import re


def fetch(session, request_type, url, regex, encoding, item_type='song'):
    response = session.get(url)
    response.encoding = encoding
    text = response.text
    text = text.strip()
    match = re.search(regex, text)
    field_values = match.groupdict()
    if item_type == 'song':
        item = Song(**field_values)
    elif item_type == 'programme':
        item = Programme(**field_values)
    return AggregationResult(
        items=[item],
        sources=[Source(type='text', data=response.text)]
    )
