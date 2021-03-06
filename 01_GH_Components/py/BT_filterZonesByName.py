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
Use this to split apart multi-zone Groups based on Zone Name. Useful since the order of the zones in the list changes sometimes - so if you want one or another zone isolated out to apply unique loads, use this component.
-
EM Jul. 10, 2020
    Args:
        _HBZones: The Honeybee Zones
        _findZone: (list) The name or names (as multiline) of the zone(s) to seach for.
    Returns:
        foundZones_: A list of the zones who's name matches the search name(s).
        otherZones_: A list of all the zone which don't match the search name(s).
"""

ghenv.Component.Name = "BT_filterZonesByName"
ghenv.Component.NickName = "Filter Zones"
ghenv.Component.Message = 'JUL_10_2020'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "BT"
ghenv.Component.SubCategory = "01 | Model"

import scriptcontext as sc

hb_hive = sc.sticky["honeybee_Hive"]()
HBZoneObjects = hb_hive.callFromHoneybeeHive(_HBZones)

foundZones_ = []
otherZones_ = []

for i, zoneObj in enumerate(HBZoneObjects):
    for each in _findZone:
        if each in zoneObj.name:
            foundZones_.append(_HBZones[i])
            break
    else:
        otherZones_.append(_HBZones[i])
