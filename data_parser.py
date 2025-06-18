import pandas as pd
import geopandas as gpd
from pyproj import Transformer
import numpy as np 

file_path = 'Transpower/Sites.csv'

try:
    transpower_sites = pd.read_csv(file_path)
    print("Successfully loaded Sites.csv into a DataFrame:")
    print(transpower_sites.head())
    print("\nDataFrame Info:")
    transpower_sites.info()

    # --- Step 1: Convert NZTM (EPSG:2193) to WGS84 (EPSG:4326) ---
    # X, Y coordinates are likely in NZTM (New Zealand Transverse Mercator).
    # GeoJSON typically uses WGS84 (longitude, latitude).
    # We'll use pyproj for this conversion.

    # Define the transformer: from NZTM to WGS84
    # The order of coordinates in WGS84 is (longitude, latitude)
    transformer = Transformer.from_crs("epsg:2193", "epsg:4326", always_xy=True) # always_xy=True ensures (lon, lat) output

    # Apply the transformation to X and Y columns
    # We convert the pandas Series to numpy arrays for efficiency
    # and to handle potential NaN values correctly during conversion
    lon, lat = transformer.transform(transpower_sites['X'].values, transpower_sites['Y'].values)

    # Add the new longitude and latitude columns to the DataFrame
    transpower_sites['longitude'] = lon
    transpower_sites['latitude'] = lat

    print("\nDataFrame after NZTM to WGS84 conversion:")
    print(transpower_sites[['MXLOCATION', 'X', 'Y', 'longitude', 'latitude']].head())

    # --- Step 2: Convert DataFrame to GeoDataFrame for GeoJSON export ---
    # GeoPandas is excellent for working with spatial data and exporting to GeoJSON.

    # Create shapely Point geometries from longitude and latitude
    # Note: GeoJSON expects (longitude, latitude)
    geometry = gpd.points_from_xy(transpower_sites['longitude'], transpower_sites['latitude'])

    # Create a GeoDataFrame
    gdf_sites = gpd.GeoDataFrame(transpower_sites, geometry=geometry, crs="epsg:4326")

    # --- Step 3: Export to GeoJSON ---
    output_geojson_path = 'Transpower/sites.geojson'
    gdf_sites.to_file(output_geojson_path, driver='GeoJSON')

    print(f"\nSuccessfully exported to {output_geojson_path}")


except FileNotFoundError:
    print(f"Error: The file '{file_path}' was not found.")
    print("Please make sure the CSV file is in the correct directory.")
except Exception as e:
    print(f"An error occurred: {e}")