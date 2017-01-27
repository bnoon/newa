pest_status_management = { 
'pest_name': "Oriental Fruit Moth",
'biofix_phenology': "First Trap Catch",
'biofix_abbrev': "ofm",
'biofix2_phenology': "Second Generation Flight Start",
'biofix2_abbrev': None,
'biofix3_phenology': "Third Generation Flight Start",
'biofix3_abbrev': None,
'basetemp': 43,

'pre_biofix': {
0: { 'ddlo':   0, 'ddhi': 129, 'altref': ["Dormant","Silver_Tip","Green_Tip"],
							   'stage': "OFM are overwintering as pupae", 
                               'status': "No OFM flight is expected.", 
                               'management': "Pheromone traps and mating disruption dispensers should be deployed at the beginning of the pink bud stage." },
1: { 'ddlo': 130, 'ddhi': 378, 'altref': ["Half-Inch_Green","Tight_Cluster","Pink_Bud","Bloom","Petal_Fall"],
							   'stage': "First generation moths emerge", 
                               'status': "First catch of moths from the overwintering generation is expected.  Flight of OFM usually begins when trees are in the pink or bloom bud stages.",
                               'management': "No insecticides need to be applied until eggs begin to hatch; since OFM flight usually begins at bloom, it is not possible to apply an initial spray to kill adults." }  },
'post_biofix': {  
0: { 'ddlo':   0, 'ddhi': 150, 'altref': ["Post_0"],
							   'stage': "Moths flying and first egg hatch",
                               'status': "OFM eggs usually begin to hatch at petal fall.",
                               'management': "The normal petal fall spray should control OFM larvae hatching early in the season.  PC is also active at PF, so broad spectrum materials will be needed at this time to control this pest.  If you have had a past history of damage from OFM in an orchard and if trap catches are high (>10/trap/week), it is possible that local OFM populations are resistant to organophosphates and/or pyrethroids.  Therefore, you may want to use another class of chemical at petal fall for OFM control.  Although first generation OFM larvae can damage fruit, particularly in orchards with high pest population densities, most larvae from this generation in apples will infest only apple shoots.  Therefore, the primary reason to control the first brood is to cut down on resident populations in the orchard that could lead to more severe infestations later in the season." ,
                               'pesticide_link': "http://www.dec.ny.gov/nyspad/products?0" },
1: { 'ddlo': 151, 'ddhi': 375, 'altref': ["Post_1"],
							   'stage': "Moths flying & 50% of eggs have hatched",
                               'status': "Moths are still flying and usually about 50-60% of OFM eggs from the first generation have hatched.",
                               'management': "Check the time elapsed after petal fall to determine the exact timing of this second spray.  This second spray should be applied at about 10-14 days after petal fall.  This second spray against the first generation of OFM is particularly important in high-pressure orchards (past history of OFM fruit damage or high pheromone traps catches, (>10/ trap/ week) to control the remainder of hatching larvae.  If this spray is applied at the normal time of a first cover spray (10-14 days after petal fall) it will also control early hatching CM larvae from the first flight of adults.  Also, Plum curculio may still be active at this interval after PF in cool, rainy seasons." ,
                               'pesticide_link': "http://www.dec.ny.gov/nyspad/products?0" },
2: { 'ddlo': 376, 'ddhi': 877, 'altref': ["Post_2"],
							   'stage': "1st moth flight ends and egg hatch over", 
                               'status': "The first flight of moths is diminishing and the start of the seond flight of OFM is expected at 701-1100 degree days.",
                               'management': "It is too late to apply control sprays against the first generation of OFM larvae." }, 
3: { 'ddlo': 878, 'ddhi':1241, 'altref': ["Post_3"],
							   'stage': "2nd generation moths emerge",
                               'status': "The second flight of OFM usually starts in late June to early July in western NY.", 
                               'management': "It is too soon to apply a control spray against the second generation of OFM.  The initial spray should be applied when eggs begin to hatch." } },
'post_biofix2': {  
0: { 'ddlo':   0, 'ddhi': 179, 'altref': ["Post_4"],
							   'stage': "Moths flying, no eggs hatched",
                               'status': "The second flight of OFM and oviposition is increasing, but the first eggs hatch at 150-200 degree days since trap catch.", 
                               'management': "It is too soon to apply a control spray against the second generation of OFM.  The initial spray should be applied when eggs begin to hatch." },
1: { 'ddlo': 180, 'ddhi': 235, 'altref': ["Post_5"],
							   'stage': "Moth flight increasing & 10% of eggs have hatched",
                               'status': "About 10% of the eggs laid by the second generation of OFM have hatched.", 
                               'management': "The initial control spray to control the second generation of OFM should be applied.  In orchards that have a history of previous fruit infestation from this pest, populations may be resistant to organophosphates or pyrethroids.  Therefore, it might be better to use another class of materials against OFM.  Eggs from the summer generation of OBLR may also begin to hatch during this time and, if possible, a material should be selected that also will control larvae of this pest.",
                               'pesticide_link': "http://www.dec.ny.gov/nyspad/products?0"  },
2: { 'ddlo': 236, 'ddhi': 680, 'altref': ["Post_6"],
							   'stage': "Moths flying and peak egg hatch",
                               'status': "The peak flight of the second generation of OFM is expected.", 
                               'management': "Check the interval after the initial control spray for OFM.  If at least 10-14 days have elapsed, apply another control spray.  If the interval is less than 10-14 days, delay the second spray until this time interval has accumulated.  Again, if this is a high-pressure block, consider not using organophosphates or pyrethroids for this second spray.",
                               'pesticide_link': "http://www.dec.ny.gov/nyspad/products?0"  },
3: { 'ddlo': 681, 'ddhi':1018, 'altref': ["Post_7"],
							   'stage': "2nd moth flight ends & egg hatch over",
                               'status': "The second flight of OFM is diminishing.", 
                               'management': "It is too late to apply control sprays against this generation of OFM." },
4: { 'ddlo':1019, 'ddhi':1820, 'altref': ["Post_8"],
							   'stage': "3rd generation moths emerge",
                               'status': "Start of the third flight of OFM.  In western NY the third flight of OFM begins in mid to late August.",
                               'management': "It is too soon to apply a control spray against the third generation of OFM.  The initial spray should be applied when eggs begin to hatch.  Since the third flight of OFM usually begins in late August, you  may want to consider applying a final spray just before September 1, if you don't want to spray after Labor Day." } },
'post_biofix3': {  
0: { 'ddlo':   0, 'ddhi': 235, 'altref': ["Post_9"],
							   'stage': "Moths flying & 10% egg hatch",
                               'status': "About 10% of the eggs laid by the third generation of OFM have hatched. In western NY, this usually occurs in late August to early September.",
                               'management': "Apply insecticides to control newly hatching larvae.  In order to manage insecticide resistance it is best to apply a different class of material to control this third generation of OFM than was used earlier in the season against previous generations.  Sprays to control the third generation of OFM may be necessary for high-pressure orchards.  For mid-season maturing cultivars this spray timed for early hatch may be the last spray of the season.  For late maturing apples, another spray may be needed 10-14 days later.  Observations have shown that late sprays (during September or October) may be necessary to protect fruit of late maturing cultivars if damage from OFM is noted during fruit inspections in the summer.",
                               'pesticide_link': "http://www.dec.ny.gov/nyspad/products?0"  },
1: { 'ddlo': 236, 'ddhi':9999, 'altref': ["Post_10"],
						       'stage': "Moth flight is over",
                               'status': "OFM seasonal activity has finished.",
                               'management': "Control sprays are no longer necessary." } } }