.PHONY: docs test test-pdb tox pylint pylint-all website

docs:
	rm -rf ./docs/build/*
	sphinx-build -b html ./docs/source ./docs/build

test:
	nosetests --with-coverage --cover-package=eww --cover-package=scripts -s --cover-erase --cover-branches --nocapture --cover-inclusive -x

test-pdb:
	nosetests --with-coverage --cover-package=eww --cover-package=scripts -s --cover-erase --cover-branches --nocapture --cover-inclusive -x --pdb

tox:
	tox

pylint:
	pylint eww

pylint-all:
	pylint eww
	pylint scripts/eww

website:
	rsync -avz website/* eww.io:/var/www/eww.io/
