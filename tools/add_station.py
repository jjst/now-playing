# -*- coding: utf-8 -*-
from dataclasses import dataclass, asdict
from typing import Optional
import re
import os
from pycountry import countries
from pyradios import RadioBrowser
import questionary
from unidecode import unidecode
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import TerminalFormatter
import requests
import yaml


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
    return [
        Stream(
            r['url'],
            r['codec'].lower(),
            r['bitrate'] if r['bitrate'] != 0 else None
        ) for r in results
    ]


def ask_whether_to_look_for_streams():
    yes = "Yes, please do"
    no = "No, I would like to enter stream information manually"
    answer = questionary.select(
        "🔍 Would you like me to see if I can find stream URLs for this radio station?",
        choices=[yes, no]
    ).ask()
    return answer == yes


def guess_codec(stream_url):
    if stream_url.endswith('.mp3'):
        return 'mp3'
    elif stream_url.endswith('.aac'):
        return 'aac'
    elif stream_url.endswith('.aac'):
        return 'aac'


def generate_station(country, slug, station_name, website_url, streams):
    namespace = country.alpha_2.lower()
    stations = {
        'stations': {
            namespace: {
                slug: {
                    'name': station_name,
                    'website_url': website_url,
                    'streams': [{k: v for k, v in asdict(s).items() if v is not None} for s in streams],
                    'aggregators': {
                        'now-playing': {}
                    }
                }
            }
        }
    }
    yaml_string = yaml.dump(stations, sort_keys=False)
    filename = f'conf/stations/{namespace}/{slug}.yaml'
    with open(filename, 'w') as f:
        f.write(yaml_string)
    print()
    questionary.print(
        f"🙌 Success! I generated the following configuration file for you at '{filename}':"
    )
    lexer = get_lexer_by_name("yaml", stripall=True)
    formatter = TerminalFormatter()
    result = highlight(yaml_string, lexer, formatter)
    print(result)


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
        if streams:
            selected_stream_urls = questionary.checkbox(
                "🎉 I found some matching streams! Which ones would you like me to include?",
                choices=[s.url for s in streams]
            ).ask()
            streams = [s for s in streams if s.url in selected_stream_urls]
    else:
        streams = []
        stream_url = True
        while stream_url:
            stream_url = questionary.text(
                "🎶 What's their stream url?",
                instruction="(leave this blank to abort adding a stream)"
            ).ask()
    generate_station(country, slug, station_name, website_url, streams)



if __name__ == '__main__':
    main()
