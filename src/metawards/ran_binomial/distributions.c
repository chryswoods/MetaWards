#include "./distributions.h"
#include "./ziggurat_constants.h"
#include "./logfactorial.h"

#include <stdlib.h>

#if defined(_MSC_VER) && defined(_WIN64)
#include <intrin.h>
#endif

void seed_ran_binomial(binomial_rng *rng, uint32_t seed){
  mt19937_seed(&(rng->state), seed);
}

int64_t ran_binomial(binomial_rng *rng, double p, int64_t n){
  return random_binomial(&(rng->state), p, n, &(rng->binomial));
}

binomial_rng * binomial_rng_alloc(void)
{
  return (binomial_rng*)malloc(sizeof(binomial_rng));
}

void binomial_rng_free(binomial_rng *rng)
{
  if (rng != 0){
    free(rng);
  }
}

double next_double(bitgen_t *bitgen_state){
  return mt19937_next_double(bitgen_state);
}

double binomial_rng_uniform(binomial_rng *rng){
  return next_double(&(rng->state));
}

float next_float(bitgen_t *bitgen_state){
  return mt19937_next_double(bitgen_state);
}

uint64_t next_uint64(bitgen_t *bitgen_state){
  return mt19937_next64(bitgen_state);
}

uint32_t next_uint32(bitgen_t *bitgen_state){
  return mt19937_next32(bitgen_state);
}

/* Random generators for external use */
float random_standard_uniform_f(bitgen_t *bitgen_state) {
    return next_float(bitgen_state);
}

double random_standard_uniform(bitgen_t *bitgen_state) {
    return next_double(bitgen_state);
}

static double standard_exponential_unlikely(bitgen_t *bitgen_state,
                                                uint8_t idx, double x) {
  if (idx == 0) {
    /* Switch to 1.0 - U to avoid log(0.0), see GH 13361 */
    return ziggurat_exp_r - log(1.0 - next_double(bitgen_state));
  } else if ((fe_double[idx - 1] - fe_double[idx]) * next_double(bitgen_state) +
                 fe_double[idx] <
             exp(-x)) {
    return x;
  } else {
    return random_standard_exponential(bitgen_state);
  }
}

double random_standard_exponential(bitgen_t *bitgen_state) {
  uint64_t ri;
  uint8_t idx;
  double x;
  ri = next_uint64(bitgen_state);
  ri >>= 3;
  idx = ri & 0xFF;
  ri >>= 8;
  x = ri * we_double[idx];
  if (ri < ke_double[idx]) {
    return x; /* 98.9% of the time we return here 1st try */
  }
  return standard_exponential_unlikely(bitgen_state, idx, x);
}

static float standard_exponential_unlikely_f(bitgen_t *bitgen_state,
                                             uint8_t idx, float x) {
  if (idx == 0) {
    /* Switch to 1.0 - U to avoid log(0.0), see GH 13361 */
    return ziggurat_exp_r_f - logf(1.0f - next_float(bitgen_state));
  } else if ((fe_float[idx - 1] - fe_float[idx]) * next_float(bitgen_state) +
                 fe_float[idx] <
             expf(-x)) {
    return x;
  } else {
    return random_standard_exponential_f(bitgen_state);
  }
}

float random_standard_exponential_f(bitgen_t *bitgen_state) {
  uint32_t ri;
  uint8_t idx;
  float x;
  ri = next_uint32(bitgen_state);
  ri >>= 1;
  idx = ri & 0xFF;
  ri >>= 8;
  x = ri * we_float[idx];
  if (ri < ke_float[idx]) {
    return x; /* 98.9% of the time we return here 1st try */
  }
  return standard_exponential_unlikely_f(bitgen_state, idx, x);
}

double random_standard_normal(bitgen_t *bitgen_state) {
  uint64_t r;
  int sign;
  uint64_t rabs;
  int idx;
  double x, xx, yy;
  for (;;) {
    /* r = e3n52sb8 */
    r = next_uint64(bitgen_state);
    idx = r & 0xff;
    r >>= 8;
    sign = r & 0x1;
    rabs = (r >> 1) & 0x000fffffffffffff;
    x = rabs * wi_double[idx];
    if (sign & 0x1)
      x = -x;
    if (rabs < ki_double[idx])
      return x; /* 99.3% of the time return here */
    if (idx == 0) {
      for (;;) {
        /* Switch to 1.0 - U to avoid log(0.0), see GH 13361 */
        xx = -ziggurat_nor_inv_r * log(1.0 - next_double(bitgen_state));
        yy = -log(1.0 - next_double(bitgen_state));
        if (yy + yy > xx * xx)
          return ((rabs >> 8) & 0x1) ? -(ziggurat_nor_r + xx)
                                     : ziggurat_nor_r + xx;
      }
    } else {
      if (((fi_double[idx - 1] - fi_double[idx]) * next_double(bitgen_state) +
           fi_double[idx]) < exp(-0.5 * x * x))
        return x;
    }
  }
}

float random_standard_normal_f(bitgen_t *bitgen_state) {
  uint32_t r;
  int sign;
  uint32_t rabs;
  int idx;
  float x, xx, yy;
  for (;;) {
    /* r = n23sb8 */
    r = next_uint32(bitgen_state);
    idx = r & 0xff;
    sign = (r >> 8) & 0x1;
    rabs = (r >> 9) & 0x0007fffff;
    x = rabs * wi_float[idx];
    if (sign & 0x1)
      x = -x;
    if (rabs < ki_float[idx])
      return x; /* # 99.3% of the time return here */
    if (idx == 0) {
      for (;;) {
        /* Switch to 1.0 - U to avoid log(0.0), see GH 13361 */
        xx = -ziggurat_nor_inv_r_f * logf(1.0f - next_float(bitgen_state));
        yy = -logf(1.0f - next_float(bitgen_state));
        if (yy + yy > xx * xx)
          return ((rabs >> 8) & 0x1) ? -(ziggurat_nor_r_f + xx)
                                     : ziggurat_nor_r_f + xx;
      }
    } else {
      if (((fi_float[idx - 1] - fi_float[idx]) * next_float(bitgen_state) +
           fi_float[idx]) < exp(-0.5 * x * x))
        return x;
    }
  }
}

double random_standard_gamma(bitgen_t *bitgen_state,
                                            double shape) {
  double b, c;
  double U, V, X, Y;

  if (shape == 1.0) {
    return random_standard_exponential(bitgen_state);
  } else if (shape == 0.0) {
    return 0.0;
  } else if (shape < 1.0) {
    for (;;) {
      U = next_double(bitgen_state);
      V = random_standard_exponential(bitgen_state);
      if (U <= 1.0 - shape) {
        X = pow(U, 1. / shape);
        if (X <= V) {
          return X;
        }
      } else {
        Y = -log((1 - U) / shape);
        X = pow(1.0 - shape + shape * Y, 1. / shape);
        if (X <= (V + Y)) {
          return X;
        }
      }
    }
  } else {
    b = shape - 1. / 3.;
    c = 1. / sqrt(9 * b);
    for (;;) {
      do {
        X = random_standard_normal(bitgen_state);
        V = 1.0 + c * X;
      } while (V <= 0.0);

      V = V * V * V;
      U = next_double(bitgen_state);
      if (U < 1.0 - 0.0331 * (X * X) * (X * X))
        return (b * V);
      /* log(0.0) ok here */
      if (log(U) < 0.5 * X * X + b * (1. - V + log(V)))
        return (b * V);
    }
  }
}

float random_standard_gamma_f(bitgen_t *bitgen_state,
                                             float shape) {
  float b, c;
  float U, V, X, Y;

  if (shape == 1.0f) {
    return random_standard_exponential_f(bitgen_state);
  } else if (shape == 0.0) {
    return 0.0;
  } else if (shape < 1.0f) {
    for (;;) {
      U = next_float(bitgen_state);
      V = random_standard_exponential_f(bitgen_state);
      if (U <= 1.0f - shape) {
        X = powf(U, 1.0f / shape);
        if (X <= V) {
          return X;
        }
      } else {
        Y = -logf((1.0f - U) / shape);
        X = powf(1.0f - shape + shape * Y, 1.0f / shape);
        if (X <= (V + Y)) {
          return X;
        }
      }
    }
  } else {
    b = shape - 1.0f / 3.0f;
    c = 1.0f / sqrtf(9.0f * b);
    for (;;) {
      do {
        X = random_standard_normal_f(bitgen_state);
        V = 1.0f + c * X;
      } while (V <= 0.0f);

      V = V * V * V;
      U = next_float(bitgen_state);
      if (U < 1.0f - 0.0331f * (X * X) * (X * X))
        return (b * V);
      /* logf(0.0) ok here */
      if (logf(U) < 0.5f * X * X + b * (1.0f - V + logf(V)))
        return (b * V);
    }
  }
}

int64_t random_positive_int64(bitgen_t *bitgen_state) {
  return next_uint64(bitgen_state) >> 1;
}

int32_t random_positive_int32(bitgen_t *bitgen_state) {
  return next_uint32(bitgen_state) >> 1;
}

int64_t random_positive_int(bitgen_t *bitgen_state) {
#if ULONG_MAX <= 0xffffffffUL
  return (int64_t)(next_uint32(bitgen_state) >> 1);
#else
  return (int64_t)(next_uint64(bitgen_state) >> 1);
#endif
}

uint64_t random_uint(bitgen_t *bitgen_state) {
#if ULONG_MAX <= 0xffffffffUL
  return next_uint32(bitgen_state);
#else
  return next_uint64(bitgen_state);
#endif
}

/*
 * log-gamma function to support some of these distributions. The
 * algorithm comes from SPECFUN by Shanjie Zhang and Jianming Jin and their
 * book "Computation of Special Functions", 1996, John Wiley & Sons, Inc.
 *
 * If random_loggam(k+1) is being used to compute log(k!) for an integer k, consider
 * using logfactorial(k) instead.
 */
double random_loggam(double x) {
  double x0, x2, xp, gl, gl0;
  RAND_INT_TYPE k, n;

  static double a[10] = {8.333333333333333e-02, -2.777777777777778e-03,
                         7.936507936507937e-04, -5.952380952380952e-04,
                         8.417508417508418e-04, -1.917526917526918e-03,
                         6.410256410256410e-03, -2.955065359477124e-02,
                         1.796443723688307e-01, -1.39243221690590e+00};
  x0 = x;
  n = 0;
  if ((x == 1.0) || (x == 2.0)) {
    return 0.0;
  } else if (x <= 7.0) {
    n = (RAND_INT_TYPE)(7 - x);
    x0 = x + n;
  }
  x2 = 1.0 / (x0 * x0);
  xp = 2 * M_PI;
  gl0 = a[9];
  for (k = 8; k >= 0; k--) {
    gl0 *= x2;
    gl0 += a[k];
  }
  gl = gl0 / x0 + 0.5 * log(xp) + (x0 - 0.5) * log(x0) - x0;
  if (x <= 7.0) {
    for (k = 1; k <= n; k++) {
      gl -= log(x0 - 1.0);
      x0 -= 1.0;
    }
  }
  return gl;
}

/*
double random_normal(bitgen_t *bitgen_state, double loc, double scale) {
  return loc + scale * random_gauss(bitgen_state);
}
*/

double random_normal(bitgen_t *bitgen_state, double loc, double scale) {
  return loc + scale * random_standard_normal(bitgen_state);
}

double random_exponential(bitgen_t *bitgen_state, double scale) {
  return scale * random_standard_exponential(bitgen_state);
}

double random_uniform(bitgen_t *bitgen_state, double lower, double range) {
  return lower + range * next_double(bitgen_state);
}

double random_gamma(bitgen_t *bitgen_state, double shape, double scale) {
  return scale * random_standard_gamma(bitgen_state, shape);
}

float random_gamma_f(bitgen_t *bitgen_state, float shape, float scale) {
  return scale * random_standard_gamma_f(bitgen_state, shape);
}

double random_beta(bitgen_t *bitgen_state, double a, double b) {
  double Ga, Gb;

  if ((a <= 1.0) && (b <= 1.0)) {
    double U, V, X, Y, XpY;
    /* Use Johnk's algorithm */

    while (1) {
      U = next_double(bitgen_state);
      V = next_double(bitgen_state);
      X = pow(U, 1.0 / a);
      Y = pow(V, 1.0 / b);
      XpY = X + Y;
      /* Reject if both U and V are 0.0, which is approx 1 in 10^106 */
      if ((XpY <= 1.0) && (XpY > 0.0)) {
        if (X + Y > 0) {
          return X / XpY;
        } else {
          double logX = log(U) / a;
          double logY = log(V) / b;
          double logM = logX > logY ? logX : logY;
          logX -= logM;
          logY -= logM;

          return exp(logX - log(exp(logX) + exp(logY)));
        }
      }
    }
  } else {
    Ga = random_standard_gamma(bitgen_state, a);
    Gb = random_standard_gamma(bitgen_state, b);
    return Ga / (Ga + Gb);
  }
}

double random_chisquare(bitgen_t *bitgen_state, double df) {
  return 2.0 * random_standard_gamma(bitgen_state, df / 2.0);
}

double random_f(bitgen_t *bitgen_state, double dfnum, double dfden) {
  return ((random_chisquare(bitgen_state, dfnum) * dfden) /
          (random_chisquare(bitgen_state, dfden) * dfnum));
}

double random_standard_cauchy(bitgen_t *bitgen_state) {
  return random_standard_normal(bitgen_state) / random_standard_normal(bitgen_state);
}

double random_pareto(bitgen_t *bitgen_state, double a) {
  return exp(random_standard_exponential(bitgen_state) / a) - 1;
}

double random_weibull(bitgen_t *bitgen_state, double a) {
  if (a == 0.0) {
    return 0.0;
  }
  return pow(random_standard_exponential(bitgen_state), 1. / a);
}

double random_power(bitgen_t *bitgen_state, double a) {
  return pow(1 - exp(-random_standard_exponential(bitgen_state)), 1. / a);
}

double random_laplace(bitgen_t *bitgen_state, double loc, double scale) {
  double U;

  U = next_double(bitgen_state);
  if (U >= 0.5) {
    U = loc - scale * log(2.0 - U - U);
  } else if (U > 0.0) {
    U = loc + scale * log(U + U);
  } else {
    /* Reject U == 0.0 and call again to get next value */
    U = random_laplace(bitgen_state, loc, scale);
  }
  return U;
}

double random_gumbel(bitgen_t *bitgen_state, double loc, double scale) {
  double U;

  U = 1.0 - next_double(bitgen_state);
  if (U < 1.0) {
    return loc - scale * log(-log(U));
  }
  /* Reject U == 1.0 and call again to get next value */
  return random_gumbel(bitgen_state, loc, scale);
}

double random_logistic(bitgen_t *bitgen_state, double loc, double scale) {
  double U;

  U = next_double(bitgen_state);
  if (U > 0.0) {
    return loc + scale * log(U / (1.0 - U));
  }
  /* Reject U == 0.0 and call again to get next value */
  return random_logistic(bitgen_state, loc, scale);
}

double random_lognormal(bitgen_t *bitgen_state, double mean, double sigma) {
  return exp(random_normal(bitgen_state, mean, sigma));
}

double random_rayleigh(bitgen_t *bitgen_state, double mode) {
  return mode * sqrt(-2.0 * log(1.0 - next_double(bitgen_state)));
}

double random_standard_t(bitgen_t *bitgen_state, double df) {
  double num, denom;

  num = random_standard_normal(bitgen_state);
  denom = random_standard_gamma(bitgen_state, df / 2);
  return sqrt(df / 2) * num / sqrt(denom);
}

static RAND_INT_TYPE random_poisson_mult(bitgen_t *bitgen_state, double lam) {
  RAND_INT_TYPE X;
  double prod, U, enlam;

  enlam = exp(-lam);
  X = 0;
  prod = 1.0;
  while (1) {
    U = next_double(bitgen_state);
    prod *= U;
    if (prod > enlam) {
      X += 1;
    } else {
      return X;
    }
  }
}

/*
 * The transformed rejection method for generating Poisson random variables
 * W. Hoermann
 * Insurance: Mathematics and Economics 12, 39-45 (1993)
 */
#define LS2PI 0.91893853320467267
#define TWELFTH 0.083333333333333333333333
static RAND_INT_TYPE random_poisson_ptrs(bitgen_t *bitgen_state, double lam) {
  RAND_INT_TYPE k;
  double U, V, slam, loglam, a, b, invalpha, vr, us;

  slam = sqrt(lam);
  loglam = log(lam);
  b = 0.931 + 2.53 * slam;
  a = -0.059 + 0.02483 * b;
  invalpha = 1.1239 + 1.1328 / (b - 3.4);
  vr = 0.9277 - 3.6224 / (b - 2);

  while (1) {
    U = next_double(bitgen_state) - 0.5;
    V = next_double(bitgen_state);
    us = 0.5 - fabs(U);
    k = (RAND_INT_TYPE)floor((2 * a / us + b) * U + lam + 0.43);
    if ((us >= 0.07) && (V <= vr)) {
      return k;
    }
    if ((k < 0) || ((us < 0.013) && (V > us))) {
      continue;
    }
    /* log(V) == log(0.0) ok here */
    /* if U==0.0 so that us==0.0, log is ok since always returns */
    if ((log(V) + log(invalpha) - log(a / (us * us) + b)) <=
        (-lam + k * loglam - random_loggam(k + 1))) {
      return k;
    }
  }
}

RAND_INT_TYPE random_poisson(bitgen_t *bitgen_state, double lam) {
  if (lam >= 10) {
    return random_poisson_ptrs(bitgen_state, lam);
  } else if (lam == 0) {
    return 0;
  } else {
    return random_poisson_mult(bitgen_state, lam);
  }
}

RAND_INT_TYPE random_negative_binomial(bitgen_t *bitgen_state, double n,
                                       double p) {
  double Y = random_gamma(bitgen_state, n, (1 - p) / p);
  return random_poisson(bitgen_state, Y);
}

RAND_INT_TYPE random_binomial_btpe(bitgen_t *bitgen_state, RAND_INT_TYPE n,
                                   double p, binomial_t *binomial) {
  double r, q, fm, p1, xm, xl, xr, c, laml, lamr, p2, p3, p4;
  double a, u, v, s, F, rho, t, A, nrq, x1, x2, f1, f2, z, z2, w, w2, x;
  RAND_INT_TYPE m, y, k, i;

  if (!(binomial->has_binomial) || (binomial->nsave != n) ||
      (binomial->psave != p)) {
    /* initialize */
    binomial->nsave = n;
    binomial->psave = p;
    binomial->has_binomial = 1;
    binomial->r = r = MIN(p, 1.0 - p);
    binomial->q = q = 1.0 - r;
    binomial->fm = fm = n * r + r;
    binomial->m = m = (RAND_INT_TYPE)floor(binomial->fm);
    binomial->p1 = p1 = floor(2.195 * sqrt(n * r * q) - 4.6 * q) + 0.5;
    binomial->xm = xm = m + 0.5;
    binomial->xl = xl = xm - p1;
    binomial->xr = xr = xm + p1;
    binomial->c = c = 0.134 + 20.5 / (15.3 + m);
    a = (fm - xl) / (fm - xl * r);
    binomial->laml = laml = a * (1.0 + a / 2.0);
    a = (xr - fm) / (xr * q);
    binomial->lamr = lamr = a * (1.0 + a / 2.0);
    binomial->p2 = p2 = p1 * (1.0 + 2.0 * c);
    binomial->p3 = p3 = p2 + c / laml;
    binomial->p4 = p4 = p3 + c / lamr;
  } else {
    r = binomial->r;
    q = binomial->q;
    fm = binomial->fm;
    m = binomial->m;
    p1 = binomial->p1;
    xm = binomial->xm;
    xl = binomial->xl;
    xr = binomial->xr;
    c = binomial->c;
    laml = binomial->laml;
    lamr = binomial->lamr;
    p2 = binomial->p2;
    p3 = binomial->p3;
    p4 = binomial->p4;
  }

/* sigh ... */
Step10:
  nrq = n * r * q;
  u = next_double(bitgen_state) * p4;
  v = next_double(bitgen_state);
  if (u > p1)
    goto Step20;
  y = (RAND_INT_TYPE)floor(xm - p1 * v + u);
  goto Step60;

Step20:
  if (u > p2)
    goto Step30;
  x = xl + (u - p1) / c;
  v = v * c + 1.0 - fabs(m - x + 0.5) / p1;
  if (v > 1.0)
    goto Step10;
  y = (RAND_INT_TYPE)floor(x);
  goto Step50;

Step30:
  if (u > p3)
    goto Step40;
  y = (RAND_INT_TYPE)floor(xl + log(v) / laml);
  /* Reject if v==0.0 since previous cast is undefined */
  if ((y < 0) || (v == 0.0))
    goto Step10;
  v = v * (u - p2) * laml;
  goto Step50;

Step40:
  y = (RAND_INT_TYPE)floor(xr - log(v) / lamr);
  /* Reject if v==0.0 since previous cast is undefined */
  if ((y > n) || (v == 0.0))
    goto Step10;
  v = v * (u - p3) * lamr;

Step50:
  k = llabs(y - m);
  if ((k > 20) && (k < ((nrq) / 2.0 - 1)))
    goto Step52;

  s = r / q;
  a = s * (n + 1);
  F = 1.0;
  if (m < y) {
    for (i = m + 1; i <= y; i++) {
      F *= (a / i - s);
    }
  } else if (m > y) {
    for (i = y + 1; i <= m; i++) {
      F /= (a / i - s);
    }
  }
  if (v > F)
    goto Step10;
  goto Step60;

Step52:
  rho =
      (k / (nrq)) * ((k * (k / 3.0 + 0.625) + 0.16666666666666666) / nrq + 0.5);
  t = -k * k / (2 * nrq);
  /* log(0.0) ok here */
  A = log(v);
  if (A < (t - rho))
    goto Step60;
  if (A > (t + rho))
    goto Step10;

  x1 = y + 1;
  f1 = m + 1;
  z = n + 1 - m;
  w = n - y + 1;
  x2 = x1 * x1;
  f2 = f1 * f1;
  z2 = z * z;
  w2 = w * w;
  if (A > (xm * log(f1 / x1) + (n - m + 0.5) * log(z / w) +
           (y - m) * log(w * r / (x1 * q)) +
           (13680. - (462. - (132. - (99. - 140. / f2) / f2) / f2) / f2) / f1 /
               166320. +
           (13680. - (462. - (132. - (99. - 140. / z2) / z2) / z2) / z2) / z /
               166320. +
           (13680. - (462. - (132. - (99. - 140. / x2) / x2) / x2) / x2) / x1 /
               166320. +
           (13680. - (462. - (132. - (99. - 140. / w2) / w2) / w2) / w2) / w /
               166320.)) {
    goto Step10;
  }

Step60:
  if (p > 0.5) {
    y = n - y;
  }

  return y;
}

RAND_INT_TYPE random_binomial_inversion(bitgen_t *bitgen_state, RAND_INT_TYPE n,
                                        double p, binomial_t *binomial) {
  double q, qn, np, px, U;
  RAND_INT_TYPE X, bound;

  if (!(binomial->has_binomial) || (binomial->nsave != n) ||
      (binomial->psave != p)) {
    binomial->nsave = n;
    binomial->psave = p;
    binomial->has_binomial = 1;
    binomial->q = q = 1.0 - p;
    binomial->r = qn = exp(n * log(q));
    binomial->c = np = n * p;
    binomial->m = bound = (RAND_INT_TYPE)MIN(n, np + 10.0 * sqrt(np * q + 1));
  } else {
    q = binomial->q;
    qn = binomial->r;
    np = binomial->c;
    bound = binomial->m;
  }
  X = 0;
  px = qn;
  U = next_double(bitgen_state);
  while (U > px) {
    X++;
    if (X > bound) {
      X = 0;
      px = qn;
      U = next_double(bitgen_state);
    } else {
      U -= px;
      px = ((n - X + 1) * p * px) / (X * q);
    }
  }
  return X;
}

int64_t random_binomial(bitgen_t *bitgen_state, double p, int64_t n,
                        binomial_t *binomial) {
  double q;

  if ((n == 0LL) || (p == 0.0f))
    return 0;

  if (p <= 0.5) {
    if (p * n <= 30.0) {
      return random_binomial_inversion(bitgen_state, n, p, binomial);
    } else {
      return random_binomial_btpe(bitgen_state, n, p, binomial);
    }
  } else {
    q = 1.0 - p;
    if (q * n <= 30.0) {
      return n - random_binomial_inversion(bitgen_state, n, q, binomial);
    } else {
      return n - random_binomial_btpe(bitgen_state, n, q, binomial);
    }
  }
}
