/* miscellaneous functions by Kyu Rang Kim */
#include "dmcast2.h"

int isleap(int year)
/*  purpose	: Is it leap year ?
    input	: integer year
    return	: leap ? 1 : 0          */
{
    if (year % 400 == 0) return(1);
    if (year % 100 == 0) return(0);
    if (year % 4 == 0) return(1);
    return(0);
}

int gre2jul( struct date *d)
/*  purpose         : converts gregorian date to julian day of year
    input data      : struct date
    return          : integer day of year   */
{
    int month[13]={0,31,28,31,30,31,30,31,31,30,31,30,31};
    int i, jd=0;

    month[2]+=isleap(d->da_year);

    for(i=1; i<d->da_mon; i++)
    {
        jd += month[i];
    }
    jd += d->da_day;
    return(jd);
}

struct date * jul2gre(int jd, struct date *d)
/*  purpose	: converts julian day of year to gregorian date
    input data 	: jd = julian day of year
		  *d <= year
    return data : *d => month, date             */
{
	int month[13]={0,31,28,31,30,31,30,31,31,30,31,30,31}, i=1;

	month[2] += isleap(d->da_year);
	month[0] = jd;
	while( (jd - month[i]) > 0 )
	{
		jd -= month[i];
		i++;
	}
	d->da_mon = i;
	d->da_day = jd;
	if( (d->da_day > 31)||(i > 12) ) printf("Given day of year (%d) invalid", 
month[0]);
	return d;
}

struct tm * jul2tm(int year, int day, int hour, struct tm *tm)
/*	purpose		: converts julian day of year to tm structure
	input data     	: year = year (1970 ~ 2105)
                          day  = julian day of year
			  hour = time of the day
	return data     : *tm => month, day of month             */
{
    int month[12]={31,28,31,30,31,30,31,31,30,31,30,31}, i;

    tm->tm_sec = 0;
    tm->tm_min = hour % 100;
    tm->tm_hour= hour / 100;
    tm->tm_year= year - 1900;
    tm->tm_isdst = 0;
    
    month[1] += isleap(year);
    i=0;
    while( (i < 11) && ((day - month[i]) > 0) )
    {
	day -= month[i];
	i++;
    }
    tm->tm_mon = i;
    tm->tm_mday = day;
    if(tm->tm_mday > 31) {
	printf("Given day of year (%d) invalid", month[0]);
	return (NULL);
    } 
    return (tm);
}

/* convert (year, day, time of day) to unix time */
time_t jul2utime(int year, int day, int tod) {
    struct tm time_ptr;
    int month[12] = { 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 };
    int i;

    /* is it leap year? */
	month[1] += isleap(year);

    for (i = 0; (i < 11) && (day - month[i] > 0); i++) 
		day -= month[i];

    time_ptr.tm_sec = 0;
    time_ptr.tm_min = tod % 100;
    time_ptr.tm_hour = tod / 100;
    time_ptr.tm_mday = day;
    time_ptr.tm_mon = i;
    time_ptr.tm_year = year - 1900;
    time_ptr.tm_isdst = 0;

    return(mktime(&time_ptr));
}


/* error logger */
void errlog (const char *format, ...) {
    time_t time_val;
    struct tm *time_ptr;
    char tmp[MAX_BUF];
    va_list ap;

    /* initialize variable arguments */
    va_start(ap, format);
    /* get current time */
    time(&time_val);
    /* print the time string */
    strcpy(tmp, asctime(localtime(&time_val)));
    tmp[strlen(tmp) - 1] = 0;
    strcat(tmp, " ");
    strcat(tmp, format);
    /* trailing '\n' */
    strcat(tmp, "\n");
    /* print message */
    vprintf(tmp, ap);
    /* vfprintf(stdout, tmp, ap); */
    va_end(ap);
}

