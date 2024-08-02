import cairocffi as cairo
import json

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

def set_cairo_context(style):
    context.select_font_face(
            style["font-family"],
            css2cairo_style[style["font-style"]],
            css2cairo_weight[style["font-weight"]])
    context.set_font_size(style["font-size"])

def measure_text_element(elem):
    set_cairo_context(text_classes[elem["style"]])
    extents = context.text_extents(elem["text"])
    elem["x_bearing"] = extents[0]
    elem["y_bearing"] = extents[1]
    elem["width"]     = extents[2]
    elem["height"]    = extents[3]
    elem["x_advance"] = extents[4]
    elem["y_advance"] = extents[5]
    return elem

def measure_font(style):
    set_cairo_context(style)
    extents = context.font_extents()
    style["ascent"]    = extents[0]
    style["descent"]   = extents[1]
    style["height"]    = extents[2]
    style["x_advance"] = extents[3]
    style["y_advance"] = extents[4]
    style["cap_height"] = context.text_extents("ABCDEFGHIJKLMNOPQRSTUVXYZ")[3]
    style["x_height"] = context.text_extents("vwxz")[3]

def new_element(text, style_name):
    elem = {"text": text_filter(text),
            "style": style_name}
    measure_text_element(elem)
    return elem

