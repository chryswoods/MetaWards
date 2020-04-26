.PHONY: build dist makedist cov makecov install clean uninstall

# Get the number of workers passed in using "make -j" - I need to 
# pass this to the setup.py script as part of cythonizing.
# Thanks to yashma for this great answer on the stackoverflow post
# https://stackoverflow.com/questions/5303553/gnu-make-extracting-argument-to-j-within-makefile
MAKE_PID := $(shell echo $$PPID)
JOB_FLAG := $(filter -j%, $(subst -j ,-j,$(shell ps T | grep "^\s*$(MAKE_PID).*$(MAKE)")))
JOBS     := $(subst -j,,$(JOB_FLAG))

# Default to running on 4 cores if this is not passed
ifeq ($(JOBS),)
JOBS := 4
endif

build:
	# Get the number jobs requested by "make -j"
	CYTHONIZE=1 CYTHON_NBUILDERS=$(JOBS) python setup.py build -j $(JOBS)

makedist:
	CYTHONIZE=1 python setup.py sdist bdist_wheel

makecov:
	CYTHONIZE=1 CYTHON_LINETRACE=1 CYTHON_NBUILDERS=$(JOBS) python setup.py build_ext --force --inplace -j $(JOBS)

test: install
	pytest --cov=metawards --cov-report html:doc/build/html/cov_html tests

doc: install
	cd doc && make html

# Always build the coverage version from scratch so that
# we line-trace all of the source
cov: clean makecov

# Always build the dist from scratch to prevent
# accidentally distributing line-traced source
dist: clean makedist

install:
	CYTHONIZE=1 pip install .

clean:
	$(RM) -r build dist
	$(RM) -r src/metawards/*.c
	$(RM) -r src/metawards/utils/*.c

uninstall:
	pip uninstall metawards
