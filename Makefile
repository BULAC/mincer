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

# Create a production environnement with just what's needed
initprod:
	python3 -m pip install pip --upgrade --user
	python3 -m pip install pipenv --upgrade --user
	pipenv install --three --skip-lock

# Launch all inexpensive tests
test:
	# Moving to the mincer module dir allows doctests to run properly
	cd mincer; pipenv run py.test --doctest-modules ..

# Launch all tests even the one depending on BULAC servers
alltest:
	# Moving to the mincer module dir allows doctests to run properly
	cd mincer; BULAC_TESTS=1 pipenv run py.test --doctest-modules ..

# Launch only the last failed test
testlast:
	# Moving to the mincer module dir allows doctests to run properly
	cd mincer; pipenv run py.test --doctest-modules --lf ..

# Generate the doc
doc:
	cd docs; make html

# Run the server in production mode
prodrun:
	FLASK_APP=mincer/__init__.py flask run --host=0.0.0.0

# Run the server in debug mode
debugrun:
	FLASK_APP=mincer/__init__.py FLASK_DEBUG=1 flask run --host=0.0.0.0

initdb:
	FLASK_APP=mincer/__init__.py flask initdb

loadbulacdb:
	FLASK_APP=mincer/__init__.py flask loadbulacdb

loaddemodb:
	FLASK_APP=mincer/__init__.py flask loaddemodb
