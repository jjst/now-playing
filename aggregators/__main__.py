import sys
import aggregators


def main():
    try:
        full_station_id = sys.argv[1]
        aggregator = aggregators.aggregator_for_station(full_station_id)
    except (KeyError, ModuleNotFoundError):
        aggregator_name = sys.argv[1]
        aggregator = aggregators.load(aggregator_name)
    country_code, station_name = sys.argv[2].split('/')
    print(aggregator.fetch(country_code, station_name))


if __name__ == '__main__':
    main()
