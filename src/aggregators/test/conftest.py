from aggregators import load, load_aggregators


def pytest_generate_tests(metafunc):
    aggs = load_aggregators()
    if "aggregator" in metafunc.fixturenames:
        args = []
        for key, agg_name in aggs.items():
            cc, station_id = key
            agg = load(agg_name)
            args.append((cc, station_id, agg))
        metafunc.parametrize(
            ["country_code", "station_id", "aggregator"],
            args
        )
