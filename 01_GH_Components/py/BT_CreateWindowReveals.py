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
Will create geometry for the window 'reveals' (the sides, top and bottom for windows which are installed in a host surface). These are used to accurately calcualte the window shading factors. Will also generate 'punched' envelope surface geometry to allow for accurate shading assessment.
-
EM August 3, 2020
    Args:
        _HBZones: (list) The Honeybee Zones for analysis
        moveWindows_: (bool) True = will move the window surfaces based on their 'InstallDepth' parameter. Use this if you want to push the windows 'in' to the host surface for the shading calculations. False = will not move the window surfaces.
    Returns:
        HBZones_: The updated Honeybee Zone objects to pass along to the next step.
        windowNames_: A list of the window names in the order calculated.
        windowSurfaces_: The window surfaces in the same order as the "windowNames_" output. If "moveWindows_" is set to True, these surfaces will be pushed 'in' according to their 'InstallDepth' parameter and surface normal.
        windowSurrounds_: (Tree) Each branch represents one window object. The surfaces in each branch correspond to the Bottom, Left, Top and Right 'reveal' surfaces. Use this to calculate the shading factors for the window surface.
        envelopSrfcs: The Honeybee zone surfaces, except with all the windows 'punched' out. 
"""

ghenv.Component.Name = "BT_CreateWindowReveals"
ghenv.Component.NickName = "Create Window Reveals"
ghenv.Component.Message = 'AUG_03_2020'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "BT"
ghenv.Component.SubCategory = "01 | Model"

import scriptcontext as sc
import ghpythonlib.components as ghc
import math
import rhinoscriptsyntax as rs
import Rhino 
from System import Object
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path

hb_hive = sc.sticky["honeybee_Hive"]()
HBZoneObjects = hb_hive.callFromHoneybeeHive(_HBZones)

windowSurrounds_ = DataTree[Object]()
windowNames_ = []
windowSurfaces_ = []
srfcEdges = DataTree[Object]()
count = 0

for zone in HBZoneObjects:
    for srfc in zone.surfaces:
        if srfc.hasChild == False:
            continue
        
        for childSrfc in srfc.childSrfs:
            # Get the Window Surface Honeybee Info
            windowNames_.append(childSrfc.name)
            
            # Get the PHPP Window Object
            phppWindowObj = zone.phppWindowDict.get(childSrfc.name, None)
            
            # Get the Shading Geometry, Add to the output list
            winShadingGeom = phppWindowObj.getWindowRevealGeom()
            windowSurrounds_.AddRange( winShadingGeom, GH_Path(count) )
            
            # Move (inset) the Window Surface
            windowSurfaces_.append( phppWindowObj.getInsetWindowSurface(moveWindows_) )
            
            count += 1
            
            # Add the updated Window Obj back to the phppDict
            zone.phppWindowDict[childSrfc.name] = phppWindowObj

# Go through and get all the opaque surfaces and add them to the output set
envelopSrfcs = DataTree[Object]()
envelopSrfcs_punched = []
for i, zone in enumerate(HBZoneObjects):
    for srfc in zone.surfaces:
        childSrfcs = []
        parentSrfc = srfc.geometry
        
        if 'INTERIOR' not in str(srfc.EPConstruction).upper():
            envelopSrfcs.Add(srfc.geometry, GH_Path(i) )
            
            if srfc.hasChild == True:
                for childSrfc in srfc.childSrfs:
                    childSrfcs.append(childSrfc.geometry)
                    
                envelopSrfcs_punched.append( ghc.SolidDifference(parentSrfc, childSrfcs) )
            else:
                envelopSrfcs_punched.append( srfc.geometry )

# Pass Along the Honeybee Zones
HBZones_ = _HBZones
