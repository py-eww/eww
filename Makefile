.PHONY: docs test test-pdb pylint pylint-all

docs:
	rm -rf ./docs/build/*
	sphinx-build -b html ./docs/source ./docs/build

test:
	nosetests --with-coverage --cover-package=eww -s --cover-erase --cover-branches --nocapture --cover-inclusive -x

test-pdb:
	nosetests --with-coverage --cover-package=eww -s --cover-erase --cover-branches --nocapture --cover-inclusive -x --pdb

pylint:
	pylint eww

pylint-all:
	pylint eww
	pylint scripts/eww
