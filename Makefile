SPHINXBUILD ?= sphinx-build
SPHINXOPTS ?= -n -W --keep-going
.PHONY: html clean serve check
html:
	$(SPHINXBUILD) -b html $(SPHINXOPTS) source build/html
check: html
	python tools/check_site.py build/html
serve:
	python -m http.server 8056 --bind 127.0.0.1 --directory build/html
clean:
	python -c "import shutil; shutil.rmtree('build', ignore_errors=True)"
