import pandas as pd
from jinja2 import Environment, FileSystemLoader
import json
import sys
from combo import Combo
from text_handling import new_element, measure_font, text_classes

# Check if the correct number of arguments is provided
if len(sys.argv) != 2:
    print("No combo file given.")
    sys.exit(1)

color_scheme = 5

# Input-files
combo_file_name = sys.argv[1]
style_file_name = "config/style.json"
color_file_name = f"config/level{color_scheme}.json"

# Set up Jinja2 environment
env = Environment(loader=FileSystemLoader("."),
                  trim_blocks=True,
                  lstrip_blocks=True)

with open(style_file_name, "r") as f:
    d = json.load(f)

# include text classes
d.update({"styles": text_classes})

for style_name, style in d["styles"].items():
    measure_font(style)

# include color pallet and level name
with open(color_file_name, "r") as f:
    color_data = json.load(f)
d["colors"] = color_data

# Add static text elements
d["combo_start"] = new_element("ALKU", "combo_start")

beat_labels = []
for i in range(1,Combo.chunk_size+1):
    beat_labels.append(new_element(str(i), "beat_label"))
d["beat_labels"] = beat_labels

def read_combo(file_path):
    # Read the TSV file into a DataFrame
    df = pd.read_csv(file_path, delimiter='\t')

    # Extract the metadata from the first row of the pair
    combo_title = str(df.iloc[i, 1])
    value = int(df.iloc[i, 0])

    # Extract sequences, skipping the first two columns (metadata)
    rope = df.iloc[:,1].fillna("").tolist()
    feet = df.iloc[:, 2].fillna("").tolist()

    # Create a dictionary for the paired entry
    combo = Combo(title = f"{file_path}",
                  layers = [rope[:-1], feet],
                  stop = rope[-1])

    return dict(combo)

d["combo"] = read_combo(combo_file_name)

combos_template = env.get_template("templates/combo_standalone.svg.jinja")

combos_svg = combos_template.render(d)

# Save the rendered SVG to a file
filename = f"output/combo.svg"
with open(filename, "w") as f:
    f.write(combos_svg)
    print(f"Successfully generated {filename}")

# Save the data array passed to jinja as json for debugging purposes
with open("output/d.json", "w") as json_file:
    json.dump(d, json_file, indent=4, sort_keys=False)

