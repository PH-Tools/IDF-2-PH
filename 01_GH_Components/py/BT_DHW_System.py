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
Collects and organizes data for a DHW System. Hook up inputs from DHW components and this will organize for the excel writere.
Connect the output to the 'dhw_' input on the 'Create Excel Obj - Setup' component to use.
-
EM August 10, 2020
    Args:
        usage_: The Usage Profile object decribing DHW litres/person/day of HW at the Design Forward temp (unmixed). Input the result from a 'DHW Usage' component.
        design_frwrd_T: (Deg C) Design Forward Temperature. Default is 60 deg C. Unmixed HW temp.
        ['DHW+Distribution', Cell J146]
        circulation_piping_: The Recirculation Piping (not including branches). This is only used if there is a recirc loop in the project. Connect a 'Pipping | Recirc' component here.
        ['DHW+Distribution', Cells J149:N163]
        branch_piping_: All the branch (non-recirc) piping. Connect the 'Piping | Banches' result here. 
        ['DHW+Distribution', Cells J167:N175]
        tank1_: The main DHW tank (if any) used. Input the results of a 'DHW Tank' component.
        ['DHW+Distribution', Cells J186:J204]
        tank2_: The secondary DHW tank (if any) used. Input the results of a 'DHW Tank' component. 
        ['DHW+Distribution', Cells M186:M204]
        buffer_tank_: The DHW buffer tank (if any) used. Input the results of a 'DHW Tank' component. 
        ['DHW+Distribution', Cells P186:P204]
    Returns:
        dhw_: The combined DHW System object with all params. Connect this to the 'dhw_' input on the 'Create Excel Obj - Setup' component to use.
"""

ghenv.Component.Name = "BT_DHW_System"
ghenv.Component.NickName = "DHW"
ghenv.Component.Message = 'AUG_10_2020'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "BT"
ghenv.Component.SubCategory = "01 | Model"

import scriptcontext as sc
import Grasshopper.Kernel as ghK

# Classes and Defs
preview = sc.sticky['Preview']
PHPP_DHW_System = sc.sticky['PHPP_DHW_System']
hb_hive = sc.sticky["honeybee_Hive"]()
HBZoneObjects = hb_hive.callFromHoneybeeHive(_HBZones)

def inputWarnings(_obj, _key, _inputName):
    try:
        result = getattr(_obj, _key)
        return True
    except:
        warning = "Error. The '{}' input doesn't look right?\nMissing or incorrect type of input for: '{}'.\nPlease check your input values.".format(_inputName, _key)
        ghenv.Component.AddRuntimeMessage(ghK.GH_RuntimeMessageLevel.Warning, warning)
        return False

# Check Input Types
if _systemName: name = _systemName
else: name = 'DHW'
if usage_:
    try:
        if usage_.UsageType == 'Res': inputWarnings(usage_, 'demand_showers', 'usage_')
        else: inputWarnings(usage_, 'use_daysPerYear', 'usage_')
    except: ghenv.Component.AddRuntimeMessage(ghK.GH_RuntimeMessageLevel.Warning, 'Error reading the Usage Input? Use a "DHW Use" component.')
if design_frwrd_T: 
    try: float(design_frwrd_T)
    except: ghenv.Component.AddRuntimeMessage(ghK.GH_RuntimeMessageLevel.Warning, 'Design Forward Temp should be number.')
if len(circulation_piping_) > 0: inputWarnings(circulation_piping_[0], 'insulThck', 'circulation_piping_')
if len(branch_piping_) > 0: inputWarnings(branch_piping_[0], 'tapOpenings', 'branch_piping_')
if tank1_:  inputWarnings(tank1_, 'hl_rate', 'tank1_')
if tank2_:  inputWarnings(tank2_, 'hl_rate', 'tank2_')

# Edit Buffer inputs
if buffer_tank_ and inputWarnings(buffer_tank_, 'hl_rate', 'buffer_tank_'):
    if '0' not in buffer_tank_.type:
        buffer_tank_.type = '1-Existing storage tank'

# Create the DHW System Object
dhw_ = PHPP_DHW_System(name, 
            usage_,
            design_frwrd_T,
            circulation_piping_,
            branch_piping_,
            tank1_,
            tank2_,
            buffer_tank_
            )

# Add the new System onto the Zones
for zone in HBZoneObjects:
    dhw_.getZonesAssignedList().append(zone.name)
    setattr(zone, 'PHPP_DHWSys', dhw_)

if _HBZones:
    HBZones_ = hb_hive.addToHoneybeeHive(HBZoneObjects, ghenv.Component)

print('----\nDHW System:')
preview(dhw_)
