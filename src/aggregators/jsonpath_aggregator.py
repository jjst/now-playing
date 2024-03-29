from jsonpath_ng.ext import parse
import commentjson
import json
from json.decoder import JSONDecodeError
import pprint
import logging
from requests.exceptions import HTTPError

from aggregators import AggregationResult, Song, Programme, Source

PYTHON_JSONPATH_NG_EXT = 'python-jsonpath-ng-ext'
JAVA_JAYWAY = 'java-jayway'
DEFAULT_ENGINE = PYTHON_JSONPATH_NG_EXT

JAVA_JSONPATH_API_URL = "https://java-jsonpath-api-bknua.ondigitalocean.app/"


def fetch(session, request_type: str, item_type: str, station_id: str,
          url: str, field_extractors: dict, engine: str = DEFAULT_ENGINE):
    response = session.get(url)
    try:
        response.raise_for_status()
    except HTTPError as e:
        logging.error(e)
        return AggregationResult(items=[], sources=[])
    json_data = read_json(response)
    logging.debug(f"Raw extracted data from {url}:")
    logging.debug(json_data)
    extracted_json_by_json_query = extract_json(session, field_extractors.values(), json_data, engine)
    field_values = {name: extracted_json_by_json_query[query] for (name, query) in field_extractors.items()}
    # Make sure all field extraction was successful
    playing_items = []
    if all(field_values.values()):
        logging.debug(field_values)
        if item_type == 'song':
            playing_items = [Song(**field_values)]
        elif item_type == 'progamme':
            playing_items = [Programme(**field_values)]
        else:
            raise ValueError(f"Invalid item_type: '{item_type}'")
    return AggregationResult(
        items=playing_items,
        sources=[Source(type='json', data=json_data)]
    )


def read_json(response):
    try:
        return commentjson.loads(response.text)
    except ValueError:
        logging.error("Failed to parse response. Is it valid JSON? Here's what I got:")
        logging.error(response)
        logging.error(response.text)
        return {}


def extract_json(session, jsonpath_queries, json_data, engine=DEFAULT_ENGINE):
    if engine == PYTHON_JSONPATH_NG_EXT:
        query_results = {}
        for query in jsonpath_queries:
            jsonpath_expr = parse(query)
            matches = jsonpath_expr.find(json_data)
            query_results[query] = matches[0].value
    elif engine == JAVA_JAYWAY:
        query_results = query_java_jsonpath_api(session, list(jsonpath_queries), json.dumps(json_data))
        logging.debug("Extraction results from API:")
        logging.debug(f"\n{pprint.pformat(query_results)}\n")
        return {query: first_value(r) for (query, r) in query_results.items()}
    else:
        raise ValueError(f"Invalid jsonpath engine value: '{engine}'")
    return query_results


def first_value(o):
    if isinstance(o, str):
        return o
    else:
        try:
            return next(iter(o))
        except TypeError:
            return o


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
