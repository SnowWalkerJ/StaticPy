.Phony: clean test benchmark

clean:
	rm tests/*.so
	rm tests/build/*.cpp

test:
	python -m unittest discover -s tests

benchmark: benchmark.py
	python benchmark.py
