# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from dataclasses import dataclass, asdict
from typing import Optional
import re
import os
from pycountry import countries
from pyradios import RadioBrowser
import questionary
from unidecode import unidecode
from prompt_toolkit.shortcuts import ProgressBar
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import TerminalFormatter
import requests
from requests.exceptions import ConnectionError, HTTPError
from streamscrobbler import streamscrobbler
import tempfile
import time
import yaml


subscription_key = os.environ.get("BING_SEARCH_KEY")
audd_token = os.environ.get("AUDD_TOKEN")

search_url = "https://api.bing.microsoft.com/v7.0/search"
audd_url = "https://api.audd.io/"

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
    try:
        response.raise_for_status()
    except HTTPError:
        return None
    search_results = response.json()
    first_result_url = search_results['webPages']['value'][0]['url']
    return first_result_url


def find_stream_urls(station_name, station_country):
    results = radio_browser.search(name=station_name, countrycode=station_country.alpha_2)
    streams = []
    for r in results:
        stream_url = r['url']
        if is_valid_stream_url(stream_url):
            questionary.print(f'✔️  Found valid stream at "{stream_url}"')
            streams.append(Stream(
                stream_url,
                r['codec'].lower(),
                r['bitrate'] if r['bitrate'] != 0 else None
            ))
    return streams


def is_valid_stream_url(url):
    try:
        res = requests.head(url)
        res.raise_for_status()
    except ConnectionError:
        return False
    except HTTPError:
        return False
    return True


def ask_whether_to_look_for_streams():
    yes = "Yes, please do"
    no = "No, I would like to enter stream information manually"
    answer = questionary.select(
        "🔍 Would you like me to see if I can find stream URLs for this radio station?",
        choices=[yes, no]
    ).ask()
    return answer == yes


def ask_whether_to_look_for_aggregators():
    yes = "Yes, find an aggregator for me"
    no = "No, I would like to configure an aggregator manually later"
    answer = questionary.select(
        "🔍 I might be able to automatically find an aggregator for this station. Would you like me to try?",
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


def save_audio_fingerprint(stream_url, max_size_kbs=200, max_duration_seconds=10):
    r = requests.get(stream_url, stream=True)
    audio_file_path = os.path.join(tempfile.gettempdir(), 'stream.mp3')

    with ProgressBar() as pb:
        with open(audio_file_path, 'wb') as f:
            content_iterable = r.iter_content(1024)
            for i, block in enumerate(pb(content_iterable, total=max_size_kbs)):
                f.write(block)
                if i >= max_size_kbs:
                    break

    return audio_file_path


def identify_current_song(stream_url):
    audio_file_path = save_audio_fingerprint(stream_url)
    with open(audio_file_path, 'rb') as f:
        data = {
            'api_token': audd_token,
            'url': 'https://audd.tech/example1.mp3',
            'return': 'apple_music,spotify',
        }
        files = {
            'file': f,
        }
        response = requests.post('https://api.audd.io/', data=data, files=files)
        try:
            response.raise_for_status()
        except HTTPError:
            return None
        else:
            r = response.json()
            try:
                return (r['result']['artist'], r['result']['title'])
            except KeyError:
                return None



def generate_station(country, slug, station_name, website_url, streams, aggregators):
    namespace = country.alpha_2.lower()
    stations = {
        'stations': {
            namespace: {
                slug: {
                    'name': station_name,
                    'website_url': website_url,
                    'streams': [{k: v for k, v in asdict(s).items() if v is not None} for s in streams],
                    'aggregators': {
                        'now-playing': aggregators
                    }
                }
            }
        }
    }
    yaml_string = yaml.dump(stations, sort_keys=False)
    folder_name = f'conf/stations/{namespace}/'
    os.makedirs(folder_name, exist_ok=True)
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


def determine_streams(station_name, country):
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
            questionary.print(
                "! 😬 I didn't find any streams for this station... sorry!",
                style="bold"
            )
    else:
        streams = []
        stream_url = True
        while stream_url:
            stream_url = questionary.text(
                "🎶 What's their stream url?",
                instruction="(leave this blank to abort adding a stream)"
            ).ask()
    return streams


def get_song_metadata_from_stream(stream):
    stationinfo = streamscrobbler.get_server_info(stream.url)
    if stationinfo['metadata']:
        metadata = stationinfo['metadata']
        try:
            song = metadata['song']
        except KeyError:
            return None
        else:
            return song
    return None


def find_stream_aggregator(streams):
    for stream in streams:
        song = get_song_metadata_from_stream(stream)
        if song:
            return {
                'module': 'stream_aggregator',
                'params': {
                    'stream_url': stream.url
                }
            }
    return None


def find_radio_net_aggregator(station_name):
    headers = {'user-agent': 'station-finder/0.0.1'}
    res = requests.get(
        "https://www.radio.net/search",
        params={'q': station_name},
        headers=headers
    )
    res.raise_for_status()
    soup = BeautifulSoup(res.text, features='html.parser')
    span = soup.find("span", text=station_name)
    search_results = span.parent.parent
    station = search_results.find(href=re.compile("^\\/s\\/(?P<station>.+)$"))
    print(station)
    return None


def determine_aggregators(station_name, country, streams):
    look_for_aggegators = ask_whether_to_look_for_aggregators()
    if look_for_aggegators:
        if audd_token and streams:
            questionary.print(
                "👂 Okay, let me try to find which song is currently playing first...",
                style="bold"
            )
            result = identify_current_song(streams[0].url)
            if result:
                (artist, title) = result
                questionary.print(
                    "",
                    style="bold"
                )
            else:
                pass
        aggregator_finders = {
            'stream metadata': lambda: find_stream_aggregator(streams),
            'radio.net': lambda: find_radio_net_aggregator(station_name)
        }
        for aggregator, fn in aggregator_finders.items():
            print(f"  > Trying {aggregator} aggregator...", end=" ")
            result = fn()
            if result:
                print("✔️  Success!")
                return [result]
            else:
                print("❌ No luck.")
    else:
        return []


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
    country = None
    while not country:
        choice = questionary.autocomplete(
            "🗾 Which country is the station from?",
            choices=country_choices
        ).ask()  # returns value of selection
        country = country_map.get(choice)
        if not country:
            questionary.print(
                "! 🤔 I don't know that country... can you pick one from the suggestions?",
                style="bold"
            )
    guessed_url = guess_station_website_url(station_name, country.name)
    if guessed_url:
        instruction = "(I tried to guess it for you, but I might be wrong!)"
    else:
        instruction = None
    website_url = questionary.text(
        "🌐 What's their website url? ",
        instruction=instruction,
        default=(guessed_url or "")
    ).ask()
    streams = determine_streams(station_name, country)
    aggregators = determine_aggregators(station_name, country, streams)
    generate_station(country, slug, station_name, website_url, streams, aggregators)


if __name__ == '__main__':
    main()
