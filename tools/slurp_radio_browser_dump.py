#!/usr/bin/env python3
"""
Slurp data from https://github.com/tunerapp/stations
Try and remove as much duplicates as possible
Generate station config in YAML from it
"""
import json
import os
import re
import sys
import itertools

from unidecode import unidecode


def load_data(path):
    all_stations = []
    for f in os.listdir(path):
        filepath = os.path.join(path, f)
        if filepath.endswith(".json"):
            with open(filepath, 'r') as json_file:
                data = json.load(json_file)
                all_stations.append(data)
    return all_stations


def print_stats(stations):
    print(f"Loaded {len(stations)} stations")
    without_country = len(list(s for s in stations if not s['country_code']))
    print(f"Stations without country: {without_country}")


def generate_slug(station_name):
    slug = unidecode(station_name).lower()
    slug = slug.replace(" - ", "-")
    slug = re.sub('[^\\w-]', '-', slug)
    slug = re.sub('-{2,}', '-', slug)
    slug = re.sub('^-|-$', '', slug)
    return slug


def hash_name(station_name):
    hashed_name = unidecode(station_name).lower()
    hashed_name = re.sub('[^\\w]', '', hashed_name)
    return hashed_name


def main():
    folder = sys.argv[1]
    all_stations = load_data(folder)
    print_stats(all_stations)
    sorted_by_hash = sorted(all_stations, key=lambda s: hash_name(s['name']))
    grouped_by_hash = itertools.groupby(sorted_by_hash, key=lambda s: hash_name(s['name']))
    print(list(grouped_by_hash))


if __name__ == '__main__':
    main()
