from jsonpath_ng.ext import parse
import json

from aggregators import PlayingItem

PYTHON_JSONPATH_NG_EXT = 'python-jsonpath-ng-ext'
JAVA_JAYWAY = 'java-jayway'
DEFAULT_ENGINE = PYTHON_JSONPATH_NG_EXT

JAVA_JSONPATH_API_URL = "https://java-jsonpath-api-bknua.ondigitalocean.app/"


def fetch(session, request_type: str, url: str, field_extractors: dict, format_string: str, engine: str = DEFAULT_ENGINE):
    response = session.get(
      url
    )
    field_values = {}
    for field_name, field_extractor in field_extractors.items():
        field_values[field_name] = extract_json(session, field_extractor, response, engine)

    title = format_string.format(**field_values)
    playing_items = [PlayingItem(type='song', title=title)]
    return playing_items


def extract_json(session, jsonpath_query, response, engine=DEFAULT_ENGINE):
    if engine == PYTHON_JSONPATH_NG_EXT:
        jsonpath_expr = parse(jsonpath_query)
        matches = jsonpath_expr.find(response.json())
        return matches[0]
    elif engine == JAVA_JAYWAY:
        matches = query_java_jsonpath_api(session, jsonpath_query, response.text)
        return matches[0]
    else:
        raise ValueError(f"Invalid jsonpath engine value: '{engine}'")


def query_java_jsonpath_api(session, jsonpath_query, json_str):
    request_body = {
        'query': jsonpath_query,
        'json_str': json_str
    }
    response = session.post(JAVA_JSONPATH_API_URL, json=request_body)
    return response.json()
