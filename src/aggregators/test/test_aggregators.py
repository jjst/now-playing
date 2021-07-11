import requests_cache
import aggregators
import datetime

# Used cached session for these tests, we don't really need to call domains multiple times with same query
session = requests_cache.CachedSession(backend='memory', expire_after=60)


def test_fetch_returns_aggregation_result(country_code, station_id, aggregator):
    result = aggregator(session, 'now-playing')
    assert isinstance(result, aggregators.AggregationResult)


def test_fetch_has_required_fields(country_code, station_id, aggregator):
    result = aggregator(session, 'now-playing')
    for item in result.items:
        assert (isinstance(item.text, str)) and item.text != ""
        assert isinstance(item.type, str)
        assert item.type in ('song', 'programme')
        if item.start_time:
            assert isinstance(item.start_time, datetime.datetime)
        if item.end_time:
            assert isinstance(item.end_time, datetime.datetime)


def test_fetch_returns_valid_song(country_code, station_id, aggregator):
    result = aggregator(session, 'now-playing')
    for item in result.items:
        if item.type == 'song':
            assert item.artist is not None and item.artist != ""
            assert item.song_title is not None and item.artist != ""


def test_fetch_returns_valid_programme(country_code, station_id, aggregator):
    result = aggregator(session, 'now-playing')
    for item in result.items:
        if item.type == 'programme':
            assert item.programme_title is not None and item.programme_title != ""
            assert item.episode_title is None or isinstance(item.episode_title, str) and item.episode_title != ""
