PYTHON ?= .venv/bin/python
MKDOCS ?= .venv/bin/mkdocs

.PHONY: serve build doctor physics sim check
serve:
	$(MKDOCS) serve --dev-addr 127.0.0.1:8000
build:
	$(PYTHON) scripts/check_content.py
	$(MKDOCS) build --strict
doctor:
	$(PYTHON) examples/00_doctor.py
physics:
	$(PYTHON) examples/01_mujoco_basics.py
sim:
	$(PYTHON) examples/02_strands_so101.py --render
check:
	$(PYTHON) -m unittest discover -s tests -v
	$(PYTHON) scripts/check_content.py
	$(MKDOCS) build --strict
