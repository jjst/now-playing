from jsonpath_ng.ext import parse
import commentjson
import json
from json.decoder import JSONDecodeError
import pprint
import logging


from aggregators import PlayingItem

PYTHON_JSONPATH_NG_EXT = 'python-jsonpath-ng-ext'
JAVA_JAYWAY = 'java-jayway'
DEFAULT_ENGINE = PYTHON_JSONPATH_NG_EXT

# JAVA_JSONPATH_API_URL = "https://java-jsonpath-api-bknua.ondigitalocean.app/"
JAVA_JSONPATH_API_URL = "http://localhost:4567/"


def fetch(session, request_type: str, url: str, field_extractors: dict, format_string: str, engine: str = DEFAULT_ENGINE):
    response = session.get(url)
    json_data = read_json(response)
    extracted_json_by_json_query = extract_json(session, field_extractors.values(), json_data, engine)
    field_values = {name: extracted_json_by_json_query[query] for (name, query) in field_extractors.items()}
    logging.debug(field_values)
    title = format_string.format(**field_values)
    playing_items = [PlayingItem(type='song', title=title)]
    return playing_items


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
    print(request_body)
    print(json.dumps(request_body))
    response = session.post(JAVA_JSONPATH_API_URL, json=request_body)
    try:
        results = response.json()
        logging.debug("API response:")
        logging.debug(results)
        print(type(results))
    except JSONDecodeError:
        logging.error("API response:")
        logging.error(response.text)
    # JSON response for each result is stringified so it needs to be JSON decoded again
    return {jsonpath_query: json.loads(result) for jsonpath_query, result in results.items()}
