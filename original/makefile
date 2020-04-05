LD = gcc
CC = gcc

# To use GSL, define METAWARDS_USE_GSL and include
# these GSL libraries and includes in CFLAGS
#GSL_INC = $(shell gsl-config --cflags)
#GSL_LIB = $(shell gsl-config --libs)

JSON_C_INC = -I/usr/local/include/json-c    # $(shell pkg-config --cflags json-c)
JSON_C_LIB = -L/usr/local/include -ljson-c  # $(shell pkg-config --libs json-c)

CFLAGS = $(JSON_C_INC) $(JSON_C_LIB)

metawards: src/*.c src/*.h
	$(CC) src/*.c ../src/metawards/ran_binomial/*.c -o metawards $(CFLAGS) -Isrc -lgsl -lm -O3

clean:  
	rm metawards
