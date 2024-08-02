import pandas as pd
from jinja2 import Environment, FileSystemLoader
import cairosvg
import json
import sys
import numpy as np
import re
from combo import Combo
from text_handling import new_element, measure_font, text_classes

# Check if the correct number of arguments is provided
if len(sys.argv) != 2:
    sys.exit(1)
level = sys.argv[1]

# Input-files
style_file_name = "config/style.json"
level_file_name = f"config/level{level}.json"
logo_file_name = "static/logo.b64.svg"
skills_file_name = f"data/taso{level}.csv"
combos_file_name = "data/sarjat.csv"

# Set up Jinja2 environment
env = Environment(loader=FileSystemLoader("."),
                  trim_blocks=True,
                  lstrip_blocks=True)

with open(style_file_name, "r") as f:
    d = json.load(f)

# include text classes
d.update({"styles": text_classes})

with open(logo_file_name, "r") as f:
    d["logo"] = f.read()

for style_name, style in d["styles"].items():
    measure_font(style)

# include color pallet and level name
with open(level_file_name, "r") as f:
    level_data = json.load(f)
d["level"] = level
d["name"] = level_data["name"]
del level_data["name"]
d["colors"] = level_data

# Add static text elements
d["combo_start"] = new_element("ALKU", "combo_start")
d["combo_completion"] = new_element("suoritettu", "combo_start")
d["title_circle"] = new_element(d["level"], "title_circle")
d["title_banner"] = new_element(d["name"], "title_banner")
d["name_line"] = new_element("hyppijän nimi", "name_line")

beat_labels = []
for i in range(1,Combo.chunk_size+1):
    beat_labels.append(new_element(str(i), "beat_label"))
d["beat_labels"] = beat_labels
d["table_header"] = [
    new_element("liike", "table_header"),
    new_element("suoritusvaatimus", "table_header")
]

def split_by_underscore(s):
    # Define the regular expression pattern
    pattern = r"(_[^\W]+|[^_]+)"

    # Find all matches
    matches = re.findall(pattern, s)

    # Create a list of booleans indicating if the match starts with an underscore
    has_underscore = [match.startswith('_') for match in matches]

    # Remove the underscore from the matches where it exists
    cleaned_matches = [match[1:] if match.startswith('_') else match for match in matches]

    return cleaned_matches, has_underscore


def read_combos(file_path):
    # Read the TSV file into a DataFrame
    df = pd.read_csv(file_path, delimiter='\t')

    # Initialize a list to store the parsed data entries
    combos = []

    combo_number = 0
    for i in range(0, len(df), 2):
        # Extract the metadata from the first row of the pair
        combo_title = str(df.iloc[i, 1])
        combo_level = int(df.iloc[i, 0])

        # Exclude combos of other levels
        if combo_level != int(level):
            continue

        combo_number += 1

        # Extract sequences, skipping the first two columns (metadata)
        rope = df.iloc[i,2:].fillna("").tolist()
        while rope and rope[-1] == "":
            rope.pop()

        feet = df.iloc[i + 1, 2:len(rope)+1].fillna("").tolist()

        # Create a dictionary for the paired entry
        combo = Combo(title = f"Sarja {combo_number}, {combo_title}",
                      layers = [rope[:-1], feet],
                      stop = rope[-1])

        # Append the entry to the data_entries list
        combos.append(dict(combo))

    return combos

d["combos"] = read_combos(combos_file_name)

#print(json.dumps(d["combos"], indent=4, sort_keys=False))

# read skill table data from google sheet exports
csv = pd.read_csv(skills_file_name, sep=",", na_filter=False)

g = []
skills = []
for i, row in csv.iterrows():
    req_points = row["kategoria"]
    if re.fullmatch(r"\d+", req_points) is not None:
        # create a new group
        g.append({"min_points": int(req_points),
                  "max_points": 0,
                  "indices": []})
    g[-1]["indices"].append(i)

    tick_boxes = []
    for tick in row["tick"].split(" "):
        box = new_element(tick, "tick_box")
        tick_boxes.append(box)
        g[-1]["max_points"] += int(tick)

    liike = new_element(row["liike"], "table_row")
    vaatimus = new_element(row["suoritusvaatimus"], "table_row")

    skills.append({
        "liike": liike,
        "suoritusvaatimus": vaatimus,
        "tick_boxes": tick_boxes,
    })

skill_groups = []
for group in g:
    min_points = group["min_points"]
    max_points = group["max_points"]
    show_label = group["min_points"] < group["max_points"]
    if show_label:
        label = "{}/{}".format(min_points, max_points)
    else:
        label = ""
        # hide tick labels
        for i in group["indices"]:
            for box in skills[i]["tick_boxes"]:
                box["text"] = ""
    skill_groups.append({
        "start_index": group["indices"][0],
        "size": len(group["indices"]),
        "text": new_element(label, "point_requirement")})

d["skills"] = skills
d["skill_groups"] = skill_groups

# Load the SVG template
skills_template = env.get_template("templates/skills.svg.jinja")
combos_template = env.get_template("templates/combos.svg.jinja")

# Render the SVG with the data
skills_svg = skills_template.render(d)
combos_svg = combos_template.render(d)

# Save the rendered SVG to a file
for i, svg in enumerate([skills_svg, combos_svg]):
    filename = f"output/taso{level}-{i}.svg"
    with open(filename, "w") as f:
        f.write(svg)
        print(f"Successfully generated {filename}")

# Save the data array passed to jinja as json for debugging purposes
del(d["logo"])
with open("output/d.json", "w") as json_file:
    json.dump(d, json_file, indent=4, sort_keys=False)
