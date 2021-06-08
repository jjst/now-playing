from aggregators import aggregators, load


def pytest_generate_tests(metafunc):
    print("calling generate_tests")
    if "aggregator" in metafunc.fixturenames:
        args = []
        for key, agg_name in aggregators.items():
            cc, station_id = key
            agg = load(agg_name)
            args.append((cc, station_id, agg))
        metafunc.parametrize(
            ["country_code", "station_id", "aggregator"],
            args
        )
