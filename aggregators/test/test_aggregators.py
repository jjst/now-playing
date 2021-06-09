import requests_cache
import aggregators

# Used cached session for these tests, we don't really need to call domains multiple times with same query
session = requests_cache.CachedSession(backend='memory', expire_after=60)


def test_fetch_returns_iterable(country_code, station_id, aggregator):
    results = aggregator(session, 'now-playing')
    iter(results)


def test_fetch_returns_playing_items(country_code, station_id, aggregator):
    results = aggregator(session, 'now-playing')
    for item in results:
        assert isinstance(item, aggregators.PlayingItem)


def test_fetch_has_required_fields(country_code, station_id, aggregator):
    results = aggregator(session, 'now-playing')
    for item in results:
        assert (item.title is None or isinstance(item.title, str))
        assert isinstance(item.type, str)
        assert item.type in ('song', 'programme')
