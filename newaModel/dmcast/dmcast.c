/* DMCast Version 2.0 by Kyu Rang Kim, Feb. 2003
CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
CC     This program predicts oospore maturation and primary infections of   CC
CC  Plasmopara viticola in the spring and determines infection periods      CC
CC  during the growing season of grapevines.                                CC
CC     This program integrates logic of the POM and the GDM models which    CC
CC  were originally developed by C. Tran Manh Sung and R. C. Seem,          CC
CC  respectively.                                                           CC
CC     This forecasting model was developed by Eun Woo Park, Department of  CC
CC  Agricultural Biology, Seoul National University, Suwon 441-744, Korea   CC
CC  during his one year visit in 1990 to the New York State Agricultural    CC
CC  Experiment Station, Geneva, NY 14456, U.S.A.  His visit was financially CC
CC  supported by the Yunam Foundation, Seoul, Korea. <EWP:20 NOV., 1990>    CC
CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
*/

#include "dmcast2.h"
#define MFREE(x) { if (x) { free (x); (x)=NULL; } }

void free_memory (void) {
	MFREE(c);
	MFREE(w); 
	MFREE(m); 
	MFREE(wrn);
	MFREE(raw);
}

int main (void) 
{

	int id, day, hour;
	return 0;
}


int setup_dm(void)
{
	free_memory();
	model_init = TRUE;
	init_arrays();
	clear_arrays();
	return 0;
}

/* allocate memory for global arrays */
int init_arrays (void) {
	c = calloc(1, sizeof(*c));

	w = calloc(367, sizeof(*w));
	
	m = calloc(367, sizeof(*m));
	
	wrn  = calloc(367, sizeof(*wrn));

	raw = calloc(721, sizeof(*raw));

	return 0;
}

int clear_arrays (void) {
	memset (c, 0x00, 1*sizeof(*c));
	memset (w, 0x00, 367*sizeof(*w));
	memset (m, 0x00, 367*sizeof(*m));
	memset (wrn, 0x00, 367*sizeof(*wrn));
	return 0;
}


