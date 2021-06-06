import requests

url = "https://www.franceinter.fr/programmes"
requests.get(
    url=url,
    params={'xmlHttpRequest': 1, 'ignoreGridHour': 1}
)
