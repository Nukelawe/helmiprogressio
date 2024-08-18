import cairocffi as cairo
import json, re

with open(f"config/text_classes.json", "r") as f:
    text_classes = json.load(f)

# populate missing values with defaults
for text_class in text_classes:
    for default in text_classes["default"]:
        if default not in text_classes[text_class]:
            text_classes[text_class][default] = text_classes["default"][default]

# map CSS names to Cairo names
css2cairo_style = {"normal": cairo.FONT_SLANT_NORMAL,
                "italic": cairo.FONT_SLANT_ITALIC}
css2cairo_weight = {"normal": cairo.FONT_WEIGHT_NORMAL,
                "bold": cairo.FONT_WEIGHT_BOLD}

# Set up a dummy surface for measurement (dimensions don't matter)
surface = cairo.SVGSurface(None, 210, 297)
context = cairo.Context(surface)

def text_filter(text):
    string = str(text)
    if string == ".": string = ""
    return string.replace("->", "→").replace("*", "×")

def parse_underlined_text(input_string):
    # Use regular expressions to find all underlined sections and the text outside them
    pattern = r"_\((.*?)\)|([^_]+)"
    matches = re.findall(pattern, input_string)
    if input_string == "":
        return [""], [False]

    # Initialize the result list
    words = []
    overlines = []

    for match in matches:
        # The first group (match[0]) contains underlined text, the second group (match[1]) contains regular text
        if match[0]:  # If the first group is not empty, it's an underlined text
            words.append(match[0])
            overlines.append(True)
        if match[1]:  # If the second group is not empty, it's a regular text
            words.append(match[1])
            overlines.append(False)
    return words, overlines

def set_cairo_context(style):
    context.select_font_face(
            style["font-family"],
            css2cairo_style[style["font-style"]],
            css2cairo_weight[style["font-weight"]])
    context.set_font_size(style["font-size"])

def measure_word(word):
    set_cairo_context(text_classes[word["style"]])
    extents = context.text_extents(word["text"])
    word["x_bearing"] = extents[0]
    word["y_bearing"] = extents[1]
    word["width"]     = extents[2]
    word["height"]    = extents[3]
    word["x_advance"] = extents[4]
    word["y_advance"] = extents[5]
    return word

def measure_font(style):
    set_cairo_context(style)
    extents = context.font_extents()
    style["ascent"]    = extents[0]
    style["descent"]   = extents[1]
    style["height"]    = extents[2]
    style["x_advance"] = extents[3]
    style["y_advance"] = extents[4]
    style["cap_height"] = context.text_extents("ABCDEFGHIJKLMNOPQRSTUVXYZ")[3]
    style["real_height"] = context.text_extents("1234567890abcdefghijklmnopqrstuvxyzABCDEFGHIJKLMNOPQRSTUVXYZ")[3]
    style["x_height"] = context.text_extents("vwxz")[3]
    style["x_width"] = context.text_extents("x")[2]

def measure_line(line):
    line["x_bearing"] = line["words"][0]["x_bearing"]
    line["y_bearing"] = line["words"][0]["y_bearing"]
    line["width"] = 0
    line["height"] = 0
    line["x_advance"] = 0
    line["y_advance"] = 0
    for word in line["words"]:
        line["width"] += word["width"]
        line["height"] = max(word["height"], line["height"])
        line["x_advance"] += word["x_advance"]
        line["x_advance"] = max(word["y_advance"], line["y_advance"])

def measure_element(elem):
    elem["x_bearing"] = elem["lines"][0]["words"][0]["x_bearing"]
    elem["y_bearing"] = elem["lines"][0]["words"][0]["y_bearing"]
    elem["width"] = 0
    elem["height"] = 0
    elem["x_advance"] = 0
    for line in elem["lines"]:
        elem["width"] = max(line["width"], elem["width"])
        elem["x_advance"] = max(line["x_advance"], elem["x_advance"])
        elem["height"] += line["height"]

def new_element(text, style):
    text = text_filter(text)
    lines = text.split("\\n ")
    elem = {"lines": [], "style": style}
    for line in lines:
        elem_line = {"words": [], "style": style}
        words, overlines = parse_underlined_text(line)
        for i, word in enumerate(words):
            elem_word = {"text": word, "style": style, "overline": overlines[i]}
            measure_word(elem_word)
            elem_line["words"].append(elem_word)
        measure_line(elem_line)
        elem["lines"].append(elem_line)
    measure_element(elem)
    return elem

