/* header file for dmcast2.c */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <dirent.h>
#include <stddef.h>
#include <stdarg.h>
#include <sys/types.h>
#include <sys/stat.h>

// program and model specific definitions
#define MAX_DIRS 512 // max. directory entries in the program root dir
#define MAX_FNAME 128 // max. length of file names
#define MAX_CV 23 // max. number of cultivars
#define MAX_BUF 1024 // max. temporary buffer size

#define WARNING 0 // dmcast risk threshold that determines dm warning
#define RH 0
#define WET 1
#define RAIN 2
#define TEMP 3

#define TRUE 1
#define FALSE 0
#define PI 3.141592
#ifndef min
#define min(x,y) ( ((x) < (y)) ? (x) : (y) )
#endif
#ifndef max
#define max(x,y) ( ((x) > (y)) ? (x) : (y) )
#endif

/* type definition */


struct wthr_t { // weather data (in Celsius and mm)
	double 
		temp[24], rh[24], wet[24], rainfall[24], // OBSERVED DATA
		wetcnt[24], // hours of a consecutive wetness period
		wetmins[24], // wetness period in minutes (wetprd)
		wettemps[24], // sum of temperature during the wetting period (tsumi)
		dd7, dlyrain, dlytemp, // 7C-base degree-day, daily rainfall and temp
		ok[24]; // data were read OK
};

struct cultivar_t { // cultivar specific
	double
		els[367], // daily phenological (Eichhorn and Lorenz) stage of grape vine
		rincb[367][24], sincb[367][24]; // for incubation period after primary infection
	int
		els12, // Julian day of EL stage >= 12
		primary_inf, // Julian day of primary infection (0 for no infection)
		incubation, // Julian day of the completion for incubation period
		dmwarns; // number of DMwarnings
};

struct model_t {
	double
		sp[24], sv[24], dmrisk[24], // key variables: sporulation, survival & risk
		isprd[24], istmp[24], // hrs of sporulation period & avg temp during isprd
		spmort[24], // spore mortality factor
		infect[24]; // infection factor
};

struct warning_t {
	int
		sday, shour, eday, ehour, duration;
	double
		dmrisk;
};

/* default structure definitions */
struct date {
    int	da_year;
    int	da_mon;
    int	da_day;
};


/* global variables */
struct wthr_t *w;
struct model_t *m;
struct warning_t *wrn;
struct cultivar_t *c;
double *raw; // temporary raw data
double raw1, raw2, wthr1, wthr2; // first and last data range for raw and stored
int cyear, // current year
	nsites, // number of sites (subdirectories)
	d_temp, d_rh, d_wet, d_rainfall; // weather data availability

int model_init;
int dmwarns; //sum of DMwarnings
int day_first;
int day_last;
int hour_first;
int hour_last;




/* function definition */
int init_arrays (void);
int clear_arrays (void);
int setup_dm(void);
int read_weatherdata(int endIndex, int *allDays, int *allHours, double *tmp, double *rh, double *prcp, double *lwet, double *ok); 
int process_weatherdata (void);
int calculate_warnings (int day, int hour);

int grape_phenology (double A, double B, double k, double m);
int primary_infection (void);
int incubation_period (void);
int sporulation (int, int);
int survival (int, int);
int infection (int, int);
int run_disease_model(int *w_sday, int *w_shour, int *w_eday, int *w_ehour, int *w_duration, int *w_parms);

int get_current_year(void);
int isleap(int year);
int gre2jul( struct date *d);
struct date * jul2gre(int jd, struct date *d);
struct tm * jul2tm(int year, int day, int hour, struct tm *tm);
time_t jul2utime(int year, int day, int tod);

void errlog (const char *format, ...);
int show (const char *format, ...);
