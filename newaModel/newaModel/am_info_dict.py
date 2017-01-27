pest_status_management = { 
'pest_name': "Apple Maggot",
'biofix_phenology' : "First Trap Catch",
'biofix_abbrev': None,
'basetemp': 50,

'pre_biofix': {
0: { 'ddlo':   0, 'ddhi': 795, 'altref': ["Dormant","Silver_Tip","Green_Tip","Half-Inch_Green","Tight_Cluster","Pink_Bud","Bloom","Petal_Fall","Post_Petal_Fall"],
							   'stage': "Overwintering as pupae", 
                               'status': "Predicted first emergence of <a href='http://nysipm.cornell.edu/factsheets/treefruit/pests/am/am.asp' target='_blank'>apple maggot</a> occurs after approximately 796 to 1297 degree days have accumulated.", 
                               'management': "No control measures recommended at this time." },
1: { 'ddlo': 796, 'ddhi':1297, 'altref': ["Pre_1"],
							   'stage': "First adult emergence", 
                               'status': "<a href='http://nysipm.cornell.edu/factsheets/treefruit/pests/am/am_fig1.asp' target='_blank'>Apple maggot</a> flies usually emerge first in unsprayed apple trees.  Females are capable of laying eggs 7-10 days after the emerge.  AM usually initially lay <a href='http://nysipm.cornell.edu/factsheets/treefruit/pests/am/am_fig5.asp' target='_blank'>eggs</a> in unsprayed apple trees outside of commercial orchards.  Then later in the summer (late July-August) mature females begin to immigrate into the edges of commercial orchards.",
                               'management': "Most commercial apple orchards have no indigenous populations of AM.  AM infestations in commercial orchards result from flies immigrating into the orchards from outside sources.  AM <a href='http://nysipm.cornell.edu/publications/apple_man/files/am.pdf' target='_blank'>volatile-baited sticky spheres</a> should be deployed along the edges of commercial orchards that are closest to outside sources of apple maggots (abandoned orchards, unsprayed homeowner's trees, feral apple trees).   (See link to AM monitoring in recommends).  Check traps at least once/week." }},
'post_biofix': {
0: { 'datelo':0, 'datehi':+7,  'altref': ["Post_0"],
							   'stage': "Sexually immature females",
                               'status': "Early emerging AM females are still sexually immature and have not yet started to lay eggs.",
                               'management': "It is still too early to apply insecticide sprays against AM even if flies have been captured on traps deployed along the edges of commercial apple orchards." },
1: { 'datelo':+8, 'datehi':(7,31,23), 'altref': ["Post_1"],
							   'stage': "Adults and first eggs",
                               'status': "Adult apple maggots are active in abandoned orchards or unsprayed trees and capable of laying eggs. In July, most flies stay in unsprayed areas outside of orchards and usaully only a few immigrate into the edges of commercial orchards.",
                               'management': "Initial pesticide treatments should be applied as soon as trap catches exceed recommended threshold levels (<a href='http://nysipm.cornell.edu/publications/apple_man/files/am.pdf' target='_blank'>average 5 flies/trap</a>).  If orchard has no previous history of damage and is not located near any major source of outside AM infestation, spraying orchard perimeters may be sufficient.  If trap catches are high and orchard is near outside sources, spray the whole orchard or more perimeter rows." ,
                               'pesticide_link': "http://www.dec.ny.gov/nyspad/products?0" },
2: { 'datelo':(8,1,0), 'datehi':(8,15,23), 'altref': ["Post_2"],
							   'stage': "Adults move into orchards, eggs laid",
                               'status': "Previous studies have shown that August 1-15 is the time period when the most AM flies immigrate into commercial orchards, although flies can be trapped in late June and into September and early October.",
                               'management': "After 10-14 days have elapsed since the first AM treatment (estimated period of residual effectiveness of insecticides), continue to check AM traps and apply additional sprays when trap catches exceed the threshold.  Perimeter sprays can be used for low pressure orchards.  In high pressure orchards, after the first spray is applied, continue to apply sprays to a larger perimeter area.  Repeat monitoring protocol and apply additional sprays as necessary  to provide protection until at least September 1." ,
                               'pesticide_link': "http://www.dec.ny.gov/nyspad/products?0" },
3: { 'datelo':(8,16,0), 'datehi':(12,31,23), 'altref': ["Post_3"],
							   'stage': "Adults flying, few eggs laid",
                               'status': "In warm fall seasons AM may be captured in September and October until the first frost.  Studies in western NY have shown that usually no damage results from these late season infestations as long as fruit has been protected until at least the first of September.",
                               'management': "AM treatments are not usually recommended after September 1, particularly in earlier maturing apple cultivars.  Sprays may be recommended in September in late season maturing cultivars if AM damage has been noted in fruit during late season inspections or if the orchard is located near an outside source of AM infestation and if the orchard has a past history of AM damage." } } }