#!/usr/bin/env python3

from datetime import datetime
import json
import csv

# source from https://www.arcgis.com/apps/webappviewer/index.html?id=6ede03a9fd0f4b11a45947cca3b13156&extent=-13558123.7027%2C5183492.8301%2C-13539778.8159%2C5192426.4078%2C102100
# e.g. https://services.arcgis.com/H6Mh1bySxR4oHx6x/arcgis/rest/services/KC_Taxlots/FeatureServer/1/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&geometry=%7B%22xmin%22%3A-13554024.76705249%2C%22ymin%22%3A5187567.879180019%2C%22xmax%22%3A-13547613.611304902%2C%22ymax%22%3A5190333.944141162%2C%22spatialReference%22%3A%7B%22wkid%22%3A102100%7D%7D&geometryType=esriGeometryEnvelope&inSR=102100&outFields=*&orderByFields=OBJECTID%20ASC&outSR=102100&resultOffset=0&resultRecordCount=25

with open('raw_gis_feature_dump.json') as f:
    d = json.load(f)


    # clean it up
    cleaned_property_list = []

    for property in d:
        actual_property = property['attributes']
        cleaned_prop_entry = {}

        if "KLAMATH FOREST ESTATES" not in str(actual_property['LEGAL']):
            continue

        for key in actual_property:
            if isinstance(actual_property[key], str):
                cleaned_prop_entry[key] = actual_property[key].strip()
            else:
                cleaned_prop_entry[key] = actual_property[key]

            if key == "SALE_DATE" and cleaned_prop_entry[key]:
                cleaned_prop_entry["SALE_DATE_PARSED"] = datetime.fromtimestamp(cleaned_prop_entry[key] / 1000).strftime('%Y-%m-%d')

        cleaned_property_list.append(cleaned_prop_entry)

    # DUMP CSV
    # keys = cleaned_property_list[0].keys()
    # with open('Klamath Forest Estates + First Addition Property Dump.csv', 'w', newline='') as output_file:
    #     dict_writer = csv.DictWriter(output_file, keys)
    #     dict_writer.writeheader()
    #     dict_writer.writerows(cleaned_property_list)
    # DUMP JSON
    with open('Klamath Forest Estates + First Addition Property Dump.json', 'w') as f:
        json.dump(cleaned_property_list, f)
