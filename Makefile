test:
	pytest tests --rootdir=tests --verbosity=1

dist:
	. venv/bin/activate
	pip install -e .[dist]
	python setup.py sdist bdist_wheel
	twine upload dist/*
