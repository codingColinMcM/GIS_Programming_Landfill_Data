# Import the arcpy module for geospatial analysis
import arcpy
import os

# Print a "Run summary" message to indicate the start of the script
arcpy.AddMessage("Run summary")

# Read an integer parameter (PD_NO) from the user
pdnum = int(arcpy.GetParameterAsText(0))
arcpy.AddMessage(f"    PD {pdnum} selected")

# Create a new File Geodatabase (GDB) with a name containing the PD_NO
output_gdb_path = os.path.join(os.getcwd(), f"McMurtrayGDB_{pdnum}.gdb")
arcpy.CreateFileGDB_management(output_gdb_path)

# Set the workspace (input directory) to the Lab11_Data folder
inputDir = os.path.join(os.getcwd(), "Lab11_Data")
arcpy.env.workspace = inputDir

# Define the output boundary feature layer based on the PD_NO query
outputBoundary = os.path.join(output_gdb_path, f"boundary_{pdnum}")
arcpy.management.MakeFeatureLayer("vapdbounds.shp", outputBoundary, f"\"PD_NO\" = \'{pdnum}\'")

# Specify input shapefiles for rivers and roads
inputRivers = "varivers.shp"
inputRoads = "vards.shp"

# Perform intersection analysis between boundary and roads, rivers, and landfills
intersectRoads = os.path.join(output_gdb_path, f"roads_{pdnum}")
intersectRivers = os.path.join(output_gdb_path, f"rivers_{pdnum}")
intersectLandfills = os.path.join(output_gdb_path, f"landfills_{pdnum}")

arcpy.analysis.Intersect([inputRoads, outputBoundary], intersectRoads)
arcpy.analysis.Intersect([inputRivers, outputBoundary], intersectRivers)
arcpy.analysis.Intersect(["landfills.shp", outputBoundary], intersectLandfills)

# Count the number of landfills located within the boundary
countLandfills = arcpy.GetCount_management(intersectLandfills)
arcpy.AddMessage(f"    {countLandfills} landfills were located in PD {pdnum}")

# Read buffer distances for roads and rivers from user parameters
bufferRoadsInt = int(arcpy.GetParameterAsText(1))
bufferRiversInt = int(arcpy.GetParameterAsText(2))

# Create buffer polygons around roads and rivers based on user-defined distances
outputRoadsBuffer = rf"memory\roadsBuffer_{pdnum}"
outputRiversBuffer = rf"memory\riversBuffer_{pdnum}"
arcpy.AddMessage("    Buffers of roads and rivers defined in memory.")

arcpy.analysis.Buffer(intersectRoads, outputRoadsBuffer, bufferRoadsInt)
arcpy.analysis.Buffer(intersectRivers, outputRiversBuffer, bufferRiversInt)

# Calculate the intersection between landfills and road and river buffers
landfillsIntersectRoads = rf"memory\roadsIntersectLandfills_{pdnum}"
landfillsIntersectRivers = rf"memory\riversIntersectLandfills_{pdnum}"
arcpy.AddMessage("    Intersects of both buffers and landfills defined in memory.")

arcpy.analysis.Intersect([intersectLandfills, outputRoadsBuffer], landfillsIntersectRoads)
arcpy.analysis.Intersect([intersectLandfills, outputRiversBuffer], landfillsIntersectRivers)

# Calculate the erase operation between landfills and road and river buffers
landfillsOutsideRoads = rf"memory\roadsEraseLandfills_{pdnum}"
landfillsOutsideRivers = rf"memory\riversEraseLandfills_{pdnum}"
arcpy.AddMessage("    Erases of both buffers on landfills defined in memory.")

arcpy.analysis.Erase(intersectLandfills, outputRoadsBuffer, landfillsOutsideRoads)
arcpy.analysis.Erase(intersectLandfills, outputRiversBuffer, landfillsOutsideRivers)

# Calculate the intersection between the resulting road and river erase outputs
landfillsOutsideRoadsAndRivers = os.path.join(output_gdb_path, f"erasesIntersect_{pdnum}")
arcpy.analysis.Intersect([landfillsOutsideRivers, landfillsOutsideRoads], landfillsOutsideRoadsAndRivers)

# Count the number of landfills within road and river buffers, as well as outside the buffers
countRoadIntersect = arcpy.GetCount_management(landfillsIntersectRoads)
countRiverIntersect = arcpy.GetCount_management(landfillsIntersectRivers)
countRoadErase = arcpy.GetCount_management(landfillsOutsideRoads)
countRiverErase = arcpy.GetCount_management(landfillsOutsideRivers)
countEraseIntersect = arcpy.GetCount_management(landfillsOutsideRoadsAndRivers)

# Print the results
arcpy.AddMessage("")
arcpy.AddMessage("    Road Buffer is complete")
arcpy.AddMessage(f"        {countRoadIntersect} landfills are within the {bufferRoadsInt} meter road buffer")
arcpy.AddMessage(f"        {countRoadErase} landfill(s) located more than {bufferRoadsInt} meters from a road")
arcpy.AddMessage("")
arcpy.AddMessage("    River Buffer is complete")
arcpy.AddMessage(f"        {countRiverIntersect} landfills are within the {bufferRiversInt} meter river buffer")
arcpy.AddMessage(f"        {countRiverErase} landfill(s) located more than {bufferRiversInt} meters from a river")
arcpy.AddMessage(f"***{countEraseIntersect} landfills fell outside both buffers***")
