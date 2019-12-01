.Phony: clean test benchmark

clean:
	rm tests/*.so
	rm -r build dist tests/build
	rm -r StaticPy.egg-info

test:
	python -m unittest discover -s tests

benchmark: benchmark.py
	python benchmark.py
