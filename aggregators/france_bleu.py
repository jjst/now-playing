from aggregators import france_inter

base_url = "https://www.francebleu.fr/grid"


def fetch(session, request_type, country_code, station_id):
    location = station_id.removeprefix('france-bleu-')  # bit hackish but eh
    url = f"{base_url}/{location}"
    return france_inter.fetch_url(session, url, country_code, station_id)
