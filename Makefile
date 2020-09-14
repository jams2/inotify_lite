test:
	pytest

dist:
	. venv/bin/activate
	pip install -e .[dist]
	python setup.py sdist bdist_wheel
	twine upload dist/*
