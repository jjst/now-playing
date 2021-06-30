import asyncio
import json
import logging
import os
import requests_cache
import boto3
import botocore.exceptions
import time
from aiohttp.web import json_response

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider


from api.models.radio_station_list import RadioStationList
from api.models.radio_station import RadioStation
from api.models.now_playing import NowPlaying
from api.models.stream import Stream

import aggregators
from aggregators import AggregationResult
from base.json import DataClassJSONEncoder
from api.encoder import JSONEncoder as ConnexionJsonEncoder
from base.stations import RadioStationInfo
import base.stations as stations
from base.config import settings

trace.set_tracer_provider(TracerProvider())


cache_ttl = int(os.environ.get("REQUEST_CACHE_TTL_SECONDS", "3"))
session = requests_cache.CachedSession(backend='memory', expire_after=cache_ttl, allowable_methods=('GET', 'POST'))


async def get_stations():
    all_stations = stations.get_all()
    data = RadioStationList(items=[_build_station(s) for s in all_stations])
    return json_response(data=data.to_dict())


async def get_stations_by_country_code(namespace):
    stations_by_country = stations.get_all(namespace=namespace)
    data = RadioStationList(items=[_build_station(s) for s in stations_by_country])
    return json_response(data=data.to_dict())


async def get_now_playing_by_country_code_and_station_id(namespace, slug):
    tracer = trace.get_tracer(__name__)
    logging.info(f"Getting now playing information for station id: '{namespace}/{slug}'")
    try:
        _ = stations.get(namespace, slug)
    except KeyError:
        return json_response(data={'title': "Station not found"}, status=404)
    try:
        aggregator = aggregators.aggregator_for_station(country_code=namespace, station_id=slug)
    except ModuleNotFoundError as e:
        # Couldnt get a valid aggregator
        logging.warn("Could not load station aggregator for station")
        logging.exception(e)
        return json_response(data={'title': f"No 'now-playing' information is available for station '{namespace}/{slug}'"}, status=404)
    try:
        with tracer.start_as_current_span("call_aggregator") as span:
            span.set_attribute('aggregator.module_name', aggregator.module_name)
            for key, val in aggregator.params.items():
                span.set_attribute(f'aggregator.params.{key}', str(val))
            span.set_attribute('station_id', f'{namespace}/{slug}')
            span.set_attribute('namespace', namespace)
            span.set_attribute('slug', slug)
            aggregation_result = aggregator(session, 'now-playing')
            asyncio.create_task(save_aggregation_result_on_s3(f"{namespace}/{slug}", aggregation_result))
        playing_item = next(iter(aggregation_result.items))
        return json_response(data=NowPlaying(type=playing_item.type, title=playing_item.title).to_dict())
    except StopIteration:
        return json_response(data={'title': "Could not fetch now playing information"}, status=500)


async def get_station_by_country_code_and_station_id(namespace, slug):  # noqa: E501
    """
    Returns a radio station

    :param namespace: Country code of a station
    :type namespace: str
    :param slug: ID of a station
    :type slug: str

    :rtype: RadioStation
    """
    try:
        station_info = stations.get(namespace, slug)
        return json_response(data=_build_station(station_info).to_dict())
    except KeyError:
        return json_response(data={'title': "Station not found"}, status=404)


def search(query):  # noqa: E501
    """Finds a station by name

    :param query: Search query

    :rtype: List[SearchResult]
    """
    return []


def _build_station(station_info: RadioStationInfo):
    streams = [Stream(**s) for s in station_info.streams]
    radio_station = RadioStation(
        namespace=station_info.namespace,
        slug=station_info.slug,
        id=f"{station_info.namespace}/{station_info.slug}",
        name=station_info.name,
        favicon=station_info.favicon,
        streams=streams
    )
    return radio_station


async def save_aggregation_result_on_s3(station_id, aggregation_result: AggregationResult):
    if settings.s3.enabled:
        logging.info("Saving aggregated data to S3")
        try:
            tracer = trace.get_tracer(__name__)
            with tracer.start_as_current_span("save_aggregation_result_on_s3"):
                s3 = boto3.resource('s3', endpoint_url=settings.s3.endpoint_url)
                timestamp = int(time.time())
                bucket = s3.Bucket(settings.s3.bucket_name)
                key = f"{station_id}/{timestamp}/extracted.json"
                bucket.put_object(
                    Key=key,
                    Body=json.dumps(aggregation_result.items, cls=DataClassJSONEncoder)
                )
                for source in aggregation_result.sources:
                    if isinstance(source.data, str):
                        extension = "txt"
                        body = source.data
                    else:
                        extension = "json"
                        body = json.dumps(source.data)
                    key = f"{station_id}/{timestamp}/sources/{source.type}/data.{extension}"
                    bucket.put_object(
                        Key=key,
                        Body=body
                    )
        except botocore.exceptions.BotoCoreError as e:
            # Don't error out here, just log a warning.
            # Aggregation was still successful, we just can't gather stats.
            logging.warning("Could not save aggregation results on S3")
            logging.exception(e)
        except botocore.exceptions.ClientError as e:
            # Don't error out here, just log a warning.
            # Aggregation was still successful, we just can't gather stats.
            logging.warning("Could not save aggregation results on S3")
            logging.exception(e)
