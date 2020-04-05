#ifndef _GLOBALS_H
#define _GLOBALS_H

//#define FLU
//#define FLU2
//#define POX
//define DEFAULT
//#define VACCINATE
#define NCOV


//#define SELFISOLATE

//#define WEEKENDS

//#define VTKWARDS
//#define IMPORTS
#define EXTRASEEDS

#define NAMESIZEMAX 10
#define MAXSIZE 10050 // this needs to be more or less accurate, plz.
#define MAXLINKS 2414000
#ifdef FLU
	#define N_INF_CLASSES 5
	#define START_SYMPTOM 2
#endif
#ifdef FLU2
	#define N_INF_CLASSES 6
	#define START_SYMPTOM 2
#endif

#ifdef POX
	#define N_INF_CLASSES 11
	#define START_SYMPTOM 5

#endif
#ifdef DEFAULT
	#define N_INF_CLASSES 3
	#define START_SYMPTOM 1
#endif

#ifdef NCOV
  #define N_INF_CLASSES 5
  #define START_SYMPTOM 3
#endif


typedef struct parameters{

//	FILENAMES:
	char WorkName[100]; // WORK MATRIX
	char PlayName[100]; // PLAY MATRIX
	char WeekendName[100]; // WEEKENDMATRIX
	char IdentifierName[100]; // WARD NAMES
	char IdentifierName2[100]; // WARD ID's (Communities, Counties, Districts, UA's etc);

	char PositionName[100]; // CENTRE of BOUNDING BOXES
	char PlaySizeName[100]; // SIZE OF POPULATION IN THE PLAY PILE

	char SeedName[100]; // LIST OF SEED NODES
	char NodesToTrack[100]; // LIST OF NODES TO TRACK

	char AdditionalSeeding[100]; // LIST OF EXTRA SEED WARDS...

	char UVFilename[100];

	double beta[N_INF_CLASSES];
	double TooIllToMove[N_INF_CLASSES];
	double Progress[N_INF_CLASSES];
	double ContribFOI[N_INF_CLASSES];

	double LengthDay;
	double PLengthDay;
	int initial_inf;

	double StaticPlayAtHome;
	double DynPlayAtHome;

	//	double recover_p;
	double DataDistCutoff;
	double DynDistCutoff;

	double PlayToWork;
	double WorkToPlay;

	int LocalVaccinationThresh;
	int GlobalDetectionThresh;
	int DailyWardVaccinationCapacity;
	double NeighbourWeightThreshold;

	double DailyImports; // proportion of daily imports if #IMPORTS is defined
  double UV;
}parameters;


#ifdef METAWARDS_USE_GSL
#include <gsl/gsl_statistics_double.h>   // gnu scientific libraries
#include <gsl/gsl_rng.h>
#include <gsl/gsl_randist.h>
#include <gsl/gsl_histogram.h>
#include <gsl/gsl_heapsort.h>
#include <gsl/gsl_sort_double.h>
#else
#include "../../src/metawards/ran_binomial/distributions.h"

#define gsl_rng_default 0

typedef binomial_rng gsl_rng;
inline double gsl_rng_uniform(gsl_rng *rng){
	return binomial_rng_uniform(rng);
}

inline int64_t gsl_ran_binomial(gsl_rng *rng, double p, int64_t n){
	return ran_binomial(rng, p, n);
}

inline gsl_rng* gsl_rng_alloc(int _unused){
	return binomial_rng_alloc();
}

inline void gsl_rng_set(gsl_rng *rng, int seed){
	seed_ran_binomial(rng, seed);
}

inline void gsl_rng_free(gsl_rng *rng){
	binomial_rng_free(rng);
}
#endif // if METAWARDS_USE_GSL // else // endif


#endif
