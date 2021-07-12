# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import Optional
import re
import os
from pycountry import countries
from pyradios import RadioBrowser
import questionary
from unidecode import unidecode
import requests


subscription_key = os.environ.get("BING_SEARCH_KEY")
search_url = "https://api.bing.microsoft.com/v7.0/search"

radio_browser = RadioBrowser()


@dataclass
class Stream():
    url: str
    codec: Optional[str]
    bitrate_kbps: Optional[str]


def generate_slug(station_name):
    slug = unidecode(station_name).lower()
    slug = slug.replace(" - ", "-")
    slug = re.sub('[^\\w-]', '-', slug)
    slug = re.sub('-{2,}', '-', slug)
    slug = re.sub('^-|-$', '', slug)
    return slug


def guess_station_website_url(station_name, station_country):
    search_term = f"radio {station_name} {station_country}"
    headers = {"Ocp-Apim-Subscription-Key": subscription_key}
    params = {"q": search_term, "textDecorations": True, "textFormat": "HTML"}
    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    search_results = response.json()
    first_result_url = search_results['webPages']['value'][0]['url']
    return first_result_url


def find_stream_urls(station_name, station_country):
    results = radio_browser.search(name=station_name, countrycode=station_country.alpha_2)
    return [Stream(r['url'], r['codec'], r['bitrate']) for r in results]


def ask_whether_to_look_for_streams():
    yes = "Yes, please do"
    no = "No thanks, I would like to enter stream information manually"
    answer = questionary.select(
        "🔍 Would you like me to see if I can find stream URLs for this radio station?",
        choices=[yes, no]
    ).ask()
    return answer == yes


def main():
    print("Want to add a new radio station? Let me help you out!")
    station_name = questionary.text("🔤 What is the name of the station?").ask()
    slug = questionary.text(
        "🔤 Which slug (human-friendly ID) would you like to use for this station?",
        instruction="(if you're not sure, leave the one I picked for you)",
        default=generate_slug(station_name)
    ).ask()
    country_map = {c.name: c for c in countries}
    country_choices = sorted(country_map.keys())
    choice = questionary.select(
        "🗾 Which country is the station from?",
        choices=country_choices
    ).ask()  # returns value of selection
    country = country_map.get(choice)
    guessed_url = guess_station_website_url(station_name, country.name)
    website_url = questionary.text(
        "🌐 What's their website url? ",
        instruction="(I tried to guess it for you, but I might be wrong!)",
        default=guessed_url
    ).ask()
    look_for_streams = ask_whether_to_look_for_streams()
    if look_for_streams:
        streams = find_stream_urls(station_name, country)
        print(streams)
    else:
        stream_url = questionary.text("🎶 What's their stream url? (You can leave this blank)").ask()


if __name__ == '__main__':
    main()
