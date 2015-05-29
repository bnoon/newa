/* Secondary infection routines */

#include "dmcast2.h"

/*
C*****************************************************************************C
CC  SP: Sporulation factor                                                    C
CC  SV: Spore survival factor                                                 C
CC  NI: Number of infection periods                                           C
CC  TSUMI: Sum of temperature during an infection period                      C
CC  WETSUM: Sum of wet period during an infection period                      C
CC  ISPD: Hours of sporulation period                                         C
C******************************************************************************
*/

/*
CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
CC   This subroutine estimates sporulation factor at each hour depending on  CC
CC   temperature and relative humidity.                                      CC
CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
C*****************************************************************************C
CC  List of variables:                                                       CC
CC   ISPRD = Hours of sporulation period: Sporulation starts when conditions CC
CC          are favorable at least 4 hours (i.e., ISPD>=4) without any       CC
CC          interuption                                                      CC
CC   ISTMP = Average temperature during ISPRD                                CC
CC   TMPSUM = Sum of hourly temperature during ISPRD                         CC
CC   SP = Sporulation factor                                                 CC
C*****************************************************************************C
CCC==Sporulation occurs only during night (21:00-5:00) and relative humidity
CCC==is greater than 90% 
*/


int run_disease_model(int *w_sday, int *w_shour, int *w_eday, int *w_ehour, int *w_duration, int *w_parms)
{
	int day;
	int hour;

	for (day=day_first; day<=day_last; day++) 
	{
		for (hour=0; hour<=23; hour++) 
		{
			if ((day == day_first && hour < hour_first) || 
				(day == day_last && hour > hour_last)) continue;
			sporulation(day,hour);
			survival(day,hour);
			infection(day,hour);
			calculate_warnings(day,hour);
			if (model_init) model_init = FALSE;
		}
	}

	for (day=0; day<=dmwarns; day++)
	{
		w_sday[day] = wrn[day].sday;
		w_shour[day] = wrn[day].shour;
		w_eday[day] = wrn[day].eday;
		w_ehour[day] = wrn[day].ehour;
		w_duration[day] = wrn[day].duration;
	}
	w_parms[0] = dmwarns;
	w_parms[1] = c[0].els12;
	w_parms[2] = c[0].primary_inf;
	w_parms[3] = c[0].incubation;

	return 0;

}


int sporulation (int day, int hour) {
	static int 
		isprd;
	static double 
		tmpsum;
	double 
		istmp, sp;

	if (model_init) { isprd = 0; tmpsum = 0.0; }

	if ( (hour <= 21 && hour > 5) || w[day].rh[hour] < 90.0 ) {
		isprd = 0;
		tmpsum = 0.0;
		istmp = 0.0;
	}
	if ( (hour > 21 || hour <= 5) && w[day].rh[hour] >= 90.0 ) {
		isprd++;
		tmpsum += w[day].temp[hour];
		istmp = tmpsum/isprd;

		if (isprd < 4)
			sp = 0.0;
		else {
			if (istmp > 13.0 && istmp < 22.5)
				sp = max( (-642.0 + 53.7*istmp - 0.0356*istmp*istmp*istmp)/160.756 , 0.0 );
			else if (istmp >= 22.5 && istmp <= 28.0)
				sp = 1.0;
			else if (istmp > 28.0 && istmp < 30.0)
				sp = 0.1;
			else
				sp = 0.0;
		}
	}
	else
		sp = 0.0;

	m[day].isprd[hour] = isprd;
	m[day].istmp[hour] = istmp;
	m[day].sp[hour] = sp;
	return 0;
}

/*
CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
CC   This subroutine estimates mortality factor of spores and calculates     CC
CC   survival factor at each hour depending on temperature and relative      CC
CC   humidity.                                                               CC
CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
C*****************************************************************************C
CC   List of variables:                                                      CC
CC    SP = Sporulation factor                                                CC
CC    SV = Spore survival factor                                             CC
CC    SPMORT = Spore mortality factor                                        CC
C*****************************************************************************C
*/
int survival (int day, int hour) {
	static double 
		sv;
	double 
		spmort, t;

	if (model_init) sv = 0;

	/* Set SV to the maximum amount of survival or sporulation. */
	if (sv < m[day].sp[hour]) sv = m[day].sp[hour];
	t = w[day].temp[hour];

	/* Calculate SPMORT based on hourly temperature and relative humidity. */
	if (w[day].rh[hour] >= 90.0) {
		if (t <= 25.0)
			spmort = -0.00138 + 0.000496*t;
		else
			spmort = -0.7711 + 0.03126*t;
	} else {
		spmort = exp( -4.2057 - 0.2101*t + 0.0095*t*t );
	}

	spmort = max (spmort, 0.0);

	/* Calculate SV. Set SV=0 if SV<0.0;. */
	sv = sv - spmort;
	sv = max (sv, 0.0);
	m[day].spmort[hour] = spmort;
	m[day].sv[hour] = sv;
	return 0;
}

/*
CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
CC   This subroutine identifies favorable environmental conditions for       CC
CC   infection process of the fungus.  Longer than 10 min of wetness period  CC
CC   is necessary to make infection.                                         CC
CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
C*****************************************************************************C
CC   List of variables:                                                      CC
CC    INFECT = Infection factor                                              CC
CC    TSUMI = Sum of temperature during infection period                     CC
CC    DF = Risk level of disease development                                 CC
CC                                                                           CC
CC    AVTMPI = Average temperature during the infection period               CC
CC    WETPRD = Wetness period in minutes                                     CC
CC    NI = Hours of a consecutive wetness period                             CC
CC    IDSTRT = Starting date of wetness period                               CC
CC    IHSTRT = Starting hour of wetness period                               CC
CC    WETSUM = Sum of wetness period during infection period                 CC
C*****************************************************************************C
*/
int infection (int day, int hour) {
	double 
		tsumi, infect;

	tsumi = w[day].wettemps[hour];

	/* Determine infection factor */
	if(tsumi<45.0)
		infect=0.0;
	else if(tsumi>=45.0 && tsumi<50.0)
		infect=(0.3/5.0)*(tsumi-45.0) + 0.2;
	else if(tsumi>=50.0 && tsumi<71.0)
		infect=(0.5/21.0)*(tsumi-50.0) + 0.5;
	else
		infect=1.0;
	m[day].infect[hour] = infect;
	/* Determine risk level of disease development */
	m[day].dmrisk[hour] = m[day].sv[hour] * infect * 100;
	
	return 0;
}



int calculate_warnings (int day, int hour) {
	static int 
		flag=FALSE,
		duration=0, duration1=0, sday=0, shour=0;
	static double 
		sumrisk;
	int lastdata;

	if (model_init) { 
		flag=FALSE; duration=0; duration1=0; sday=0; shour=0; dmwarns=0; sumrisk=0.0; 
	}

	if (w[day].ok[hour] != TRUE) return 0;

	if (day==day_last && hour==hour_last) lastdata=TRUE;
	else lastdata=FALSE;

	if (m[day].dmrisk[hour] > WARNING) {

		if (flag == FALSE) {
			sday=day; shour=hour;
			flag = TRUE;
		}
		duration++; duration1++;
		sumrisk += m[day].dmrisk[hour];
	}

	if ( (flag==TRUE) && (m[day].dmrisk[hour]<=WARNING || lastdata) ) {
		wrn[dmwarns].sday=sday;
		wrn[dmwarns].shour=shour;
		if (hour == 0) {
			wrn[dmwarns].eday=day-1;
			wrn[dmwarns].ehour=23;
		} else {
            wrn[dmwarns].eday=day;
			wrn[dmwarns].ehour=hour-1;
		}
		wrn[dmwarns].duration=duration1;
		wrn[dmwarns].dmrisk=sumrisk/duration;
		dmwarns++;
		duration=0; duration1=0;
		sumrisk=0.0;
		flag=FALSE;
		

		/* for cultivar specific warnings */
		if (day >= c[0].incubation) {
			c[0].dmwarns++;
		}


	}

	return 0;
}

