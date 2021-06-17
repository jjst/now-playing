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


def main():
    folder = sys.argv[1]
    all_stations = load_data(folder)
    print_stats(all_stations)
    print(list(generate_slug(s['name']) for s in all_stations))


if __name__ == '__main__':
    main()
