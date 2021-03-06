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
Ref: https://developer.rhino3d.com/samples/rhinocommon/overlay-text-display-conduit/
-
EM Mar. 7, 2020
    Args:
        _header: (List) The names for the Header (first) row. The length of this input list should correspond to the length of each branch in '_rows'
        _rows: (Tree) The data to plot. Each Branch on the input tree will correspond to one row in the final table
        preview_: (Int) Input an Integer value corresponding to the BranchNumber of the zone you'd like to preview in the _rows DataTree input. If none input will not preview. Note - probably want to turn this off for any printing.  
        tableOrigin_: (Point3d) <Optional> A starting point for the table (upper left corner). If no input uses 0,0,0
        rowHeight_: (Float) If printing to a page (8.5x11, 11x17, etc..) try ~5.0 (typical range from 1.0<-->5.0)
        columnWidths_: (Float) A value for the Column widths. Try ~15<-->20
        txtHeight_: (Float) If printing to a page (8.5x11, 11x17, etc..) try ~2.0 (typical range from 1.0<-->5.0)
    Returns:
        tables: A tree of the output tables, one table per Branch. Input this into the '_tablesToBake' input on a '2PDF | Print' component to print this to a PDF.
"""

ghenv.Component.Name = "BT_2PDF_BuildTable"
ghenv.Component.NickName = "2PDF | Make Table"
ghenv.Component.Message = 'MAR_07_2020'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "BT"
ghenv.Component.SubCategory = "03 | PDF"

import Rhino
import ghpythonlib.components as ghc
import rhinoscriptsyntax as rs
import scriptcontext as sc
from contextlib import contextmanager
from System import Object
import System.Drawing
import Grasshopper.Kernel as ghK
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path

@contextmanager
def docContext():
    try:
        sc.doc = Rhino.RhinoDoc.ActiveDoc
        yield
    finally:
        sc.doc = ghdoc

class CustomConduit(Rhino.Display.DisplayConduit):
    def DrawForeground(self, e):
        color = System.Drawing.Color.Blue
        numCol = 'B' # Exclude the 'Room Num' column (B)
        
        for key in self.Cells.keys():
            if numCol in key:
                txtStr = str(self.Cells[key].Value) 
            else:
                try:
                    val = float(self.Cells[key].Value)
                    txtStr = '{:.2f}'.format(val)
                except:
                    txtStr = str(self.Cells[key].Value)
                
            Text3dEntity = Rhino.Display.Text3d( txtStr )
            Text3d_Origin = self.Cells[key].Location
            Text3d_Normal = Rhino.Geometry.Vector3d(0,0,1)
            Text3dEntity.TextPlane = Rhino.Geometry.Plane(origin=Text3d_Origin, normal=Text3d_Normal)
            Text3dEntity.Height = self.Cells[key].TextHeight
            align = Rhino.DocObjects.TextHorizontalAlignment()
            Rhino.DocObjects.TextHorizontalAlignment.value__.SetValue(align, 1) #1=Center
            Text3dEntity.HorizontalAlignment = align
            
            e.Display.Draw3dText(Text3dEntity, color)
            #e.Display.Draw2dText(str(self.Cells[key].Value), color, self.Cells[key].Location, False)

def showafterscript(_cells, _preview):
    newConduit = None
    newConduit = CustomConduit()
    newConduit.Cells = _cells
    
    if not _preview:
        if sc.sticky.has_key('myconduit'):
            oldConduit = sc.sticky['myconduit']
            oldConduit.Enabled = False
            newConduit.Enabled = False
    else:
        if sc.sticky.has_key('myconduit'):
            oldConduit = sc.sticky['myconduit']
            oldConduit.Enabled = False
            newConduit.Enabled = True
            sc.sticky['myconduit'] = newConduit
        else:
            newConduit.Enabled = True
            sc.sticky['myconduit'] = newConduit
    
    if newConduit.Enabled: print('Conduit Enabled!')
    else: print('Conduit Disabled!')
    
    sc.doc.Views.Redraw()

class Table_Cell:
    
    def __init__(self, _range, _value=None, _txtHeight=1):
        self.Range = _range
        self.Column = self.Range[0]
        self.ColumnAsInt = ord(self.Column)-65
        self.Row = self.Range[1:]
        self.Value = _value
        self.Location = Rhino.Geometry.Point3d(0,0,0)
        self.TextHeight = _txtHeight
        self.valueFormat()
        
    def valueFormat(self):
        """Sets the cell's 'ValueFormated' parameter"""
        
        try:
            float(self.Value)
            self.ValueFormated = '{:.02f}'.format(self.Value)
        except:
            self.ValueFormated = self.Value
    
    def __repr__(self):
        return '{}: {}'.format(self.Range, self.Value)

class Table:
    
    def __init__(self):
        self.Name = None
        self.Origin = None
        self.Cells = {}
        self.ColumnWidths = {}
        self.RowSpacing = 1
        self.TextHeight = 1
    
    def addCell(self, _key, _cell):
        self.Cells[_key] = _cell
        self.ColumnWidths[_key[0]] = 1 # Default
        
    def __repr__(self):
        txt = 'Data Table [{}]: \n'.format(self.Name)
        for key in sorted(self.Cells.keys()):
            txt = txt + '{} \n'.format( self.Cells[key])
        return txt
    
    def sortToColumns(self):
        """Sorts the Table's cells to columns based on Alpha char
        
        something, something. Don't really remember now.
        """
        newDict = {}
        
        for key in sorted(self.Cells.keys()):
            col = key[0]
            
            if col in newDict.keys():
                newDict[col].append(self.Cells[key])
            else:
                newDict[col] = [self.Cells[key]]
        
        return newDict
    
    def locateCells(self, _colWidths, _default=10):
        """Set the self.Locate of each Cell Object in the Table
        
        Sets the right location for each cell in the table based on the
        input values of 'columnWidths_' and 'rowHeight_'. Will go through
        and change the 'Location' parameter for each Cell object found
        """
        
        self.udColWidths = { chr(k+65):v for k,v in enumerate(_colWidths) } #+65 to get to Capital Alphas
        
        for keyCount, key in enumerate(sorted(self.ColumnWidths.keys())):
            width = self.udColWidths.get(key, self.udColWidths.get('A', _default))
            self.ColumnWidths[key] = float(width)
        
        # Set the Cell Centers Based on the Column Widths
        if not self.Origin:
            self.Origin = Rhino.Geometry.Point3d(0,0,0)
        
        data = self.sortToColumns()
        colXPos = 0 + self.Origin.X
        for col in sorted(data.keys()):
            colYPos = 0 + self.Origin.Y
            for cell in data[col]:
                cell.Location = Rhino.Geometry.Point3d(colXPos,colYPos,0)
                colYPos = colYPos - self.RowSpacing
            colXPos = colXPos + self.ColumnWidths[col]
    
    def getHeaders(self):
        """Finds all the unique Header values in the Table
        
        Sets the self.Headers of the Instance. Looks for any Column with a '01'
        as the last values in the Column string, uses those as the headers
        (assumes this first line is the header line)
        """
        
        self.Headers = {}
        for key in self.Cells.keys():
            if '01' in key:
                self.Headers[key] = self.Cells[key].Value
    
    def findUniqueZoneNames(self):
        """Finds all the unique Zone values in the Table
        
        Sets the Object Instance 'ZoneList' param as a list of all the unique
        Zone names found in the cells. Looks for any 'Zone' header and uses
        that column's values to evaluate
        """
        
        # Find the Zone index of the passed in headers, if there is one
        self.getHeaders()
        for key, val in self.Headers.items():
            if 'ZONE' in val.upper():
                zoneIndex = ord(key[0])-65
            else:
                zoneIndex = 0
        
        # Find all the Unique zones passed in
        uniqueZones = []
        for key in sorted(myTable.Cells.keys()):
            if '01' not in key: # Don't include the header row
                if key[0] == chr(zoneIndex+65):
                    uniqueZones.append(myTable.Cells[key].Value)
        
        self.ZoneList = sorted(set(uniqueZones))
        return self.ZoneList
    
    def getCellsByZone(self):
        """Split the table by Zone name
        
        Splits an existing table based on the unique Zones found
        Note will not adjust the cell locations though.... grr.....
        So not that usefull.....
        """
        
        cellsByZone = DataTree[Object]()
        self.findUniqueZoneNames()
        
        for zoneCount, zone in enumerate(self.ZoneList):
            for zoneKey in sorted(self.Cells.keys()):
                if zone in str(self.Cells[zoneKey].Value):
                    # Found the Row's number. Now pull all the cells for that row
                    row = []
                    for key in sorted(self.Cells.keys()):
                        if zoneKey[1:] == self.Cells[key].Row:
                            row.append( self.Cells[key] )
                    cellsByZone.Add(row, GH_Path(zoneCount))
        
        return cellsByZone

def validateInputs(_header, _rows, _columnWidths, _rowHeight, _txtHeight):
    _rowHeight = _rowHeight if _rowHeight else 5
    _txtHeight = _txtHeight if _txtHeight else 2
    
    dataMatchError = False
    if _header and _rows.BranchCount > 0:
        # Check data and header lengths....
        for branchCount, branch in enumerate(_rows.Branches):
            if len(branch) == len(_header):
                pass
            else:
                dataMatchError = True
                warning = "The length of the '_header' input doesn't match the length of the data in branch numer: {}".format(branchCount)
                ghenv.Component.AddRuntimeMessage(ghK.GH_RuntimeMessageLevel.Warning, warning)
                break
        
        # Check columnWidths_ inputs....
        if len(_columnWidths) == 0:
            _columnWidths =  [20] * len(_header)
        elif len(_columnWidths) > 0 and  len(_columnWidths) != len(_header):
            _columnWidths =  [_columnWidths[0]] * len(_header)
    
    return dataMatchError, _columnWidths, _rowHeight, _txtHeight

dataMatchError, columnWidths_, rowHeight_, txtHeight_ = validateInputs(_header, _rows, columnWidths_, rowHeight_, txtHeight_)
tables = DataTree[Object]()

if _rows.BranchCount > 0 and not dataMatchError:
    # Get all the unique Zone Names
    # Item row[0] is used assuming the first item is always the zone name?
    zoneNames = sorted(set([row[0] for row in _rows.Branches]))
    
    # Create the Zone Data Tables and add to output Tree
    for zoneNum, zoneName in enumerate(zoneNames):
        # Get the this Zone's data as a List of lists
        zoneData = [row for row in _rows.Branches if row[0] == zoneName]
        
        # Build a table from the Zone Data
        myTable = Table()
        myTable.Name = zoneName
        myTable.Origin = rs.coerce3dpoint(tableOrigin_) if rs.coerce3dpoint(tableOrigin_) else None
        myTable.RowSpacing = rowHeight_
        myTable.TextHeight = txtHeight_
        
        for columnCount, header in enumerate(_header):
            # Get the Headers, add to the table
            try: headerTxt = header
            except: headerTxt = 'Missing'
            range = '{}{:02d}'.format(chr(columnCount+65), 1)
            myTable.addCell(range, Table_Cell(range, headerTxt, myTable.TextHeight))
            
            # Get the Table Data, add to the table
            for rowCount, rowData in enumerate(zoneData):
                if len(rowData) != 0:
                    range = '{}{:02d}'.format(chr(columnCount+65), rowCount+2) # data row
                    myTable.addCell(range, Table_Cell(range, rowData[columnCount], myTable.TextHeight))
            myTable.locateCells(columnWidths_)
            
        tables.Add(myTable, GH_Path(zoneNum))

# Table Preview
if preview_ !=None and _rows.BranchCount > 0 and header:
    showPreview = True
    previewTable = tables.Branch(int(preview_))[0].Cells
else:
    showPreview = False
    previewTable = None
showafterscript(previewTable, showPreview)
