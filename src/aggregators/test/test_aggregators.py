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
        assert (item.title is None or isinstance(item.title, str))
        assert isinstance(item.type, str)
        assert item.type in ('song', 'programme')
        if item.start_time:
            assert isinstance(item.start_time, datetime.datetime)
        if item.end_time:
            assert isinstance(item.end_time, datetime.datetime)
