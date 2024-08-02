import pandas as pd
from text_handling import new_element, measure_font

class Combo:
    chunk_size = 8

    def __init__(self, title="Example title", layers=None, stop="STOP"):
        self.skills = {}
        self.title = title
        self.stop = stop
        self.layers = []
        self.build_combo(layers)

    def build_combo(self, layers):
        for j,layer in enumerate(layers):
            num_chunks = (len(layer) - 2) // Combo.chunk_size + 1
            self.layers.append([])
            for i in range(num_chunks):
                chunk = layer[i * Combo.chunk_size : (i+1) * Combo.chunk_size]
                self.layers[j].append(self.build_row(chunk, j))

    def build_row(self, chunk, kind):
        row = []
        for i, beat in enumerate(chunk):
            if beat != "":
                row.append({
                    "text": new_element(beat, f"description_{kind}"),
                    "size": 1
                })
            elif len(row) > 0:
                row[-1]["size"] += 1
        return row

    def __iter__(self):
        # Defining this method allows converting to dictionary
        yield "title", new_element(self.title, "combo_title")
        yield "stop", new_element(self.stop, "combo_stop")
        for i,row in enumerate(self.layers):
            yield f"layer_{i}", row
