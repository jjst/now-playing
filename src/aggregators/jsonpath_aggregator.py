import boto3
import botocore.exceptions
from jsonpath_ng.ext import parse
import commentjson
import json
from json.decoder import JSONDecodeError
import pprint
import logging
import time

from base.config import settings
from aggregators import PlayingItem

PYTHON_JSONPATH_NG_EXT = 'python-jsonpath-ng-ext'
JAVA_JAYWAY = 'java-jayway'
DEFAULT_ENGINE = PYTHON_JSONPATH_NG_EXT

JAVA_JSONPATH_API_URL = "https://java-jsonpath-api-bknua.ondigitalocean.app/"


def fetch(session, request_type: str, station_id: str, url: str, field_extractors: dict, format_string: str, engine: str = DEFAULT_ENGINE):
    print(station_id)
    response = session.get(url)
    json_data = read_json(response)
    logging.debug(f"Raw extracted data from {url}:")
    logging.debug(json_data)
    extracted_json_by_json_query = extract_json(session, field_extractors.values(), json_data, engine)
    field_values = {name: extracted_json_by_json_query[query] for (name, query) in field_extractors.items()}
    # (We intentionally save even on unsuccessful extractions, because it's valuable data)
    save_data_on_s3(station_id, json_data, field_values)
    # Make sure all field extraction was successful
    if all(field_values.values()):
        logging.debug(field_values)
        title = format_string.format(**field_values)
        playing_items = [PlayingItem(type='song', title=title)]
        return playing_items
    return []


def read_json(response):
    return commentjson.loads(response.text)


def extract_json(session, jsonpath_queries, json_data, engine=DEFAULT_ENGINE):
    if engine == PYTHON_JSONPATH_NG_EXT:
        query_results = {}
        for query in jsonpath_queries:
            jsonpath_expr = parse(query)
            matches = jsonpath_expr.find(json_data)
            query_results[query] = matches[0]
    elif engine == JAVA_JAYWAY:
        query_results = query_java_jsonpath_api(session, list(jsonpath_queries), json.dumps(json_data))
        logging.debug("Extraction results from API:")
        logging.debug(f"\n{pprint.pformat(query_results)}\n")
        return {query: r if isinstance(r, str) else r[0] for (query, r) in query_results.items()}
    else:
        raise ValueError(f"Invalid jsonpath engine value: '{engine}'")
    return query_results


def query_java_jsonpath_api(session, jsonpath_queries, json_str):
    request_body = {
        'queries': jsonpath_queries,
        'json_str': json_str
    }
    response = session.post(JAVA_JSONPATH_API_URL, json=request_body)
    try:
        results = response.json()
        logging.debug("API response:")
        logging.debug(results)
    except JSONDecodeError:
        logging.error("API response:")
        logging.error(response.text)
    # JSON response for each result is stringified so it needs to be JSON decoded again
    return {jsonpath_query: json.loads(result) if result else "" for jsonpath_query, result in results.items()}


def save_data_on_s3(station_id, json_data, extracted_data):
    if settings.s3.enabled:
        try:
            s3 = boto3.resource('s3', endpoint_url=settings.s3.endpoint_url)
            timestamp = int(time.time())
            filenames = ("data.json", "extracted.json")
            content = (json_data, extracted_data)
            bucket = s3.Bucket(settings.s3.bucket_name)
            for filename, data in zip(filenames, content):
                key = f"json/{station_id}/{timestamp}/{filename}"
                bucket.put_object(
                    Key=key,
                    Body=json.dumps(data)
                )
        except botocore.exceptions.ClientError as e:
            # Don't error out here, just log a warning.
            # Aggregation was still successful, we just can't gather stats.
            logging.warning("Could not save aggregation results on S3")
            logging.exception(e)
