# Apple Growth Model

#!/usr/bin/env python

# Change log
# 2013-06-07: Bug fixes, including below-zero GDD bug from Jim Meyers (NEWA 6/10/2013)

import sys, collections, array
from math import sin, pi, exp
from mx import DateTime
if '/Users/keith/kleWeb/newaTools/newaTools/Apple_Thinning_Model' not in sys.path: sys.path.insert(1,'/Users/keith/kleWeb/newaTools/newaTools/Apple_Thinning_Model')
from NewaWeatherData import WeatherData

FALSE = 0
TRUE = 1

# Global Model Parameters

# Parameters concerning geographical location

pLatitude =                     43
pHemiFactor =                   283

# Parameters concerning phenological development

pDayBudBreak =                  105     # Ordinal date of budbreak; default, modified in _init_ - KLE

# Values concerning ecophysiological relationships

pCanopyLightExtinction =        0.42
pFmax =                         0.7     # Net photosynthetic rate
pLongShootCount =               194     # Final number of long shoots as an average for our Standard Empire/M9 tree
pNumSpurs =                     686     # Number of short shoots (fruiting and non-fruiting spurs and lateral short shoots) on the standard Empire/M9 trees.
pChillAccumulatorThreshold =    600
pChillAccumulatorOffset =       5
pAreaPerTree =                  5.1     # Area per tree=5.1 m2 based on the standard Empire/M9, Slender Spindle, mature orchard, 14 y-old, spacing:1.5m within row*3.4m between rows, 1957 tr/ha, 5.1m2/tr, mature tree height=2.5 m  (Wunsche, J.'s Ph.D. Dissertation)
pTempCoeffOfLeafResp =          0.069   # k=Temperature coefficient of leaf respiration (the slope of lnLeafResp versus Temperature); 0.069 gives a standard Q10=2
pTempCoeffOfWoodResp =          0.069   # k=Temperature coefficient of wood respiration (the slope of lnWoodResp versus Temperature)
pVegDryMatterToCO2 =            0.55    # Cost of construction of vegetative tissue (g DM per g of fixed CO2)
pLightEffectOnResp =            0.75    # The effect of light exposure of the fruit on respiration is estimated, averaged over the crop, to reduce fruit respiration rate by 25% compared to the dark respiration rates used in the main calculation of fruit respiration.  Based on data of Bepete et al (1997 Acta Hort 451)
pRelSinkStrengthRoot =          0.005
pRelSinkStrengthWood =          0.015
pRelSinkStrengthFruit =         0.05
pRelSinkStrengthShoot =         0.93
pIsAccCO2Biflow     =           FALSE
pIsDailyCarbonBalBiflow =       FALSE

# Parameters related to growth estimates

pInitialFruitCount =            300
pInitialFruitWeight =           0.1
pDisableAbscissionModel =       TRUE


# Response Curves

soilTempModelX = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
soilTempModelY = [9, 11.5, 13.4, 15, 17.2, 18.8, 21, 22, 23, 24, 24]

fractGrowingShModelX = [0,50,100,150,200,250,300,350,400,450,500,550,600,650,700,750,800,850,900,950,1000]
fractGrowingShModelY = [0.5,0.825,0.98,0.995,1,1,0.995,0.95,0.905,0.83,0.75,0.66,0.56,0.425,0.3,0.2,0.145,0.075,0.045,0,0]

fractGrowingSpurModelX = [0,50,100,150,200,250,300,350,400,450,500,550,600,650,700,750,800,850,900,950,1000]
fractGrowingSpurModelY = [0.405,1,1,0.565,0,0.69,0.995,0.91,0.7,0.19,0,0,0,0,0,0,0,0,0,0,0]

leafAbscissionModelX = [0,50,100,150,200,250,300,350,400,450,500]
leafAbscissionModelY = [0,1,1,1,1,1,1,1,1,1,1]

pMaxModelX = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200]
pMaxModelY = [0.00024600,0.00025980,0.00027360,0.00028740,0.00030120,0.00031500,0.00032880,0.00034260,0.00035640,0.00037020,0.00038400,0.00040260,0.00042120,0.00043980,0.00045840\
              ,0.00047700,0.00049560,0.00051420,0.00053280,0.00055140,0.00057000,0.00058200,0.00059400,0.00060600,0.00061800,0.00063000,0.00064200,0.00065400,0.00066600,0.00067800,\
              0.00069000,0.00069600,0.00070200,0.00070800,0.00071400,0.00072000,0.00072600,0.00073200,0.00073800,0.00074400,0.00075000,0.00075000,0.00075000,0.00075000,0.00075000,\
              0.00075000,0.00075000,0.00075000,0.00075000,0.00075000,0.00075000,0.00075000,0.00075000,0.00075000,0.00075000,0.00075000,0.00075000,0.00075000,0.00075000,0.00075000,\
              0.00075000,0.00075050,0.00075100,0.00075150,0.00075200,0.00075250,0.00075300,0.00075350,0.00075400,0.00075450,0.00075500,0.00075500,0.00075500,0.00075500,0.00075500,\
              0.00075500,0.00075500,0.00075500,0.00075500,0.00075500,0.00075500,0.00075500,0.00075500,0.00075500,0.00075500,0.00075500,0.00075500,0.00075500,0.00075500,0.00075500,\
              0.00075500,0.00075450,0.00075400,0.00075350,0.00075300,0.00075250,0.00075200,0.00075150,0.00075100,0.00075050,0.00075000,0.00074850,0.00074700,0.00074550,0.00074400,\
              0.00074250,0.00074100,0.00073950,0.00073800,0.00073650,0.00073500,0.00073500,0.00073500,0.00073500,0.00073500,0.00073500,0.00073500,0.00073500,0.00073500,0.00073500,0.00073500,\
              0.00073500,0.00073500,0.00073500,0.00073500,0.00073500,0.00073500,0.00073500,0.00073500,0.00073500,0.00073500,0.00073500,0.00073500,0.00073500,0.00073500,0.00073500,0.00073500,0.00073500,\
              0.00073500,0.00073500,0.00073500,0.00073500,0.00073500,0.00073500,0.00073500,0.00073500,0.00073500,0.00073500,0.00073500,0.00073500,0.00073500,0.00073450,0.00073400,0.00073350,\
              0.00073300,0.00073250,0.00073200,0.00073150,0.00073100,0.00073050,0.00073000,0.00073000,0.00073000,0.00073000,0.00073000,0.00073000,0.00073000,0.00073000,0.00073000,0.00073000,\
              0.00073000,0.00072650,0.00072300,0.00071950,0.00071600,0.00071250,0.00070900,0.00070550,0.00070200,0.00069850,0.00069500,0.00068800,0.00068100,0.00067400,0.00066700,0.00066000,\
              0.00065300,0.00064600,0.00063900,0.00063200,0.00062500,0.00061100,0.00059700,0.00058300,0.00056900,0.00055500,0.00054100,0.00052700,0.00051300,0.00049900,0.00048500]

photoChemEffModelX = [0,10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,230,240,250,260,270,280,290]
photoChemEffModelY = [2.00,2.625,3.225,3.825,8.00,8.00,8.00,8.00,8.00,8.00,8.00,8.00,8.00,8.00,8.00,8.00,7.680,7.200,5.640,4.38,3.18,1.92,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00]

dryMatterToFWModelX = [0,200,300,400,500,600,700,800,900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000,2100,2200,2300,2400]
dryMatterToFWModelY = [6.667,6.667,8.696,9.09,8.55,8.333,8,7.9,7.8,7.692,7.6,7.5,7.45,7.407,7.24,7.143,7.02,6.9,6.897,6.67,6.67,6.67,6.67,6.67]

fruitMaxGrowthRateModelX = [0,10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200]
fruitMaxGrowthRateModelY = [0.01,0.01,0.01,0.02,0.075,0.29,0.9,1.25,1.52,1.77,1.88,1.98,2,2,2,2,2,2,2,2,2]

fruitCarbonDryMatterModelX = [0,10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200]
fruitCarbonDryMatterModelY = [0.5,0.5,0.5,0.5,0.5,0.535,0.57,0.6,0.645,0.68,0.68,0.68,0.68,0.68,0.68,0.68,0.68,0.68,0.68,0.68,0.68]

abscissionModelX = [0,10,20,30,40,50,60,70,80,90,100]
abscissionModelY = [1,1,0.9,0.64,0.425,0.2,0.035,0,0,0,0]

handHarvestModelX = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200,201,202,203,204,205,206,207,208,209]
handHarvestModelY = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

fruitTempGrowthModelX = [0,5,10,15,20,25,30,35,40]
fruitTempGrowthModelY = [0.001,0.2,0.4,0.6,0.8,1,1,1,1]

woodSurfaceAreaModelX = [0,18,36,54,72,90,108,126,144,162,180]
woodSurfaceAreaModelY = [1.17,1.18,1.20,1.28,1.42,1.45,1.47,1.50,1.50,1.50,1.50]

leafTempRespRateModelX = [0,18,36,54,72,90,108,126,144,162,180]
leafTempRespRateModelY = [0.025,0.025,0.024,0.021,0.015,0.008,0.007,0.006,0.006,0.006,0.006]

woodTempRespModelX = [0,18,36,54,72,90,108,126,144,162,180]
woodTempRespModelY = [0.005,0.010,0.007,0.006,0.006,0.006,0.005,0.005,0.005,0.004,0.004]

tempIntFruitModelX = [0,10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,230,240,250,260,270,280,290]
tempIntFruitModelY = [0.01,0.0101,0.01,0.0098,0.0091,0.008,0.0061,0.0039,0.002,0.001,0.0007,0.0007,0.0007,0.0007,0.0007,0.0007,0.0007,0.0007,0.0007,0.0007,0.0007,0.0007,0.0007,0.0007,0.0007,0.0007,0.0007,0.0007,0.0007,0.0007]

tempSlopeFruitModelX = [0,18,36,54,72,90,108,126,144,162,180]
tempSlopeFruitModelY = [0.1,0.099,0.097,0.092,0.080,0.060,0.055,0.055,0.055,0.055,0.055]

fruitDMtoCO2ModelX = [0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100]
fruitDMtoCO2ModelY = [0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.52,0.545,0.57,0.6,0.62,0.635,0.655,0.67,0.68,0.68,0.68]

shootExtGrowthModelX = [0,10,20,30,40,50,60,70,80,90,100]
shootExtGrowthModelY = [0,156,200,200,200,200,180,116,43,13,0]

shootGrowthPerExtModelX = [0,4,8,12,16,20,24,28,32,36,40,44,48,52,56,60,64,68,72,76,80,84,88,92,96,100]
shootGrowthPerExtModelY = [0.02,0.02,0.021,0.022,0.029,0.04,0.056,0.12,0.145,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.2,0.2,0.2,0.2,0.2]

rootTempGrowthModelX = [0,5,10,15,20,25,30,35,40]
rootTempGrowthModelY = [0.1,0.18,0.25,0.36,0.5,0.71,1,1,1]

spurGrowthModelX = [0,10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200]
spurGrowthModelY = [0.02,0.023,0.027,0.032,0.042,0.055,0.065,0.081,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]

miscTempEffectModelX = [0,5,10,15,20,25,30,35,40]
miscTempEffectModelY = [0,0.11,0.28,0.5,0.73,1,1.4,2,2]

class ColumnCell:
    cellValue = ''
    isEmpty = TRUE

    def __init__(self):
        return

    def isInitialized(self):
        return self.isEmpty

    def setValue(self, value):
        try:
            self.cellValue = value
            self.isEmpty = FALSE
        except:
            raise

    def getValue(self):
        return self.cellValue



class SpreadsheetColumn:
    columnName = 'NoName'
    columnCells = {}
    dependencies = {}
    formulas = {}
    evalOrder = 0
    excludeFirstRowDep = FALSE

    def __init__(self,name):
        self.columnName = name
        return
    
    def setEvalOrder(self, num):
        self.evalOrder = num
        return

    def setDependencies(self,dependentOnName):
        self.dependencies = dependentOnName
        return self
    
    def excludeFirstRowDependencies(self):
        self.excludeFirstRowDep = TRUE
        return self
    
    def numUnresolvedDependencies(self, rowNum):
        theList = self.dependencies
        if len(theList) == 0:
            return 0
        elif (self.excludeFirstRowDep == TRUE and rowNum == 0):
            return 0
        else:
            numHits = 0
            for item in theList:
                try:
                    refCell = self.columnCells[item,rowNum]
                    if refCell.isEmpty == TRUE:
                        numHits = numHits + 1
                except KeyError:
                        numHits = numHits + 1
                    
            return numHits
    
    def row(self,rowNum):
        try:
            self.columnCells[self.columnName,rowNum]
        except KeyError:
            self.columnCells[self.columnName,rowNum] = ColumnCell()

        finally:
            return self.columnCells[self.columnName, rowNum]

    def setFormula(self, formula, rowNum):
        # Use -1 for global column formula and override individual cells
        self.formulas[self.columnName,rowNum] = formula
        return self

    def getFormula(self, rowNum):
        try:
            formula = self.formulas[self.columnName,rowNum]
        except KeyError:
            try:
                formula = self.formulas[self.columnName,-1]
            except:
                formula = str(self.columnCells[self.columnName, rowNum].getValue())

        finally:
            return formula


class Spreadsheet:
    columns = {}
    evalOrder = 0


    def __init__(self):
        return

    def addColumn(self,columnName):
        newColumn = SpreadsheetColumn(columnName)
        self.columns[columnName] = newColumn
        return self.columns[columnName]

    def column(self,colName):
        return self.columns[colName]

    def refCell(self,columnName, rowNum, offset):
        return self.column(columnName).row(rowNum+offset).getValue()
    
    def getCellValues(self):
        rtnDict = {}
        for col in self.columns:
            try:
                aCol = self.columns[col]
                for aCell in aCol.columnCells:
                    colName = aCell[0]
                    rowNum = aCell[1]
                    rtnDict[colName, rowNum] = self.column(colName).row(rowNum).getValue()
                return rtnDict
            except:
                pass
        return rtnDict
    
    def sf_IF(self, pEval, pIfYes, pIfNo):
        if pEval == TRUE:
            return pIfYes
        else:
            return pIfNo
        return
    
    def sf_AND(self, p1, p2):
        if p1 == TRUE and p2 == TRUE:
            return TRUE
        else:
            return FALSE
        
    def sf_NOT(self, p1):
        if p1 == FALSE:
            return TRUE
        else:
            return FALSE
        
    def sf_MAX(self, p1, p2):
        return max(p1,p2)

    def interpolateResponse(self, modelX, modelY, targetX):
            
        # Perform linear interpolation on XY set
            
        lenX = len(modelX)
        lenY = len(modelY)
            
        if lenX <> lenY:
            raise
        
        lowXindex = 0            
        for xLo in range(0,lenX):
            if modelX[xLo] <= targetX:
                lowXindex = xLo
            
        highXindex = lenX-1
        for xHi in range(lenX-1,-1,-1):
            if modelX[xHi] >= targetX:
                highXindex = xHi
                
            
        lowXval = modelX[lowXindex]
        highXval = modelX[highXindex]
        lowYval = modelY[lowXindex]
        highYval = modelY[highXindex]
        
        if highXindex == lowXindex:
            interpolatedY = highYval
        else:
        
            interpolationRangeX = float(highXval - lowXval)
            interpolationOffsetX = float(targetX - lowXval)
            interpolationOffsetPctX = float(interpolationOffsetX / interpolationRangeX)
        
            interpolationRangeY = float(highYval - lowYval)
            interpolationOffsetY = float(interpolationRangeY * interpolationOffsetPctX)
        
            interpolatedY = lowYval + interpolationOffsetY
            
        return interpolatedY
    

    def evaluate(self, numRows):
        
        #Evaluate
        for rowIndex in range(0,numRows):
                
            localColumns = []
            for col in self.columns:
                if self.column(col).row(rowIndex).isEmpty == TRUE:
                    localColumns.append(col)
                
            while len(localColumns) > 0:
                for col in localColumns:
                    if self.column(col).numUnresolvedDependencies(rowIndex) == 0:
                        try:
                            y = eval(self.column(col).getFormula(rowIndex))
                        except:
                            raise
                        self.columns[col].row(rowIndex).setValue(y)
                localColumns = []
                for col in self.columns:
                    if self.column(col).row(rowIndex).isEmpty == TRUE:
                        localColumns.append(col)
                
        return


class AppleGrowthModel:

    weatherData = ''
    spreadsheet = Spreadsheet()
    

    def __init__(self, wxDataArray, budBreak):

#		changed by KLE to receive and pass array to WeatherData, rather than filename
        self.weatherData = WeatherData(wxDataArray)

#       this was originally hard-coded as 105; added refinement here - KLE
        global pDayBudBreak
        pDayBudBreak = int((budBreak - DateTime.DateTime(budBreak.year, 1, 1)).days + 1)

#		initialize everything - KLE
        self.spreadsheet.columns = {}
        self.spreadsheet.evalOrder = 0
        SpreadsheetColumn.columnCells = {}
        SpreadsheetColumn.dependencies = {}
        SpreadsheetColumn.formulas = {}
        SpreadsheetColumn.evalOrder = 0
        SpreadsheetColumn.excludeFirstRowDep = FALSE
        
        # Weather (physical])
        self.spreadsheet.addColumn('TimeInterval')
        
        self.spreadsheet.addColumn('DayLength')\
        .setDependencies(['TimeInterval'])\
        .setFormula("43600+exp(7.42+0.045*pLatitude)*(sin(2*pi*(pDayBudBreak+self.refCell('TimeInterval',rowIndex,0)+pHemiFactor)/365))",-1)
        
        self.spreadsheet.addColumn('TempMin')
        
        self.spreadsheet.addColumn('TempMax')
        
        self.spreadsheet.addColumn('TempMean')\
        .setDependencies(['TempMin', 'TempMax'])\
        .setFormula("(self.refCell('TempMin', rowIndex, 0)+self.refCell('TempMax', rowIndex, 0))/2",-1)
        
        self.spreadsheet.addColumn('DailyRad')
        
        self.spreadsheet.addColumn('TotalPAR')\
        .setDependencies(['DailyRad'])\
        .setFormula("self.refCell('DailyRad',rowIndex,0)/2",-1)
        
        self.spreadsheet.addColumn('SoilTemp')\
        .setFormula("self.interpolateResponse(soilTempModelX, soilTempModelY, self.refCell('TimeInterval',rowIndex,0))",-1)
        
        #Weather (physiological)
        self.spreadsheet.addColumn('GDDs')\
        .setDependencies(['TempMin', 'TempMax'])\
        .setFormula("self.sf_MAX(0,(self.refCell('TempMin',rowIndex,0) + self.refCell('TempMax',rowIndex,0))/2-4)",-1)
        
        self.spreadsheet.addColumn('AccDegDays')\
        .setFormula("0",0)\
        .setFormula("self.refCell('GDDs',rowIndex,-1) + self.refCell('AccDegDays',rowIndex,-1)",-1)
        
        self.spreadsheet.addColumn('AccChill')\
        .setDependencies(['AccDegDays', 'TempMin'])\
        .setFormula("self.sf_IF(self.sf_AND(self.refCell('AccDegDays',rowIndex,0)>pChillAccumulatorThreshold,(pChillAccumulatorOffset-self.refCell('TempMin',rowIndex,0))>0),pChillAccumulatorOffset-self.refCell('TempMin',rowIndex,0),0)",-1)
        
        self.spreadsheet.addColumn('AccTmin5')\
        .setFormula("0",0)\
        .setFormula("self.refCell('AccTmin5',rowIndex,-1) + self.refCell('AccChill',rowIndex,-1)",-1)
        
        #Leaf area development (shoots)
        self.spreadsheet.addColumn('FractGrwngShoots')\
        .setDependencies(['AccDegDays'])\
        .setFormula("self.interpolateResponse(fractGrowingShModelX, fractGrowingShModelY, self.refCell('AccDegDays',rowIndex,0))",-1)
        
        self.spreadsheet.addColumn('NumGrwngShoots')\
        .setDependencies(['FractGrwngShoots'])\
        .setFormula("self.refCell('FractGrwngShoots',rowIndex,0) * pLongShootCount",-1)
        
        #Leaf area development (spurs)
        self.spreadsheet.addColumn('FractGrwngSpurs')\
        .setDependencies(['AccDegDays'])\
        .setFormula("self.interpolateResponse(fractGrowingSpurModelX, fractGrowingSpurModelY, self.refCell('AccDegDays',rowIndex,0))",-1)
        
        self.spreadsheet.addColumn('NumGrwngSpurs')\
        .setDependencies(['FractGrwngSpurs'])\
        .setFormula("pNumSpurs * self.refCell('FractGrwngSpurs',rowIndex,0)",-1)
        
        #Leaf area development (leaves)
        self.spreadsheet.addColumn('DailySpurLeafAreaInc')\
        .setDependencies(['AccDegDays', 'GDDs', 'NumGrwngSpurs'])\
        .setFormula("self.sf_IF(self.refCell('AccDegDays',rowIndex,0)<200,(0.00002*self.refCell('GDDs',rowIndex,0)*self.refCell('NumGrwngSpurs',rowIndex,0)),(0.00004*self.refCell('GDDs',rowIndex,0)*self.refCell('NumGrwngSpurs',rowIndex,0)))",-1)
        
        self.spreadsheet.addColumn('DailyExtShtLAInc')\
        .setDependencies(['AccDegDays', 'GDDs', 'NumGrwngShoots'])\
        .setFormula("self.sf_IF(self.refCell('AccDegDays',rowIndex,0)>100,(0.00007*self.refCell('GDDs',rowIndex,0))*self.refCell('NumGrwngShoots',rowIndex,0),(0.00004*self.refCell('GDDs',rowIndex,0))*self.refCell('NumGrwngShoots',rowIndex,0))",-1)
        
        self.spreadsheet.addColumn('AccTotLeafArea')\
        .setFormula("0",0)\
        .setFormula("self.refCell('AccTotLeafArea',rowIndex,-1)+self.refCell('DailySpurLeafAreaInc',rowIndex,-1)+self.refCell('DailyExtShtLAInc',rowIndex,-1)",-1)
        
        self.spreadsheet.addColumn('FractLeafAbcission')\
        .setDependencies(['AccTmin5'])\
        .setFormula("self.interpolateResponse(leafAbscissionModelX, leafAbscissionModelY, self.refCell('AccTmin5',rowIndex,0))",-1)
        
        self.spreadsheet.addColumn('ActiveLeafArea')\
        .setDependencies(['AccTotLeafArea', 'FractLeafAbcission'])\
        .setFormula("self.sf_IF(self.refCell('AccTotLeafArea',rowIndex,0)>0,self.refCell('AccTotLeafArea',rowIndex,0)*(1-self.refCell('FractLeafAbcission',rowIndex,0)),0)",-1)
        
        self.spreadsheet.addColumn('LeafAreaIndex')\
        .setDependencies(['ActiveLeafArea'])\
        .setFormula("self.refCell('ActiveLeafArea',rowIndex,0) / pAreaPerTree",-1)
        
        self.spreadsheet.addColumn('Pmax')\
        .setFormula("self.interpolateResponse(pMaxModelX, pMaxModelY, self.refCell('TimeInterval',rowIndex,0))",-1)
        
        self.spreadsheet.addColumn('TempEffPn')\
        .setDependencies(['TempMin','TempMax'])\
        .setFormula("0.33*(0.535+0.0384*self.refCell('TempMax',rowIndex,0)-0.0004126*self.refCell('TempMax',rowIndex,0)**2-0.00001576*self.refCell('TempMax',rowIndex,0)**3)+0.67\
                    *(0.535+0.0384*(0.75*self.refCell('TempMax',rowIndex,0)+0.25*self.refCell('TempMin',rowIndex,0))-0.0004126*(0.75*self.refCell('TempMax',rowIndex,0)+0.25\
                    *self.refCell('TempMin',rowIndex,0))**2-0.00001576*(0.75*self.refCell('TempMax',rowIndex,0)+0.25*self.refCell('TempMin',rowIndex,0))**3)",-1)
        
        self.spreadsheet.addColumn('PmaxTempAdj')\
        .setDependencies(['Pmax','TempEffPn'])\
        .setFormula("self.refCell('Pmax',rowIndex,0)*self.refCell('TempEffPn',rowIndex,0)",-1)
        
        self.spreadsheet.addColumn('PChemEff')\
        .setFormula("self.interpolateResponse(photoChemEffModelX, photoChemEffModelY, self.refCell('TimeInterval',rowIndex,0))",-1)
        
        self.spreadsheet.addColumn('PestTrtPnEff')\
        .setFormula("1",-1)
        
        self.spreadsheet.addColumn('DailyPnRate')\
        .setDependencies(['PChemEff','TotalPAR','DayLength','PmaxTempAdj','LeafAreaIndex','PestTrtPnEff'])\
        .setFormula("(self.refCell('PChemEff',rowIndex,0)*self.refCell('TotalPAR',rowIndex,0)*self.refCell('DayLength',rowIndex,0)*self.refCell('PmaxTempAdj',rowIndex,0)\
                    *pFmax*(1-exp(-pCanopyLightExtinction*(self.refCell('LeafAreaIndex',rowIndex,0)/pFmax)))/(self.refCell('PChemEff',rowIndex,0)\
                    *pCanopyLightExtinction*self.refCell('TotalPAR',rowIndex,0)+self.refCell('DayLength',rowIndex,0)*self.refCell('PmaxTempAdj',rowIndex,0)))\
                    *self.refCell('PestTrtPnEff',rowIndex,0)",-1)
        
        self.spreadsheet.addColumn('DailyPnTotal')\
        .setDependencies(['DailyPnRate']).\
        setFormula("self.refCell('DailyPnRate',rowIndex,0)*pAreaPerTree",-1)
        
        self.spreadsheet.addColumn('DmFwFruit')\
        .setDependencies(['AccDegDays'])\
        .setFormula("self.interpolateResponse(dryMatterToFWModelX, dryMatterToFWModelY, self.refCell('AccDegDays',rowIndex,0))",-1)
        
        self.spreadsheet.addColumn('MaxFGRate')\
        .setFormula("self.interpolateResponse(fruitMaxGrowthRateModelX, fruitMaxGrowthRateModelY, self.refCell('TimeInterval',rowIndex,0))",-1)
        
        self.spreadsheet.addColumn('FruitGRDmDay')\
        .setDependencies(['MaxFGRate','DmFwFruit'])\
        .setFormula("self.refCell('MaxFGRate',rowIndex,0)/self.refCell('DmFwFruit',rowIndex,0)",-1)
        
        self.spreadsheet.addColumn('CarbonDmFruit')\
        .setFormula("self.interpolateResponse(fruitCarbonDryMatterModelX, fruitCarbonDryMatterModelY, self.refCell('TimeInterval',rowIndex,0))",-1)
        
        self.spreadsheet.addColumn('CurrentFruit')\
        .setFormula("pInitialFruitCount",0)\
        .setFormula("self.refCell('CurrentFruit',rowIndex,-1)-self.refCell('FruitAbscission',rowIndex,-1)",-1)
        
        self.spreadsheet.addColumn('MeanFruitWt')\
        .setFormula("pInitialFruitWeight",0)\
        .setFormula("self.refCell('MeanFruitWt',rowIndex,-1)+self.refCell('DeltaFruitWeight',rowIndex,-1)",-1)
        
        
        self.spreadsheet.addColumn('FruitTotWeight')\
        .setDependencies(['CurrentFruit','MeanFruitWt'])\
        .setFormula("self.refCell('CurrentFruit',rowIndex,0)*self.refCell('MeanFruitWt',rowIndex,0)",-1)
        
        self.spreadsheet.addColumn('AvgCO2')\
        .setDependencies(['CurrentFruit','accum_CO2'])\
        .setFormula("self.sf_IF(self.refCell('CurrentFruit',rowIndex,0)==0,0,self.refCell('accum_CO2',rowIndex,0)/3)",-1)
        
        self.spreadsheet.addColumn('DailyFruitFW')\
        .setDependencies(['AvgCO2','CarbonDmFruit','DmFwFruit'])\
        .setFormula("self.refCell('AvgCO2',rowIndex,0)*self.refCell('CarbonDmFruit',rowIndex,0)*self.refCell('DmFwFruit',rowIndex,0)",-1)
        
        self.spreadsheet.addColumn('CurrentFruitDiv')\
        .setDependencies(['CurrentFruit'])\
        .setFormula("self.sf_IF(self.refCell('CurrentFruit',rowIndex,0)==0,1,self.refCell('CurrentFruit',rowIndex,0))",-1)
        
        self.spreadsheet.addColumn('DeltaFruitWeight')\
        .setDependencies(['AccDegDays','DailyFruitFW','CurrentFruitDiv'])\
        .setFormula("self.sf_IF(self.refCell('AccDegDays',rowIndex,0)>170,self.refCell('DailyFruitFW',rowIndex,0)/self.refCell('CurrentFruitDiv',rowIndex,0),0)",-1)
        
        self.spreadsheet.addColumn('FruitGrowthPctMax')\
        .setDependencies(['AccDegDays','DeltaFruitWeight','TempMaxFruitGrowth'])\
        .setFormula("self.sf_IF(self.refCell('AccDegDays',rowIndex,0)>170,self.refCell('DeltaFruitWeight',rowIndex,0)/self.refCell('TempMaxFruitGrowth',rowIndex,0)*100,100)",-1)
        
        self.spreadsheet.addColumn('TMultiplierFG')\
        .setDependencies(['TempMean'])\
        .setFormula("self.interpolateResponse(fruitTempGrowthModelX, fruitTempGrowthModelY, self.refCell('TempMean',rowIndex,0))",-1)
        
        self.spreadsheet.addColumn('TempMaxFruitGrowth')\
        .setDependencies(['MaxFGRate','TMultiplierFG'])\
        .setFormula("self.refCell('MaxFGRate',rowIndex,0)*self.refCell('TMultiplierFG',rowIndex,0)",-1)
        
        self.spreadsheet.addColumn('AbscCurve')\
        .setDependencies(['FruitGrowthPctMax'])\
        .setFormula("self.interpolateResponse(abscissionModelX, abscissionModelY, self.refCell('FruitGrowthPctMax',rowIndex,0))",-1)
        
        self.spreadsheet.addColumn('FruitFrctAbsc')\
        .setDependencies(['AccDegDays','AbscCurve'])\
        .setFormula("self.sf_IF(self.refCell('AccDegDays',rowIndex,0)<700,self.refCell('AbscCurve',rowIndex,0),0)",-1)
        
        self.spreadsheet.addColumn('HandThin')\
        .setFormula("self.interpolateResponse(handHarvestModelX, handHarvestModelY, self.refCell('TimeInterval',rowIndex,0))",-1)
        
        self.spreadsheet.addColumn('ModFrAbsc')\
        .setDependencies(['HandThin','FruitFrctAbsc'])\
        .setFormula("self.sf_IF(self.refCell('HandThin',rowIndex,0)>0,self.refCell('HandThin',rowIndex,0),self.refCell('FruitFrctAbsc',rowIndex,0))",-1)
        
        self.spreadsheet.addColumn('FruitAbscission')\
        .setDependencies(['AccDegDays','CurrentFruit','ModFrAbsc'])\
        .setFormula("self.sf_IF(pDisableAbscissionModel,0,self.sf_IF(self.refCell('AccDegDays',rowIndex,0)<190,self.refCell('CurrentFruit',rowIndex,0)*0,self.refCell('CurrentFruit',rowIndex,0)*self.refCell('ModFrAbsc',rowIndex,0)))",-1)
        
        self.spreadsheet.addColumn('TotalDemand')\
        .setDependencies(['ShootDemand','FruitDemand','WoodDemand','RootDemand'])\
        .setFormula("self.refCell('ShootDemand',rowIndex,0)+self.refCell('FruitDemand',rowIndex,0)+self.refCell('WoodDemand',rowIndex,0)+self.refCell('RootDemand',rowIndex,0)",-1)
        
        self.spreadsheet.addColumn('DailyCarbonBal')\
        .setDependencies(['DailyPnTotal','DailyResp'])\
        .setFormula("self.sf_IF(pIsDailyCarbonBalBiflow,self.refCell('DailyPnTotal',rowIndex,0)-self.refCell('DailyResp',rowIndex,0),self.sf_IF(self.refCell('DailyPnTotal',rowIndex,0)-self.refCell('DailyResp',rowIndex,0)<0,0,self.refCell('DailyPnTotal',rowIndex,0)-self.refCell('DailyResp',rowIndex,0)))",-1)
        
        self.spreadsheet.addColumn('AccCO2')\
        .setDependencies(['DailyCarbonBal'])\
        .setFormula("self.sf_IF(self.sf_NOT(pIsAccCO2Biflow),self.sf_IF(self.refCell('DailyCarbonBal',rowIndex,0)>0,self.refCell('DailyCarbonBal',rowIndex,0),0),self.refCell('DailyCarbonBal',rowIndex,0))",0)\
        .setFormula("self.sf_IF(self.sf_NOT(pIsAccCO2Biflow),self.refCell('AccCO2',rowIndex,-1)+self.sf_IF(self.refCell('DailyCarbonBal',rowIndex,-1)>0,self.refCell('DailyCarbonBal',rowIndex,-1),0),self.refCell('AccCO2',rowIndex,-1)+self.refCell('DailyCarbonBal',rowIndex,-1))",-1)
        
        self.spreadsheet.addColumn('SumRelParts')\
        .setDependencies(['RelPartShoot','RelPartFruit','RelWoodPart','RelRootPart'])\
        .setFormula("self.refCell('RelPartShoot',rowIndex,0)+self.refCell('RelPartFruit',rowIndex,0)+self.refCell('RelWoodPart',rowIndex,0)+self.refCell('RelRootPart',rowIndex,0)",-1)
        
        self.spreadsheet.addColumn('NoExtGrwngShts')\
        .setFormula("self.interpolateResponse(shootExtGrowthModelX, shootExtGrowthModelY, self.refCell('TimeInterval',rowIndex,0))",-1)
        
        self.spreadsheet.addColumn('ShootGrowthPerExt')\
        .setFormula("self.interpolateResponse(shootGrowthPerExtModelX, shootGrowthPerExtModelY, self.refCell('TimeInterval',rowIndex,0))",-1)
        
        self.spreadsheet.addColumn('GrowthRPerSpur')\
        .setFormula("self.interpolateResponse(spurGrowthModelX,spurGrowthModelY, self.refCell('TimeInterval',rowIndex,0))",-1)
        
        self.spreadsheet.addColumn('MiscTempEffect')\
        .setDependencies(['TempMean'])\
        .setFormula("self.interpolateResponse(miscTempEffectModelX,miscTempEffectModelY, self.refCell('TempMean',rowIndex,0))",-1)
        
        self.spreadsheet.addColumn('ShootDemand')\
        .setDependencies(['NoExtGrwngShts','ShootGrowthPerExt','NumGrwngSpurs','GrowthRPerSpur','MiscTempEffect'])\
        .setFormula("(((self.refCell('NoExtGrwngShts',rowIndex,0)*self.refCell('ShootGrowthPerExt',rowIndex,0))+(self.refCell('NumGrwngSpurs',rowIndex,0)*self.refCell('GrowthRPerSpur',rowIndex,0)))*self.refCell('MiscTempEffect',rowIndex,0))/pVegDryMatterToCO2",-1)
        
        self.spreadsheet.addColumn('RelPartShoot')\
        .setDependencies(['ShootDemand','DailyCarbonBal','TotalDemand'])\
        .setFormula("self.refCell('ShootDemand',rowIndex,0)-(self.refCell('ShootDemand',rowIndex,0)*(1-pRelSinkStrengthShoot)*(1-(self.refCell('DailyCarbonBal',rowIndex,0)/self.refCell('TotalDemand',rowIndex,0))))",-1)
        
        self.spreadsheet.addColumn('FruitDMToCO2')\
        .setFormula("self.interpolateResponse(fruitDMtoCO2ModelX,fruitDMtoCO2ModelY, self.refCell('TimeInterval',rowIndex,0))",-1)
        
        self.spreadsheet.addColumn('FruitDemand')\
        .setDependencies(['CurrentFruit','FruitGRDmDay','TMultiplierFG','FruitDMToCO2'])\
        .setFormula("self.refCell('CurrentFruit',rowIndex,0)*self.refCell('FruitGRDmDay',rowIndex,0)*self.refCell('TMultiplierFG',rowIndex,0)/self.refCell('FruitDMToCO2',rowIndex,0)",-1)
        
        self.spreadsheet.addColumn('RelPartFruit')\
        .setDependencies(['FruitDemand','DailyCarbonBal','TotalDemand'])\
        .setFormula("self.refCell('FruitDemand',rowIndex,0)-(self.refCell('FruitDemand',rowIndex,0)*(1-pRelSinkStrengthFruit)*(1-(self.refCell('DailyCarbonBal',rowIndex,0)/self.refCell('TotalDemand',rowIndex,0))))",-1)
        
        self.spreadsheet.addColumn('CO2toFruit')\
        .setDependencies(['DailyCarbonBal','SumRelParts','RelPartFruit','FruitDemand'])\
        .setFormula("self.sf_IF(self.refCell('DailyCarbonBal',rowIndex,0)/self.refCell('SumRelParts',rowIndex,0)<1,self.refCell('RelPartFruit',rowIndex,0)*(self.refCell('DailyCarbonBal',rowIndex,0)/self.refCell('SumRelParts',rowIndex,0)),self.refCell('FruitDemand',rowIndex,0))",-1)
        
        self.spreadsheet.addColumn('accum_CO2')\
        .setDependencies(['CO2toFruit'])\
        .setFormula("self.refCell('CO2toFruit',rowIndex,0)",0)\
        .setFormula("self.refCell('CO2toFruit',rowIndex,-1)",1)\
        .setFormula("self.refCell('CO2toFruit',rowIndex,-2)+self.refCell('CO2toFruit',rowIndex,-1)",2)\
        .setFormula("self.refCell('CO2toFruit',rowIndex,-3)+self.refCell('CO2toFruit',rowIndex,-2)+self.refCell('CO2toFruit',rowIndex,-1)",-1)\
        
        self.spreadsheet.addColumn('CO2toFruit4DayTot')\
        .setDependencies(['CO2toFruit'])\
        .setFormula("self.refCell('CO2toFruit',rowIndex,0)",0)\
        .setFormula("self.refCell('CO2toFruit',rowIndex,-1)+self.refCell('CO2toFruit',rowIndex,0)",1)\
        .setFormula("self.refCell('CO2toFruit',rowIndex,-2)+self.refCell('CO2toFruit',rowIndex,-1)+self.refCell('CO2toFruit',rowIndex,0)",2)\
        .setFormula("self.refCell('CO2toFruit',rowIndex,-3)",-1)
        
        self.spreadsheet.addColumn('DailyCtoFruit')\
        .setDependencies(['CO2toFruit','FruitDMToCO2'])\
        .setFormula("self.refCell('CO2toFruit',rowIndex,0)*self.refCell('FruitDMToCO2',rowIndex,0)",-1)
        
        self.spreadsheet.addColumn('AccDMToFruit')\
        .setDependencies(['DailyCtoFruit'])\
        .setFormula("self.refCell('DailyCtoFruit',rowIndex,0)",0)\
        .setFormula("self.refCell('DailyCtoFruit',rowIndex,-1)+self.refCell('AccDMToFruit',rowIndex,-1)",-1)
        
        self.spreadsheet.addColumn('WoodDemand')\
        .setDependencies(['MiscTempEffect'])\
        .setFormula("5*self.refCell('MiscTempEffect',rowIndex,0)/pVegDryMatterToCO2",-1)
        
        self.spreadsheet.addColumn('RelWoodPart')\
        .setDependencies(['WoodDemand','DailyCarbonBal','TotalDemand'])\
        .setFormula("+self.refCell('WoodDemand',rowIndex,0)-(self.refCell('WoodDemand',rowIndex,0)*(1-pRelSinkStrengthWood)*(1-(self.refCell('DailyCarbonBal',rowIndex,0)/self.refCell('TotalDemand',rowIndex,0))))",-1)
        
        self.spreadsheet.addColumn('TempEffRoots')\
        .setDependencies(['SoilTemp'])\
        .setFormula("self.interpolateResponse(rootTempGrowthModelX, rootTempGrowthModelY, self.refCell('SoilTemp',rowIndex,0))",-1)
        
        self.spreadsheet.addColumn('RootDemand')\
        .setDependencies(['TempEffRoots'])\
        .setFormula("5*self.refCell('TempEffRoots',rowIndex,0)/pVegDryMatterToCO2",-1)
        
        self.spreadsheet.addColumn('RelRootPart')\
        .setDependencies(['RootDemand','DailyCarbonBal','TotalDemand'])\
        .setFormula("self.refCell('RootDemand',rowIndex,0)-(self.refCell('RootDemand',rowIndex,0)*(1-pRelSinkStrengthRoot)*(1-(self.refCell('DailyCarbonBal',rowIndex,0)/self.refCell('TotalDemand',rowIndex,0))))",-1)
        
        self.spreadsheet.addColumn('DailyResp')\
        .setDependencies(['DailyLeafR','DailyWoodR','DailyFruitR'])\
        .setFormula("self.refCell('DailyLeafR',rowIndex,0)+self.refCell('DailyWoodR',rowIndex,0)+self.refCell('DailyFruitR',rowIndex,0)",-1)
        
        self.spreadsheet.addColumn('LeafTempDk')\
        .setDependencies(['TempMin','TempMax'])\
        .setFormula("(self.refCell('TempMin',rowIndex,0)+self.refCell('TempMin',rowIndex,0)+self.refCell('TempMax',rowIndex,0))/3",-1)
        
        self.spreadsheet.addColumn('TempIntLF')\
        .setFormula("self.interpolateResponse(leafTempRespRateModelX,leafTempRespRateModelY, self.refCell('TimeInterval',rowIndex,0))",-1)
        
        self.spreadsheet.addColumn('RateLeafR')\
        .setDependencies(['TempIntLF','LeafTempDk','DayLength'])\
        .setFormula("((self.refCell('TempIntLF',rowIndex,0)*exp(self.refCell('LeafTempDk',rowIndex,0)*pTempCoeffOfLeafResp))*(86400-self.refCell('DayLength',rowIndex,0)))/1000",-1)
        
        self.spreadsheet.addColumn('DailyLeafR')\
        .setDependencies(['ActiveLeafArea','RateLeafR'])\
        .setFormula("self.refCell('ActiveLeafArea',rowIndex,0)*self.refCell('RateLeafR',rowIndex,0)",-1)
        
        self.spreadsheet.addColumn('WoodTemp')\
        .setDependencies(['TempMean'])\
        .setFormula("self.refCell('TempMean',rowIndex,0)",-1)
        
        self.spreadsheet.addColumn('WoodTRespInt')\
        .setFormula("self.interpolateResponse(woodTempRespModelX,woodTempRespModelY, self.refCell('TimeInterval',rowIndex,0))",-1)
        
        self.spreadsheet.addColumn('RateWoodR')\
        .setDependencies(['WoodTRespInt','WoodTemp'])\
        .setFormula("((self.refCell('WoodTRespInt',rowIndex,0)*exp(pTempCoeffOfWoodResp*self.refCell('WoodTemp',rowIndex,0)))*86400)/1000",-1)
        
        self.spreadsheet.addColumn('WoodSurfArea')\
        .setFormula("self.interpolateResponse(woodSurfaceAreaModelX,woodSurfaceAreaModelY, self.refCell('TimeInterval',rowIndex,0))",-1)
        
        self.spreadsheet.addColumn('DailyWoodR')\
        .setDependencies(['RateWoodR','WoodSurfArea'])\
        .setFormula("self.refCell('RateWoodR',rowIndex,0)*self.refCell('WoodSurfArea',rowIndex,0)",-1)
        
        self.spreadsheet.addColumn('FruitTemp')\
        .setDependencies(['TempMean'])\
        .setFormula("self.refCell('TempMean',rowIndex,0)",-1)
        
        self.spreadsheet.addColumn('TIntFrt')\
        .setFormula("self.interpolateResponse(tempIntFruitModelX,tempIntFruitModelY, self.refCell('TimeInterval',rowIndex,0))",-1)
        
        self.spreadsheet.addColumn('TSlopeFrt')\
        .setFormula("self.interpolateResponse(tempSlopeFruitModelX,tempSlopeFruitModelY, self.refCell('TimeInterval',rowIndex,0))",-1)
        
        self.spreadsheet.addColumn('RateFruitR')\
        .setDependencies(['TIntFrt','TSlopeFrt','FruitTemp'])\
        .setFormula("(self.refCell('TIntFrt',rowIndex,0)*exp(self.refCell('TSlopeFrt',rowIndex,0)*self.refCell('FruitTemp',rowIndex,0)))*0.0864",-1)
        
        self.spreadsheet.addColumn('DailyFruitR')\
        .setDependencies(['RateFruitR','FruitTotWeight'])\
        .setFormula("self.refCell('RateFruitR',rowIndex,0)*self.refCell('FruitTotWeight',rowIndex,0)*pLightEffectOnResp",-1)
        
        
        return

    def evaluate(self):
        
        # Populate weather data columns
        self.spreadsheet.columns['TimeInterval'].setEvalOrder(1)
        self.spreadsheet.columns['TempMin'].setEvalOrder(2)
        self.spreadsheet.columns['TempMax'].setEvalOrder(3)
        self.spreadsheet.columns['DailyRad'].setEvalOrder(4)
        self.spreadsheet.evalOrder = 5
        
        for i in range(0, self.weatherData.numberOfDays()):
            self.spreadsheet.column('TimeInterval').row(i).setValue(i)
            self.spreadsheet.column('TempMin').row(i).setValue(self.weatherData.minTemp(i))
            self.spreadsheet.column('TempMax').row(i).setValue(self.weatherData.maxTemp(i))
            self.spreadsheet.column('DailyRad').row(i).setValue(self.weatherData.totalRadiation(i))

        self.spreadsheet.evaluate(self.weatherData.numberOfDays())
        
        return self.spreadsheet.getCellValues()

