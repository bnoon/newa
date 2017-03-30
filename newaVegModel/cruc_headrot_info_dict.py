pest_status_management = { 
'pest_name': "Head Rot of Broccoli",
'time_concern': ["Pre plant","Seedling through harvest","Post harvest"],
'keychar_oc': "<i>Pseudomonas spp.</i><p><b>Key Characteristics: </b>",
'keychar_o':  "Head rot begins as water-soaked florets that become malodorous and soft-rotted if head maturation coincides with periods of prolonged wet weather. The bacterium is most serious in broccoli but can affect other brassica crops. Soft rot will continue to develop in the low temperatures of storage facilities.</p> <p><b>Relative risk:  </b>A sporadic problem in wet weather.</p>",
'keychar_c':  "Head rot begins as water-soaked florets that become malodorous and soft-rotted if head maturation coincides with periods of prolonged, wet weather.</p> <p><b>Relative risk:  </b>A sporadic problem in wet weather.</p>",
'help_links': [("Photo gallery of broccoli head rot", "http://vegetablemdonline.ppath.cornell.edu/PhotoPages/Crucifers/SoftRot/Cru_SftRtPhotoList.htm"), ("Cornell article on managing bacterial rot", "http://vegetablemdonline.ppath.cornell.edu/NewsArticles/BacterialRot.htm")],
'messages': {
'Pre plant':             { 'datelo': (1,1,0), 'datehi': (4,14,23),
                           'status': "<i>Pseudomonas spp. </i>may be in soil or crop or cruciferous weed debris.",
                           'management_oc': "Varieties like Shogun, Green Defender, and Pirate that have tight, dome-shaped heads with very small beads are less susceptible to head rot than other varieties but may be lacking in other horticultural qualities. Check <a href='http://www.nysaes.cals.cornell.edu/recommends/15cabbage.html' target='_blank'>Tables 15.1.1 and 15.1.2 Recommended Varieties</a> to view resistant varieties. <ul><li><a href='http://vegetablemdonline.ppath.cornell.edu/Tables/BroccoliTable.html' target='_blank'>Broccoli:  disease resistant varieties</a></ul>",                          
                           'management_o': "Crop Rotation -Maintain a minimum of 2 years without cruciferous crops, cover crops (e.g. mustard, radish, rapeseed) or weeds (e.g. wild radish, wild mustard, shepherds purse).  <ul><li><a href='http://calshort-lamp.cit.cornell.edu/bjorkman/covercrops/index.php' target='_blank'>Why use cover crops in vegetable rotations?</a> <li><a href='http://vegetablemdonline.ppath.cornell.edu/NewsArticles/McNabRotations.htm' target='_blank'>Crop roatation information</a></ul> <p>Site selection - Select fields away from hedgerows or woods that impede air flow and prevent leaves from drying quickly.</p> <p>Seed treatment: The bacteria are not seed-borne therefore seed treatments are not useful.</p> <p>Harvest - Clean all tools used during harvest. Avoid entering fields when plants are wet. Harvest when heads are tight. Cut stalks at an angel to minimize the chance the stump will provide a place for the pathogen to invade and produce inoculum for near-by healthy heads.</p>",
                           'management_c': "Crop rotation - Minimum two years without cruciferous crops or cruciferous weeds which include wild radish and wild mustard. <p>Site selection - Select land with good air movement and favorable soil moisture.</p> <p>Sanitation - Clean all tools used during harvest. Avoid entering fields when plants are wet.</p>"},
'Seedling through harvest': { 'datelo': (4,15,0), 'datehi': (11,14,23),
                           'status': "<i>Pseudomonas spp. </i>may be splashed from soil in wet weather and infect plants.",
                           'management_oc': "",
                           'management_o': "Scouting - Monitor for presence of head rot at harvest to prevent marketing of infected broccoli.",
                           'management_c': "Scouting - Record the occurrence and severity of head rot. No thresholds have been established. <p>No pesticides are available to manage this disease.</p>"},
'Post harvest':          { 'datelo': (11,15,0), 'datehi': (12,31,23),
                           'status': "<i>Pseudomonas spp. </i>may be in soil or crop or cruciferous weed debris.",
                           'management_oc': "",
                           'management_o': "Postharvest - Crop debris should be destroyed as soon as possible to reduce future inoculum and initiate decomposition.",
                           'management_c': "Crop debris should be destroyed as soon as possible to remove this source of disease for other plantings and to initiate decomposition."}
} }