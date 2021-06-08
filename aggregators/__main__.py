import sys
import aggregators
import requests
import logging


logging.basicConfig(encoding='utf-8', level=logging.DEBUG)


def main():
    country_code, station_name = sys.argv[1].split('/')
    try:
        full_station_id = sys.argv[1]
        aggregator = aggregators.aggregator_for_station(full_station_id)
    except (KeyError, ModuleNotFoundError):
        aggregator_name = sys.argv[2]
        aggregator = aggregators.load(aggregator_name)
    session = requests.Session()
    results = aggregator.fetch(
        session,
        'now-playing',
        country_code,
        station_name
    )
    print(results)


if __name__ == '__main__':
    main()
