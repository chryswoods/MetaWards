#ifndef _RANDOMDGEN__DISTRIBUTIONS_H_
#define _RANDOMDGEN__DISTRIBUTIONS_H_

#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>

#define RAND_INT_TYPE int64_t
#define RAND_INT_MAX INT64_MAX

#include "mt19937.h"

typedef mt19937_state bitgen_t;

#ifdef _MSC_VER
#define DECLDIR __declspec(dllexport)
#else
#define DECLDIR extern
#endif

#ifndef MIN
#define MIN(x, y) (((x) < (y)) ? x : y)
#define MAX(x, y) (((x) > (y)) ? x : y)
#endif

#ifndef M_PI
#define M_PI 3.14159265358979323846264338328
#endif

typedef struct s_binomial_t {
  int has_binomial; /* !=0: following parameters initialized for binomial */
  double psave;
  RAND_INT_TYPE nsave;
  double r;
  double q;
  double fm;
  RAND_INT_TYPE m;
  double p1;
  double xm;
  double xl;
  double xr;
  double c;
  double laml;
  double lamr;
  double p2;
  double p3;
  double p4;
} binomial_t;

DECLDIR double random_standard_exponential(bitgen_t *bitgen_state);
DECLDIR float random_standard_exponential_f(bitgen_t *bitgen_state);

DECLDIR int64_t random_binomial(bitgen_t *bitgen_state, double p,
                                int64_t n, binomial_t *binomial);

typedef struct s_binomial_rng_t {
  bitgen_t state;
  binomial_t binomial;
} binomial_rng;

DECLDIR void seed_ran_binomial(binomial_rng *rng, uint32_t seed);

DECLDIR double binomial_rng_uniform(binomial_rng *rng);

DECLDIR int64_t ran_binomial(binomial_rng *rng, double p, int64_t n);

DECLDIR binomial_rng * binomial_rng_alloc(void);
DECLDIR void binomial_rng_free(binomial_rng *rng);

#endif
