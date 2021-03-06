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
For setting up a Write 2XL PHPP Object. Be careful with this! It'll let you write anyplace in the XL sheet - be cautious not to overwrite an important formula in the PHPP or other unintendded error
-
EM Jul. 21, 2020
    Args:
        _worksheetName: List. Worksheet names for the data to be writen to. Be sure these match the Worksheet names in the Excel document exactly. 
        _rangeAddress: List. Cell Ranges to write to. Should be Excel style ('A1', 'B23', 'AA45', etc...)
        _rangeValue: List. The actual values to write to the Cell Ranges listed in _rangeAddress. 
    Returns:
        toPHPP_UD_: A DataTree of the final clean, Excel-Ready output objects. Each output object has a Worksheet-Name, a Cell Range, and a Value. Connect to the 'UserDefined_' input on the 'Write 2PHPP' Component to write to Excel.
"""

ghenv.Component.Name = "BT_CreateXLObj_UD"
ghenv.Component.NickName = "Create Excel Obj - UD"
ghenv.Component.Message = 'JUL_21_2020'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "BT"
ghenv.Component.SubCategory = "02 | IDF2PHPP"

import scriptcontext as sc
import Grasshopper.Kernel as ghK
from System import Object
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path

# Classes and Defs
PHPP_XL_Obj = sc.sticky['PHPP_XL_Obj'] 
preview = sc.sticky['Preview']

toPHPP_UD_ = DataTree[Object]()

# Use Path 100 so that it always comes last. UD values should override anything else in the document.
if len(_worksheetNames) == len(_rangeAddresses) and len(_worksheetNames) == len(_rangeValues):
    for i in range(len(_worksheetNames)):
        toPHPP_UD_.Add( PHPP_XL_Obj(_worksheetNames[i],  _rangeAddresses[i], _rangeValues[i]), GH_Path(100) )
elif len(_rangeValues) == len(_rangeAddresses) and len(_worksheetNames) > 0:
    for i in range(len(_rangeValues)):
        toPHPP_UD_.Add( PHPP_XL_Obj(_worksheetNames[0],  _rangeAddresses[i], _rangeValues[i]), GH_Path(100) )
else:
    msgError = "Mismatched list lengths.\nMake sure the same number of items is being input into all the input ports."
    ghenv.Component.AddRuntimeMessage(ghK.GH_RuntimeMessageLevel.Warning, msgError)



