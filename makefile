NUMBERS   = 1 2 3 4 5 6 7
CSV_FILES = $(addsuffix .csv,$(addprefix data/taso,$(NUMBERS)))
svgs      = $(addsuffix .svg,$(addprefix output/taso,$(NUMBERS)))
pdfs      = $(svgs:.svg=.pdf)
templates = templates/base.svg.jinja templates/skill_table.svg.jinja templates/skills.svg.jinja templates/combos.svg.jinja

# Default target
output/helmiprogressio.pdf: $(pdfs) | output
	pdfunite $(pdfs) $@

# Target to generate SVG
output/taso%-0.svg output/taso%-1.svg: generate_svg.py combo.py text_handling.py \
	$(templates) static/logo.b64.svg \
	data/taso%.csv data/sarjat.csv \
	config/level%.json config/style.json config/text_classes.json \
	| output
	python $< $*

# Target to convert SVG to PDF
output/taso%-0.pdf: output/taso%-0.svg | output
	cairosvg -f pdf -u -o $@ $<

output/taso%-1.pdf: output/taso%-1.svg | output
	cairosvg -f pdf -u -o $@ $<

output/taso%.pdf: output/taso%-0.pdf output/taso%-1.pdf | output
	@pdf_files="$(filter %.pdf,$^)";\
	pdfunite $$pdf_files $@

data/taso%.csv: export_sheets.py
	python $< $*

output:
	mkdir -p output

# Clean target to remove generated files
clean:
	rm -f output/*.svg output/*.pdf

downloads:
	python export_sheets.py

static/logo.b64.svg: static/logo.svg
	base64 $< > $@

.PHONY: data clean downloads

