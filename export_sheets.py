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

def save_csv(filename, url):
    response = requests.get(url)
    filename = f"{output_dir}/{filename}"
    with open(filename, "wb") as file:
        file.write(response.content)
        print(f"Exported {filename}")

def get_url(sheet_id, gid, file_format):
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format={file_format}&gid={gid}"

urls = {}
urls[f"sarjat.csv"] = get_url(combos_id, "639649563", "tsv")
for level, gid in skill_gids.items():
    urls[f"taso{level}.csv"] = get_url(skills_id, gid, "csv")

# download all
for filename, url in urls.items():
    save_csv(filename, url)
