import requests
import pandas as pd
import sys

output_dir = "data"

# Google Sheet ID
skills_id = "1hLpj9WCNbZWkh2GDwaZfjljmxPirJVj8ya3-OrzzugY"
combos_id = "1O9iQqWXnHhjdNfwnp9KM9OJI419-3nxDVwoiXGXCyKQ"

# GIDs for each tab you want to download
skill_gids = {
    "1": "0",
    "2": "301874984",
    "3": "1708948622",
    "4": "1930734345",
    "5": "1080202319",
    "6": "163001563",
    "7": "540663671"
}
combo_gids = {
    "1": "639649563",
    "2": "315381077",
    "3": "2019480086",
    "4": "1516797408",
    "5": "330080221",
    "6": "232629461",
    "7": "113063900",
}

def save_csv(filename, url):
    response = requests.get(url)
    filename = f"{output_dir}/{filename}"
    with open(filename, "wb") as file:
        file.write(response.content)
        print(f"Exported {filename}")

def get_url(sheet_id, gid, file_format):
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format={file_format}&gid={gid}"

urls = {}
for level, gid in skill_gids.items():
    urls[f"taso{level}.csv"] = get_url(skills_id, gid, "csv")
for level, gid in combo_gids.items():
    urls[f"sarjat{level}.csv"] = get_url(combos_id, gid, "tsv")

# download all
for filename, url in urls.items():
    save_csv(filename, url)
