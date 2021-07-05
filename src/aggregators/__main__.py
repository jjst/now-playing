import sys
import requests

import aggregators
from base import config


def main():
    config.load_logging_config()
    country_code, station_name = sys.argv[1].split('/')
    full_station_id = sys.argv[1]
    aggregator = aggregators.aggregator_for_station(full_station_id)
    session = requests.Session()
    result = aggregator(
        session,
        'now-playing'
    )
    print(result.items)


if __name__ == '__main__':
    main()
