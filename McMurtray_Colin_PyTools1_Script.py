# Import the arcpy module for geospatial analysis
import arcpy
import os

# Print a "Run summary" message to indicate the start of the script
print("Run summary")

# Read an integer parameter (PD_NO) from the user
pdnum = int(arcpy.GetParameterAsText("    Whereclause used: 'PD_NO'="))
print(f"    PD {pdnum} selected")

# Create a new File Geodatabase (GDB) with a name containing the PD_NO
output_gdb_path = os.path.join(os.getcwd(), f"McMurtrayGDB_{pdnum}.gdb")
arcpy.CreateFileGDB_management(output_gdb_path)

# Set the workspace (input directory) to the Lab11_Data folder
arcpy.env.workspace = os.path.join(os.getcwd(), "Lab11_Data")

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

# Count the number of landfills located within the boundary
countLandfills = arcpy.GetCount_management(intersectLandfills)
print(f"    {countLandfills} landfills were located in PD {pdnum}")

# Prompt the user to input criteria for road and river buffer distances
bufferRoadsInt = int(input("    Criteria road distance = "))
bufferRiversInt = int(input("    Criteria river distance = "))

# Create buffer polygons around roads and rivers based on user-defined distances
outputRoadsBuffer = os.path.join("memory", f"roadsBuffer_{pdnum}")
outputRiversBuffer = os.path.join("memory", f"riversBuffer_{pdnum}")
print("    Buffers of roads and rivers defined in memory.")
arcpy.analysis.Buffer(intersectRoads, outputRoadsBuffer, bufferRoadsInt)
arcpy.analysis.Buffer(intersectRivers, outputRiversBuffer, bufferRiversInt)

# Calculate the intersection between landfills and road and river buffers
landfillsIntersectRoads = os.path.join("memory", f"roadsIntersectLandfills_{pdnum}")
landfillsIntersectRivers = os.path.join("memory", f"riversIntersectLandfills_{pdnum}")
print("    Intersects of both buffers and landfills defined in memory.")
arcpy.analysis.Intersect([intersectLandfills, outputRoadsBuffer], landfillsIntersectRoads)
arcpy.analysis.Intersect([intersectLandfills, outputRiversBuffer], landfillsIntersectRivers)

# Calculate the erase operation between landfills and road and river buffers
landfillsOutsideRoads = os.path.join("memory", f"roadsEraseLandfills_{pdnum}")
landfillsOutsideRivers = os.path.join("memory", f"riversEraseLandfills_{pdnum}")
print("    Erases of both buffers on landfills defined in memory.")
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
print("")
print("    Road Buffer is complete")
print(f"        {countRoadIntersect} landfills are within the {bufferRoadsInt} meter road buffer")
print(f"        {countRoadErase} landfill(s) located more than {bufferRoadsInt} meters from a road")
print("")
print("    River Buffer is complete")
print(f"        {countRiverIntersect} landfills are within the {bufferRiversInt} meter river buffer")
print(f"        {countRiverErase} landfill(s) located more than {bufferRiversInt} meters from a river")
print("")
print(f"***{countEraseIntersect} landfills fell outside both buffers***")
