.PHONY: check_formatting clean lint publish test

check_formatting:
	black --check ./

clean:
	rm -rf build/ dist/ zoia.egg-info/ __pycache__/

lint:
	flake8 ./

publish: clean
	python3 setup.py sdist bdist_wheel
	python3 -m twine upload dist/*

test:
	pytest ./
