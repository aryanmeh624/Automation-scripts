VENV ?= .venv
REQUIREMENTS_FILE ?= requirements.txt

init:
	python3 -m venv $(VENV)
	$(VENV)/bin/python -m pip install --upgrade pip
	if [ -f $(REQUIREMENTS_FILE) ]; \
	    then $(VENV)/bin/python -m pip3 install -r $(REQUIREMENTS_FILE); \
    fiw