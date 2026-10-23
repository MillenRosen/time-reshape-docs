SPHINXBUILD ?= sphinx-build
SPHINXOPTS ?= -a -n -W --keep-going
.PHONY: html pdf clean serve check
html:
	$(SPHINXBUILD) -b html $(SPHINXOPTS) source build/html
pdf: html
	python tools/build_pdf.py --copy-to-site
check: pdf
	python tools/check_site.py build/html
	python tools/check_pdf.py build/pdf/TimeReshape-User-Guide.pdf
serve:
	python -m http.server 8056 --bind 127.0.0.1 --directory build/html
clean:
	python -c "import shutil; shutil.rmtree('build', ignore_errors=True)"
