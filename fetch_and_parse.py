#!/usr/bin/env python3

import json
import csv
import re

import urllib.request
from urllib.parse import urlparse

# source from https://www.arcgis.com/apps/webappviewer/index.html?id=6ede03a9fd0f4b11a45947cca3b13156&extent=-13558123.7027%2C5183492.8301%2C-13539778.8159%2C5192426.4078%2C102100
# e.g. https://services.arcgis.com/H6Mh1bySxR4oHx6x/arcgis/rest/services/KC_Taxlots/FeatureServer/1/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&geometry=%7B%22xmin%22%3A-13533359.186342701%2C%22ymin%22%3A5234228.980643601%2C%22xmax%22%3A-13518836.150968537%2C%22ymax%22%3A5249650.151100115%2C%22spatialReference%22%3A%7B%22wkid%22%3A102100%7D%7D&geometryType=esriGeometryEnvelope&inSR=102100&outFields=*&orderByFields=OBJECTID%20ASC&outSR=102100&resultOffset=50&resultRecordCount=25

# MUST HAVE resultOffset=0&resultRecordCount=1000 SET!!
BASE_URL = "https://services.arcgis.com/H6Mh1bySxR4oHx6x/arcgis/rest/services/KC_Taxlots/FeatureServer/1/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&geometry=%7B%22xmin%22%3A-13533454.732628059%2C%22ymin%22%3A5230932.633798807%2C%22xmax%22%3A-13518931.697253894%2C%22ymax%22%3A5246353.804255321%2C%22spatialReference%22%3A%7B%22wkid%22%3A102100%7D%7D&geometryType=esriGeometryEnvelope&inSR=102100&outFields=*&orderByFields=OBJECTID%20ASC&outSR=102100&resultOffset=0&resultRecordCount=1000"


data = []

for i in range(10):
    base_url_with_offset = re.sub(r'resultOffset=\d*', f"resultOffset={i * 1000}", BASE_URL)
    print(f"Fetching {base_url_with_offset}")
    contents = urllib.request.urlopen(base_url_with_offset).read()
    parsed_contents = json.loads(contents)
    if len(parsed_contents["features"]) < 1:
        break
    else:
        print(f"Adding {len(parsed_contents['features'])} features")
        data = data + parsed_contents["features"]

# clean it up
cleaned_property_list = []

for property in data:
    actual_property = property['attributes']
    cleaned_prop_entry = {}

    if "KLAMATH FOREST ESTATES" not in str(actual_property['LEGAL']):
        continue

    for key in actual_property:
        if isinstance(actual_property[key], str):
            cleaned_prop_entry[key] = actual_property[key].strip()
        else:
            cleaned_prop_entry[key] = actual_property[key]

    cleaned_property_list.append(cleaned_prop_entry)

# DUMP CSV
keys = cleaned_property_list[0].keys()
with open('Klamath Forest Estates + First Addition Property Dump.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(cleaned_property_list)
# DUMP JSON
with open('Klamath Forest Estates + First Addition Property Dump.json', 'w') as f:
    json.dump(cleaned_property_list, f)

print(f"Wrote {len(cleaned_property_list)} to file.")