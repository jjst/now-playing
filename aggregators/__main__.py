import sys
import aggregators


def main():
    aggregator_name = sys.argv[1]
    aggregator = aggregators.load(aggregator_name)
    print(aggregator.fetch())


if __name__ == '__main__':
    main()
