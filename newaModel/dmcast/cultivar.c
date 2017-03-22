/* Cultivar specific routines */

#include "dmcast2.h"


int grape_phenology (double A, double B, double k, double m)  
{

	double Dday7;
	int day;

	for (day=1; day<=day_last-1; day++) 
	{
		Dday7 = w[day].dd7;
		c[0].els[day] = A*pow( 1+exp(B-k*Dday7), (1.0/(1.0-m)) );
		if (c[0].els[day] >= 12 && c[0].els12 == 0) c[0].els12 = day;
	}
	c[0].els[day_last] = c[0].els[day_last-1];
	return 0;
}

/* Newly developed model for primary infection */
int primary_infection (void) 
{
	int day;

	for (day=1; day<=day_last-1; day++) 
	{
		if (c[0].els[day] >= 12 && w[day].dlyrain > 2.54 && w[day].dlytemp > 11.1) 
		{
			c[0].primary_inf = day;
			break;
		}
	}
	return 0;
}

/*
CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
CC   This subroutine determines length of incubation period after primary    CC
CC   infection.                                                              CC
CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
C*****************************************************************************C
CC  List of variables:                                                       CC
CC  RINCB = Proportion of incubation period which has passed per hour        CC
CC  SINCB = Sum of RINCB                                                     CC
C****************************************************************************CC
C==When SINCB>=1.0, the incubation period is over. 
*/
int incubation_period (void) 
{
	int day;
	int hour;
	double x;
	double y;
	double sincb;
	double rincb;

	for (day=day_first; day<=day_last; day++) 
	{
		for (hour=0; hour<24; hour++) 
		{
			if ((day==day_first && hour<hour_first) || (day==day_last && hour>hour_last))
				continue;
			if (w[day].temp[hour] > 8.0 && w[day].temp[hour] < 35.0) 
			{
				x = w[day].temp[hour];
				y = 41.961 - 3.5794*x + 0.09803*x*x - 0.0005341*x*x*x;
				if (y > 0) rincb = (1.0/y)/24.0;
				else rincb = 0;
				c[0].rincb[day][hour] = rincb;
			}
			c[0].sincb[day][hour] = c[0].sincb[day][hour-1] + c[0].rincb[day][hour];
		}
	}

	sincb=0;
	for (day=c[0].primary_inf; day<=day_last && c[0].incubation==0; day++)
	{
		for (hour=0; hour<24; hour++) 
		{
			if ((day==day_first && hour<hour_first) || (day==day_last && hour>hour_last))
				break;
			c[0].rincb[day][hour] = c[0].rincb[day][hour];
			sincb += c[0].rincb[day][hour];
			c[0].sincb[day][hour] = sincb;
			if (sincb > 0.9999) 
			{
				c[0].incubation = day;
				break;
			}
		}
	}
	return 0;
}


