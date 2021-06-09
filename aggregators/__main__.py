import sys
import aggregators
import requests
import logging


logging.basicConfig(encoding='utf-8', level=logging.DEBUG)


def main():
    country_code, station_name = sys.argv[1].split('/')
    full_station_id = sys.argv[1]
    aggregator = aggregators.aggregator_for_station(full_station_id)
    session = requests.Session()
    results = aggregator(
        session,
        'now-playing'
    )
    print(results)


if __name__ == '__main__':
    main()
