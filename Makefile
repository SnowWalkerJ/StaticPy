.Phony: clean test

clean:
	rm tests/*.so
	rm tests/build/*.cpp

test:
	python -m unittest discover -s tests