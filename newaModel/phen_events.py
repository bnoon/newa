#for each event the tuple is (mean degree day accumulation, standard deviation, min and max)
phen_events_dict = {'macph_dormant_43':      { 'dd': (  0,   0,   0,   0), 'name': 'Dormant'},
					'macph_st_43':           { 'dd': (102,  23,  75, 140), 'name': 'Silver Tip'},
					'macph_greentip_43':     { 'dd': (147,  32, 101, 196), 'name': 'Green Tip'},
					'macph_halfgreen_43':    { 'dd': (203,  27, 165, 242), 'name': 'Half-Inch Green'},	  #apple-oblr
					'macph_tightcluster_43': { 'dd': (258,  32, 199, 297), 'name': 'Tight Cluster'},
					'macph_pink_43':         { 'dd': (325,  22, 290, 366), 'name': 'Pink Bud'},			  #apple-oblr, pc
					'macph_firstblossom_43': { 'dd': (328,  51, 230, 440), 'name': 'First Blossom'},
					'macph_bloom_43':        { 'dd': (422,  38, 346, 479), 'name': 'Bloom'},			  #apple-oblr, pc
					'macph_pf_50':           { 'dd': (258,  26, 210, 303), 'name': 'Petal Fall'},		  #apple-oblr, pc
					'macph_pf_43':           { 'dd': (518,  37, 454, 580), 'name': 'Petal Fall'},		  #apple-oblr, pc
					'macph_fruitset_43':     { 'dd': (581,  35, 522, 626), 'name': 'Fruit Set'},
					'oblr_catch1_43':        { 'dd': (893,  88, 750,1212), 'name': 'First Trap Catch'},	  #apple-oblr
					'stlm_catch1_43':        { 'dd': (165,  50,  81, 274), 'name': 'First Trap Catch'},	  #apple-stlm
					'cm_catch1_43':			 { 'dd': (591, 116, 421, 801), 'name': 'First Trap Catch'},   #apple-cm
					'cm_catch1_50':			 { 'dd': (256,  53, 168, 404), 'name': 'First Trap Catch'},   #apple-cm
					'ofm_catch1_43':		 { 'dd': (274,  52, 173, 378), 'name': 'First Trap Catch'},	  #apple-ofm
					'sjs_catch1_50':		 { 'dd': (279,  61, 145, 385), 'name': 'First Trap Catch'},	  #apple-sjs
					'am_catch1_50':			 { 'dd': (934, 138, 730,1297), 'name': 'First Trap Catch'},	  #apple-maggot
					'am_catch1_43':			 { 'dd': (1645,215,1335,2116), 'name': 'First Trap Catch'},	  #apple-maggot
					'gbm_bloom_50':			 { 'dd': (-999,-999,182, 450), 'name': 'Wild Grape Bloom'} }  #grape-gbm
