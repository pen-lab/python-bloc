env-clean:
	rm -rf env

env-upd:
	env/bin/pip install -e .
	env/bin/pip install -r requirements-dev.txt

clean:
	rm -rf build
	rm -rf *egg-info dist

build:
	python3 setup.py sdist