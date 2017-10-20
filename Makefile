# author: Pierre-Yves Martin <pym.aldebaran@gmail.com>
# copyright: Copyright (C) 2017 GIP BULAC
# license: GNU AGPL V3

.PHONY: docs
# A very good reference makefile https://github.com/requests/requests/blob/master/Makefile

# Create a developpement environnement with all dependancies
initdev:
	python3 -m pip install pip --upgrade --user
	python3 -m pip install pipenv --upgrade --user
	pipenv install --three --dev --skip-lock

# initprod:
# 	python3 -m pip install pip --upgrade --user
# 	python3 -m pip install pipenv --upgrade --user
# 	pipenv install --three --skip-lock

# Launch all tests
test:
	# Moving to the mincer module dir allows doctests to run properly
	cd mincer; pipenv run py.test --doctest-modules ..

# Generate the doc
doc:
	cd docs; make html

# Run the server in production mode
prodrun:
	FLASK_APP=mincer/__init__.py flask run

# Run the server in debug mode
debugrun:
	FLASK_APP=mincer/__init__.py FLASK_DEBUG=1 flask run
