# -*- coding: utf-8 -*-
import yaml

stations = [
    {
        "name": "France Bleu Alsace",
        "url": "https://www.francebleu.fr/alsace"
    },
    {
        "name": "France Bleu Armorique",
        "url": "https://www.francebleu.fr/armorique"
    },
    {
        "name": "France Bleu Auxerre",
        "url": "https://www.francebleu.fr/auxerre"
    },
    {
        "name": "France Bleu Azur",
        "url": "https://www.francebleu.fr/azur"
    },
    {
        "name": "France Bleu Béarn Bigorre",
        "url": "https://www.francebleu.fr/bearn"
    },
    {
        "name": "France Bleu Belfort-Montbéliard",
        "url": "https://www.francebleu.fr/belfort-montbeliard"
    },
    {
        "name": "France Bleu Berry",
        "url": "https://www.francebleu.fr/berry"
    },
    {
        "name": "France Bleu Besançon",
        "url": "https://www.francebleu.fr/besancon"
    },
    {
        "name": "France Bleu Bourgogne",
        "url": "https://www.francebleu.fr/bourgogne"
    },
    {
        "name": "France Bleu Breizh Izel",
        "url": "https://www.francebleu.fr/breizh-izel"
    },
    {
        "name": "France Bleu Champagne-Ardenne",
        "url": "https://www.francebleu.fr/champagne-ardenne"
    },
    {
        "name": "France Bleu Cotentin",
        "url": "https://www.francebleu.fr/cotentin"
    },
    {
        "name": "France Bleu Creuse",
        "url": "https://www.francebleu.fr/creuse"
    },
    {
        "name": "France Bleu Drôme Ardèche",
        "url": "https://www.francebleu.fr/drome-ardeche"
    },
    {
        "name": "France Bleu Elsass",
        "url": "https://www.francebleu.fr/elsass"
    },
    {
        "name": "France Bleu Gard Lozère",
        "url": "https://www.francebleu.fr/gard-lozere"
    },
    {
        "name": "France Bleu Gascogne",
        "url": "https://www.francebleu.fr/gascogne"
    },
    {
        "name": "France Bleu Gironde",
        "url": "https://www.francebleu.fr/gironde"
    },
    {
        "name": "France Bleu Hérault",
        "url": "https://www.francebleu.fr/herault"
    },
    {
        "name": "France Bleu Isère",
        "url": "https://www.francebleu.fr/isere"
    },
    {
        "name": "France Bleu La Rochelle",
        "url": "https://www.francebleu.fr/la-rochelle"
    },
    {
        "name": "France Bleu Limousin",
        "url": "https://www.francebleu.fr/limousin"
    },
    {
        "name": "France Bleu Loire Océan",
        "url": "https://www.francebleu.fr/loire-ocean"
    },
    {
        "name": "France Bleu Lorraine Nord",
        "url": "https://www.francebleu.fr/lorraine-nord"
    },
    {
        "name": "France Bleu Maine",
        "url": "https://www.francebleu.fr/maine"
    },
    {
        "name": "France Bleu Mayenne",
        "url": "https://www.francebleu.fr/mayenne"
    },
    {
        "name": "France Bleu Nord",
        "url": "https://www.francebleu.fr/nord"
    },
    {
        "name": "France Bleu Normandie (Calvados - Orne)",
        "url": "https://www.francebleu.fr/normandie-caen"
    },
    {
        "name": "France Bleu Normandie (Seine-Maritime - Eure)",
        "url": "https://www.francebleu.fr/normandie-rouen"
    },
    {
        "name": "France Bleu Occitanie",
        "url": "https://www.francebleu.fr/toulouse"
    },
    {
        "name": "France Bleu Orléans",
        "url": "https://www.francebleu.fr/orleans"
    },
    {
        "name": "France Bleu Paris",
        "url": "https://www.francebleu.fr/107-1"
    },
    {
        "name": "France Bleu Pays Basque",
        "url": "https://www.francebleu.fr/pays-basque"
    },
    {
        "name": "France Bleu Pays d'Auvergne",
        "url": "https://www.francebleu.fr/pays-d-auvergne"
    },
    {
        "name": "France Bleu Pays de Savoie",
        "url": "https://www.francebleu.fr/pays-de-savoie"
    },
    {
        "name": "France Bleu Périgord",
        "url": "https://www.francebleu.fr/perigord"
    },
    {
        "name": "France Bleu Picardie",
        "url": "https://www.francebleu.fr/picardie"
    },
    {
        "name": "France Bleu Poitou",
        "url": "https://www.francebleu.fr/poitou"
    },
    {
        "name": "France Bleu Provence",
        "url": "https://www.francebleu.fr/provence"
    },
    {
        "name": "France Bleu RCFM",
        "url": "https://www.francebleu.fr/rcfm"
    },
    {
        "name": "France Bleu Roussillon",
        "url": "https://www.francebleu.fr/roussillon"
    },
    {
        "name": "France Bleu Saint-Étienne Loire",
        "url": "https://www.francebleu.fr/saint-etienne-loire"
    },
    {
        "name": "France Bleu Sud Lorraine",
        "url": "https://www.francebleu.fr/sud-lorraine"
    },
    {
        "name": "France Bleu Touraine",
        "url": "https://www.francebleu.fr/touraine"
    },
    {
        "name": "France Bleu Vaucluse",
        "url": "https://www.francebleu.fr/vaucluse"
    }
]

s = {}
for station in stations:
    station_id = 'france-bleu-' + station['url'].removeprefix("https://www.francebleu.fr/")
    s[station_id] = {
        'name': station['name'],
        'favicon': 'https://www.francebleu.fr/favicons/favicon-32x32.png',
        'aggregators': {
            'now-playing': [{'module': 'france_bleu', 'params': {'station_id': None}}]
        }
    }

with open('france_bleu.yaml', 'w') as f:
    documents = yaml.dump(s, f, allow_unicode=True, sort_keys=False)
