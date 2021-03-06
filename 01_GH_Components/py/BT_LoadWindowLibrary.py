#
# IDF2PHPP: A Plugin for exporting an EnergyPlus IDF file to the Passive House Planning Package (PHPP). Created by blgdtyp, llc
# 
# This component is part of IDF2PHPP.
# 
# Copyright (c) 2020, bldgtyp, llc <info@bldgtyp.com> 
# IDF2PHPP is free software; you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published 
# by the Free Software Foundation; either version 3 of the License, 
# or (at your option) any later version. 
# 
# IDF2PHPP is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU General Public License for more details.
# 
# For a copy of the GNU General Public License
# see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>
#
"""
This will read in the contents of a PHPP-Style Excel file window library ('Components' worksheet). You can certainly point this at any actual PHPP file, but that will probably be slow. Recomended to extract the 'Components' worksheeet from a PHPP file into a dedicated 'Libary' Excel file (Duplicate). That will allow this to run much faster. Will read only the 'Glazing' and 'Frames' portions of the 'Components' worksheet (blocks IE15:IG113 and IL15:JC113).
-Input *.xls or *.xlsx files only.
-
EM Feb. 25, 2020
    Args:
        _LoadLib: Set to 'True' to run.
        _libFolderPath: (string) The folder where the Window Library file is located
        _libFileName: (string) The filename of the Excel file to read from.
    Returns:
        lib_Frames_: (list) The PHPP-Style Frame Objects imported from the Library.
        lib_Glazing_: (list) The PHPP-Style Glazing Objects imported from the Library. 
"""

ghenv.Component.Name = "BT_LoadWindowLibrary"
ghenv.Component.NickName = "Load Window Lib"
ghenv.Component.Message = 'FEB_25_2020'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "BT"
ghenv.Component.SubCategory = "01 | Model"

import os
from shutil import copyfile
import random
import json
import Grasshopper.Kernel as ghK
import clr
clr.AddReferenceByName('Microsoft.Office.Interop.Excel, Culture=neutral, PublicKeyToken=71e9bce111e9429c')
from Microsoft.Office.Interop import Excel
import scriptcontext as sc

PHPP_Glazing = sc.sticky['PHPP_Glazing']
PHPP_Frame = sc.sticky['PHPP_Frame']

def getLibraryPath(_libFolderPath=None, _libFileName=None):
    # Finds the right Library File Path
    
    # first, clean up the input filename's extension
    if _libFileName:
        filename, extension = os.path.splitext(_libFileName)
        if 'xlsx' in extension or 'xls' in extension:
            _libFileName = _libFileName
        else:
            warningMsg = 'Please input only an Excel file (*.xls, *.xlsx) file to read'
            ghenv.Component.AddRuntimeMessage(ghK.GH_RuntimeMessageLevel.Warning, warningMsg)
            _libFileName = None
            
    if _libFolderPath and _libFileName:
        libraryFilePath = os.path.join(_libFolderPath, _libFileName)
        
        if os.path.exists(libraryFilePath):
            print 'Using File:', libraryFilePath
        else:
            warningMsg =  "Can't find the file. Something is wrong with the folder or filename?"
            ghenv.Component.AddRuntimeMessage(ghK.GH_RuntimeMessageLevel.Warning, warningMsg)
            return None
            
        # Make sure its an Excel File
        if 'xls' in libraryFilePath[-4:]:
            return libraryFilePath
        else: 
            warningMsg = 'Please input only an Excel file (*.xls, *.xlsx) file to read'
            ghenv.Component.AddRuntimeMessage(ghK.GH_RuntimeMessageLevel.Warning, warningMsg)
            return None
    else:
        print 'Input the folder path and filename to proceed.'
        return None

def getDataFromExcel(_filePath):
    # Pulls the Glass and Frame data from the Excel file
    
    # Open an Excel Instance and the Temporary Lib File
    print '  >Opening Excel document and reading contents....'
    ex = Excel.ApplicationClass()
    ex.Visible = False  # False means excel is hidden as it works
    ex.DisplayAlerts = False
    workbook = ex.Workbooks.Open(_filePath)
    
    # Find the Windows Worksheet
    worksheets = workbook.Worksheets
    try:
        wsComponents = worksheets['Components']
        print '  >Found the Excel Worksheet:', wsComponents.Name
    except:
        print "Could not find the 'Components' Worksheet in the taget file?"

    # Read in the Components from Excel Worksheet
    # Come in as 2D Arrays..... grrr.....
    xlArrayGlazing_ =  wsComponents.Range['IE15:IG113'].Value2
    xlArrayFrames_ = wsComponents.Range['IL15:JC113'].Value2
    
    workbook.Close()  # Close the worbook itself
    ex.Quit()  # Close out the instance of Excel
    os.remove(_filePath) # Remove the temporary read-file
    
    return xlArrayGlazing_, xlArrayFrames_

# Sort out the Library File Path to read from
libraryFilePath = getLibraryPath(_libFolderPath, _libFileName)

if _LoadLib and libraryFilePath:
    # Make a Temporary copy of the Library File
    saveDir = os.path.split(libraryFilePath)[0]
    tempFileName = 'tempLibFile_{}.xlsx'.format(random.randint(0,1000))
    tempFilePath = os.path.join(saveDir, tempFileName)
    copyfile(libraryFilePath, tempFilePath) # create a copy of the file to read from
    
    # Get the Data from the Excel File
    xlArrayGlazing, xlArrayFrames = getDataFromExcel(tempFilePath)

    # Read in the Glazing Data and Build new Glazing Objects
    lib_Glazing = []
    xlListGlazing = list(xlArrayGlazing)
    for i in range(0,  int(len(xlListGlazing)/3 ), 3 ):
        if xlListGlazing[i] != None:
            newGlazing = PHPP_Glazing(xlListGlazing[i], # Name
                            float(xlListGlazing[i+1]), # g-Value
                            float(xlListGlazing[i+2]) # U-Value
                            )
            lib_Glazing.append(newGlazing)
    
    # Read in the Excel Data and Build new Frame Objects
    lib_Frames = []
    xlListFrames = list(xlArrayFrames)
    for i in range(0,  int(len(xlListFrames)/17 ), 18 ):
        newFrame = []
        if xlListFrames[i] != None:
            newFrame = PHPP_Frame(
                xlListFrames[i], # Name
                [xlListFrames[i+1],xlListFrames[i+2], xlListFrames[i+3], xlListFrames[i+4]], # U-Values
                [xlListFrames[i+5],xlListFrames[i+6], xlListFrames[i+7], xlListFrames[i+8]], # Widths
                [xlListFrames[i+9],xlListFrames[i+10], xlListFrames[i+11], xlListFrames[i+12]], # Psi-Glazing
                [xlListFrames[i+13],xlListFrames[i+14], xlListFrames[i+15], xlListFrames[i+16]], # Psi-Installs
                xlListFrames[i+17] # Chi-Glass Carrier
                )
                
            lib_Frames.append(newFrame)

# Do it this way so you can turn off the 'reader' for the GH Session but it'll hold onto the params.
# Still need to read once at the start of the GH session, and anytime the library is updates
# But reading Excel takes a long time, so don't do it every run
try:
    lib_Frames_ = lib_Frames
    lib_Glazing_ = lib_Glazing
except:
    pass
