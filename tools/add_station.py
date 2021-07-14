# -*- coding: utf-8 -*-
from adblockparser import AdblockRules
import click
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
from prompt_toolkit import print_formatted_text, ANSI
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import TerminalFormatter
import requests
from requests.exceptions import ConnectionError, HTTPError
from retry import retry
from streamscrobbler import streamscrobbler
import tempfile
import time
import yaml
import asyncio
import nest_asyncio
import pyppeteer
from pyppeteer import launch


subscription_key = os.environ.get("BING_SEARCH_KEY")
audd_token = os.environ.get("AUDD_TOKEN")

search_url = "https://api.bing.microsoft.com/v7.0/search"
audd_url = "https://api.audd.io/"

radio_browser = RadioBrowser()


def fetch_adblock_rules():
    adblock_rules_url = "https://easylist.to/easylist/easylist.txt"
    r = requests.get(adblock_rules_url, allow_redirects=True)
    return AdblockRules(r.iter_lines(decode_unicode=True))


adblock_rules = fetch_adblock_rules()


class NonFatal(Exception):
    pass


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


@retry(NonFatal, tries=3, delay=5)
def identify_current_song(stream_url, retries=3):
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
            raise NonFatal("Got wrong HTTP response from audd API")
        else:
            r = response.json()
            result = r['result']
            try:
                return (result['artist'], result['title'])
            except TypeError:
                raise NonFatal()
            except KeyError:
                raise NonFatal()


async def generate_station(country, slug, station_name, website_url, player_url, streams, aggregators):
    namespace = country.alpha_2.lower()
    stations = {
        'stations': {
            namespace: {
                slug: {
                    'name': station_name,
                    'website_url': website_url,
                    'player_url': player_url,
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


@retry(NonFatal, tries=3, delay=2)
def get_song_metadata_from_stream(stream):
    stationinfo = streamscrobbler.get_server_info(stream.url)
    if stationinfo['metadata']:
        metadata = stationinfo['metadata']
        try:
            song = metadata['song']
        except KeyError:
            raise NonFatal("Could not get song metadata")
        else:
            return song
    raise NonFatal("Could not get song metadata")


async def find_stream_aggregator(streams):
    for stream in streams:
        try:
            song = get_song_metadata_from_stream(stream)
        except NonFatal:
            pass
        if song:
            return {
                'module': 'stream_aggregator',
                'params': {
                    'stream_url': stream.url
                }
            }
    return None


async def find_radio_net_aggregator(station_name):
    headers = {'user-agent': 'station-finder/0.0.1'}
    res = requests.get(
        "https://www.radio.net/search",
        params={'q': station_name},
        headers=headers
    )
    res.raise_for_status()
    soup = BeautifulSoup(res.text, features='html.parser')
    span = soup.find("span", text=station_name)
    regex = re.compile("^\\/s\\/(?P<station>.+)$")
    if span:
        search_results = span.parent.parent
        station = search_results.find(href=regex)
        if station:
            href = station['href']
            match = regex.search(href)
            if match:
                radio_net_id = match.group('station')
                return {
                    'module': 'radio_net_aggregator',
                    'params': {
                        'radio_net_id': radio_net_id
                    }
                }
    return None


async def find_jsonpath_xpath_aggregator(page_url, artist, title):
    loop = asyncio.new_event_loop()
    loop.set_debug(True)
    resps = []

    extensions_to_ignore = ('.js', '.css')

    # FIXME: https://docs.python.org/3/library/asyncio-task.html#waiting-primitives
    async def async_handler(response):
        resps.append(response)

    def handler(response):
        # Hack because handler can't be async
        loop.run_until_complete(async_handler(response))

    browser = await launch()
    page = await browser.newPage()
    page.on('response', handler)

    try:
        await asyncio.wait_for(page.goto(page_url), timeout=30.0)
    except asyncio.exceptions.TimeoutError:
        pass
    for resp in resps:
        if any(resp.url.endswith(ext) for ext in extensions_to_ignore) or adblock_rules.should_block(resp.url):
            # print(f"Skipping {resp.url}")
            pass
        else:
            try:
                txt = await asyncio.wait_for(resp.text(), timeout=5.0)
            except UnicodeDecodeError:
                pass
            except asyncio.exceptions.TimeoutError:
                pass
            except pyppeteer.errors.NetworkError:
                pass
            else:
                if artist in txt or title in txt:
                    print(f"Response {resp.url} contains artist or title: {txt}")


async def determine_aggregators(station_name, country, player_url, streams):
    look_for_aggegators = ask_whether_to_look_for_aggregators()
    if look_for_aggegators:
        aggregator_finders = {
            'stream metadata': find_stream_aggregator(streams),
            'radio.net': find_radio_net_aggregator(station_name)
        }
        results = []
        if audd_token and streams:
            questionary.print(
                "👂 Okay, now, let me try to find which song is currently playing first...",
                style="bold"
            )
            try:
                artist, title = identify_current_song(streams[0].url)
            except NonFatal:
                pass
            else:
                print_formatted_text(ANSI(
                    f'👉 I think I found what\'s currently playing: 🎵 \x1b[1m{title}\x1b[0m by \x1b[1m{artist}\x1b[0m'
                ))
                aggregator_finders['jsonpath/xpath'] = find_jsonpath_xpath_aggregator(player_url, artist, title)
        for aggregator, coroutine in aggregator_finders.items():
            print(f"  > Trying {aggregator} aggregator...", end=" ")
            result = await coroutine
            if result:
                print("✔️  Success!")
                results.append(result)
            else:
                print("❌ No luck.")
    else:
        return []


async def add_station(slug=None, country_code=None, station_name=None, website_url=None, player_url=None):
    print("Want to add a new radio station? Let me help you out!")
    if not station_name:
        station_name = questionary.text("🔤 What is the name of the station?").ask()
    if not slug:
        slug = questionary.text(
            "🔤 Which slug (human-friendly ID) would you like to use for this station?",
            instruction="(if you're not sure, leave the one I picked for you)",
            default=generate_slug(station_name)
        ).ask()
    if not country_code:
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
    else:
        country = countries.get(alpha_2=country_code)
    if not website_url:
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
    if not player_url:
        player_url = questionary.text(
            f'🎧 Can you give me the URL of a page on "{website_url}" where I can listen to the live stream?',
            instruction="(it can be the same as the homepage sometimes - leave blank if you can't find it)",
        ).ask()
    streams = determine_streams(station_name, country)
    aggregators = await determine_aggregators(station_name, country, player_url, streams)
    await generate_station(country, slug, station_name, website_url, player_url, streams, aggregators)


@click.command()
@click.option('--slug')
@click.option('--country-code')
@click.option('--name')
@click.option('--website-url')
@click.option('--player-url')
def main(slug=None, country_code=None, name=None, website_url=None, player_url=None):
    nest_asyncio.apply()
    loop = asyncio.new_event_loop()
    loop.run_until_complete(add_station(slug, country_code, name, website_url, player_url))


if __name__ == '__main__':
    main()
