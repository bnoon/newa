pest_status_management = { 
'pest_name': "Slugs",
'time_concern': ["Pre plant","Seedling through mature head","Post harvest"],
'keychar_oc': "<i>Slugs</i><p><b>Key Characteristics: </b>",
'keychar_o':  "Adult slugs are between one and two inches in length. Slugs can overwinter at any stage of development. Although slugs cannot survive prolonged subzero temperatures or desiccation, the burrows of small mammals and worms provide them protection. Slugs begin to move, hatch, feed, and lay eggs in the spring when temperatures are consistently above 40&deg;F. There is often little or no slug activity in the field during periods of dry weather; however, extensive feeding may persist in damp areas.</p> <p><b>Relative risk:</b> Slugs are a particular problem in wet periods during the spring and fall. Their feeding can kill seedlings in the spring. During the season, they feed on mature leaves and heads. Slugs and their droppings can cause contamination at harvest.</p>",
'keychar_c':  "Adult slugs are between one and two inches in length. Slugs can overwinter at any stage of development. Although slugs cannot survive prolonged subzero temperatures or desiccation, the burrows of small mammals and worms provide them insulation. Slugs begin to move, hatch, feed, and lay eggs in the spring when temperatures are consistently above 40&deg;F. There is often little or no slug activity in the field during periods of dry weather; however, there may be extensive feeding in damp areas.</p> <p><b>Relative risk:</b> Slugs are a particular problem in wet periods during the spring and fall. Their feeding can kill seedlings in the spring. During the season, they feed on mature leaves and heads. Slugs and their droppings can cause contamination at harvest.</p>",
'help_links': [("Pictures of slug life cycle", "http://web.entomology.cornell.edu/shelton/veg-insects-ne/pests/slugs.html"),
("Slug damage", "http://web.entomology.cornell.edu/shelton/veg-insects-ne/damage/slugs_crops.html")],
'messages': {
'Pre plant':             { 'datelo': (1,1,0), 'datehi': (4,14,23),
                           'status': "Slugs are overwintering in the soil.",
                           'management_oc': "Practices that help dry the soil surface (e.g. conventional tillage and good weed control) will reduce slug populations.",                          
                           'management_o': "",
                           'management_c': ""},
'Seedling through mature head': { 'datelo': (4,15,0), 'datehi': (11,14,23),
                           'status': "Slugs emerge from soil, look for hosts and feed on crop.",
                           'management_oc': "",
                           'management_o': "Scouting - Record the occurrence and severity of slug damage. No thresholds have been established. <p>If spraying is necessary choose from: Sluggo Ag.</p>",
                           'management_c': "Scouting - Record the occurrence and severity of slug damage. No thresholds have been established. <p>If spraying is necessary choose from:  Deadline Bullets.</p> <p>Insecticide resistance management - A classification of insecticides based on their mode of action is available in pdf format. This guide can be used to help avoid or delay the development of insecticide resistance, as well as manage populations that have developed resistance to a particular insecticide. <br /> <ul><li><a href='http://nysipm.cornell.edu/publications/res_mgmt/files/res_mgmt.pdf' target='_blank'>Classification of insecticides and acaracides for resistance management</a></li></ul></p>"},
'Post harvest':          { 'datelo': (11,15,0), 'datehi': (12,31,23),
                           'status': "na",
                           'management_oc': "No management techniques.",
                           'management_o': "",
                           'management_c': ""}
} }