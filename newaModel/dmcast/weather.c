#include "dmcast2.h"
#include "stdio.h"
#include "stdlib.h"

// read standard and processed weather data => weather data array
// NG for missing values


int read_weatherdata(int endIndex, int *allDays, int *allHours, double *tmp, double *rh, double *prcp, double *lwet, double *ok) 
{
	int index;	
	int day;
	int hour;


	for (day=1; day<=366; day++)
	{
		for (hour=0; hour<=23; hour++)
		{
			w[day].ok[hour] = FALSE;

		}
	}

	
	for (index=0; index<=endIndex; index++)
	{
		day = allDays[index];
		hour = allHours[index];
		w[day].temp[hour] = tmp[index];
		w[day].rh[hour] = rh[index];
		w[day].rainfall[hour] = prcp[index]; 
		w[day].wet[hour] = lwet[index]; 
		w[day].ok[hour] = ok[index];
	}

	day_first= allDays[0];
	hour_first= allHours[0];
	day_last= allDays[endIndex];
	hour_last=allHours[endIndex];


	return 0;
}

// calculate daily weather variables, etc.
int process_weatherdata (void) {
	int day, hour;
	double wetsum=0, wettemps=0, cnt, tmax, dd7=0, wetcnt=0;

	for (day=day_first; day<=day_last; day++) {
		tmax=0; cnt=0;
		w[day].dlyrain = 0;
		w[day].dlytemp = 0;
		for (hour=0; hour<=23; hour++) {
			if ((day==day_first && hour<hour_first) || 
				(day==day_last && hour>hour_last) ||
				(w[day].ok[hour]!=TRUE))
				continue;

			if (w[day].wet[hour] > 0.1666) {
				wetcnt++;
				wetsum += w[day].wet[hour];
				wettemps += w[day].temp[hour];
			} else {
				wetcnt = 0;
				wetsum = 0;
				wettemps = 0;
			}
			w[day].wetcnt[hour] = wetcnt;
			w[day].wetmins[hour] = wetsum * 60;
			w[day].wettemps[hour] = wettemps;

			tmax = max(tmax, w[day].temp[hour]);
			w[day].dlyrain += w[day].rainfall[hour];
			cnt++;
			w[day].dlytemp += (w[day].temp[hour] - w[day].dlytemp) / cnt;
		}
		dd7 += max((tmax-7), 0);
		w[day].dd7 = dd7;
		

	}
	return 0;
}
