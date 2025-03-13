NUMBERS   = 1 2 3 4 5 6 7
CSV_FILES = $(addsuffix .csv,$(addprefix data/taso,$(NUMBERS)))
svgs      = $(addsuffix .svg,$(addprefix output/taso,$(NUMBERS)))
titles    = $(addsuffix .png,$(addprefix output/title,$(NUMBERS)))
pdfs      = $(svgs:.svg=.pdf)
templates = templates/base.svg.jinja templates/skill_table.svg.jinja templates/skills.svg.jinja \
	templates/combos.svg.jinja templates/combo.svg.jinja templates/macros.svg.jinja

front_page_diagrams = front_page/skill_table_example.pdf front_page/tickbox_empty.pdf front_page/tickbox_1.pdf \
	front_page/tickbox_2.pdf front_page/kategoriapisteet.pdf front_page/kategoriaesimerkki.pdf front_page/titles.pdf

# Default target
output/tasopassit.pdf: set_metadata.sh output/front_page.pdf $(pdfs) | output
	pdfunite output/front_page.pdf $(pdfs) output/tasopassit_nometa.pdf
	./$<

output/tasopassit_nocover.pdf: set_metadata.sh output/front_page.pdf $(pdfs) | output
	pdfunite $(pdfs) output/tasopassit_nocover.pdf

# front page
output/front_page.pdf: front_page/front_page.tex $(front_page_diagrams)
	xelatex --output-directory output $<

# Target to generate SVG
output/taso%-0.svg output/taso%-1.svg: generate_svg.py combo.py text_handling.py \
	$(templates) static/logo.b64.svg \
	data/taso%.csv data/sarjat%.csv \
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

data/taso%.csv data/sarjat%.csv: export_sheets.py
	python $< $*

output:
	mkdir -p output

output/title%.svg: generate_title.py
	python $< $*

output/title%.png: output/title%.svg
	magick -density 300 $< $@

titles:
	make $(titles)

# Clean target to remove generated files
clean:
	rm -f output/*.svg output/*.pdf

downloads:
	python export_sheets.py

static/logo.b64.svg: static/logo.svg
	base64 $< > $@

.PHONY: data clean downloads titles

