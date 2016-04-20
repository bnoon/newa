pest_status_management = { 
'pest_name': "Plum Curculio",
'biofix_phenology' : "Petal Fall",
'biofix_abbrev': "pc",
'basetemp': 50,

'pre_biofix': {
0: { 'ddlo':   0, 'ddhi': 149, 'altref': ["Dormant","Silver_Tip","Green_Tip","Half-Inch_Green","Tight_Cluster"],
							   'stage': "Adults still overwintering", 
                               'status': "No <a href='http://nysipm.cornell.edu/factsheets/treefruit/pests/pc/pc.asp' target='_blank'>plum curculio</a> activity at this time.", 
                               'management': "No control measures are recommended at this time because most adults have not yet emerged and will escape residual effectiveness of most insecticides." },
1: { 'ddlo': 150, 'ddhi': 165, 'altref': "Pink_Bud",
							   'stage': "Adults move into orchards", 
                               'status': "<a href='http://nysipm.cornell.edu/factsheets/treefruit/pests/pc/pc_fig1.asp' target='_blank'>Adults</a> usually emerge from overwintering quarters during the pink bud state of apples and begin to immigrate into the edges of commercial orchards.",
                               'management': "No control measures are recommended at this time because fruit has not yet begun to develop and reach a susceptible stage for injury from plum curculio adults." },
2: { 'ddlo': 166, 'ddhi': 230, 'altref': "Bloom",
							   'stage': "Adults in apple trees",
                               'status': "Adults can be present in apple trees during bloom but do not begin to feed on or oviposit in fruit until petal fall.",
                               'management': "No control measures are recommended at this time because fruit has not yet begun to develop and reach a susceptible stage for injury from plum curculio adults." },
3: { 'ddlo': 231, 'ddhi': 303, 'altref': ["Petal_Fall"],
							   'stage': "Adults ovipositing",
                               'status': "At petal fall, fruit becomes susceptible to <a href='http://nysipm.cornell.edu/factsheets/treefruit/pests/pc/pc_fig4.asp' target='_blank'> fruit injury</a> from plum curculio adults.  The adults may damage fruit directly by feeding or females may oviposit in the developing apples.",
                               'management': "Apply a control spray of a broad spectrum insecticide at petal fall to control any plum curculio adults that may be present in the orchard.  Sprays applied at this time may also help control internal Lepidoptera, European apple sawfly, and the first generation of white apple leafhoppers and spotted tentiform leafminers.",
                               'pesticide_link': "http://treefruitipm.info/PesticidesForPest.aspx?PestID=28&GrowthStageID=11"} },
'post_biofix': {  
0: { 'ddlo':   0, 'ddhi': 200, 'altref': ["Post_0"],
							   'stage': "Adults ovipositing",
                               'status': "Plum curculio (PC) adults will continue to damage fruit (<a href='http://nysipm.cornell.edu/factsheets/treefruit/pests/pc/pc_fig8.asp' target='_blank'>example 1</a>, <a href='http://nysipm.cornell.edu/factsheets/treefruit/pests/pc/pc_fig6.asp' target='_blank'>example 2</a>) and may be moving among trees. PC activity is highly dependent upon temperatures, particularly at night when adults are most active.  PC usually do not feed or oviposit when nighttime temperatures are below 50 deg F.   If the weather is extremely warm after petal fall, the oviposition cycle may be completed in 2 weeks.  In cooler seasons, PC may continue to oviposit for 4-6 weeks.",
                               'management': "A petal fall spray should control plum curculio (PC) for about 10-14 days.  Incidence of observed PC damage is highly variable among different orchards.  PC damage usually occurs primarily along the edges of commercial orchards, and noticeable damage occurs in the same locations in orchards year after year, regardless of treatment levels.  Therefore, the potential for damage in any particular orchard can be predicted from past observations.  Usually, a post-petal fall spray for control of PC is not necessary in low-pressure orchards in which no damage has been observed in the past.  In high-pressure orchards, additional sprays along the perimeter of the orchards should be applied until the oviposition model predicts that control is no longer necessary.",
                               'pesticide_link': "http://treefruitipm.info/PesticidesForPest.aspx?PestID=28&GrowthStageID=12"},
1: { 'ddlo': 201, 'ddhi': 308, 'altref': ["Post_1"],
							   'stage': "Adult oviposition decreasing", 
                               'status': "Plum curculio activity is beginning to decline and any curculio remaining in trees will usually not move to other locations.",
                               'management': "Plum curculio only need to be controlled until 308 DD have accumulated after petal fall.  Make sure that the predicted residual coverage (10-14 days) from the last spray will protect fruit until DD accumulation reaches this value.",
                               'pesticide_link': "http://treefruitipm.info/PesticidesForPest.aspx?PestID=28&GrowthStageID=12" }, 
2: { 'ddlo': 309, 'ddhi': 407, 'altref': ["Post_2"],
							   'stage': "Adults stop ovipositing",
                               'status': "Plum curculio immigration into orchards is over for the season.", 
                               'management': "Plum curculio control sprays are no longer necessary during the rest of the season." },
3: { 'ddlo': 408, 'ddhi':9999, 'altref': ["Post_3"],
							   'stage': "Adults inactive",
                               'status': "Plum curculio oviposition is over.",
                               'management': "Plum curculio control sprays are no longer necessary." } } }