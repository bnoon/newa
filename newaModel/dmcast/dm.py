# ----------------------------------------
# dmc.py
# ----------------------------------------
# imports
# ----------------------------------------
import ctypes as C
import sys
import array
import get_weather
import dm_cultivars
from print_exception import print_exception

# ----------------------------------------
# Definitions
# ----------------------------------------
_dmC  = C.cdll.LoadLibrary("/home/lje5/programs/DMCast/DMCast-Source/libdmc.so")


retCode = _dmC.setup_dm()
print 'leaving' 
