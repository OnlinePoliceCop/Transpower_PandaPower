from flask import Flask, render_template, jsonify
import pandas as pd
import folium
from folium import plugins
import json
from shapely.geometry import LineString, Point
import geopandas as gpd
import numpy as np

app = Flask(__name__)

def load_network_data():
    # Load transmission lines
    lines_df = pd.read_csv('data/Transpower/Transmission_Lines.csv')
    
    # Load substations
    sites_df = pd.read_csv('data/Transpower/Sites.csv')
    
    # Load distribution network
    dist_df = pd.read_csv('data/Vector/distribution_feeder_network_and_zone_substations_5064571612058702982.csv')
    
    # Convert coordinates to proper format for transmission network
    sites_df['geometry'] = sites_df.apply(lambda row: Point(float(row['X']), float(row['Y'])), axis=1)
    sites_gdf = gpd.GeoDataFrame(sites_df, geometry='geometry', crs="EPSG:2193")
    
    # Convert to WGS84 (latitude/longitude)
    sites_gdf = sites_gdf.to_crs("EPSG:4326")
    
    # Create a dictionary of substation locations
    substation_locations = {}
    for _, row in sites_gdf.iterrows():
        substation_locations[row['MXLOCATION']] = {
            'lat': float(row.geometry.y),
            'lon': float(row.geometry.x),
            'name': str(row['description']),
            'type': str(row['type'])
        }
    
    # Process transmission lines
    lines_data = []
    for _, line in lines_df.iterrows():
        # Extract start and end points from MXLOCATION
        points = str(line['MXLOCATION']).split('-')
        if len(points) >= 2:
            start = points[0].strip()
            end = points[1].strip()
            
            if start in substation_locations and end in substation_locations:
                lines_data.append({
                    'start': start,
                    'end': end,
                    'voltage': float(line['designvolt']),
                    'type': str(line['type']),
                    'description': str(line['description']),
                    'start_coords': [substation_locations[start]['lat'], substation_locations[start]['lon']],
                    'end_coords': [substation_locations[end]['lat'], substation_locations[end]['lon']]
                })
    
    # Process distribution network
    distribution_data = []
    for _, row in dist_df.iterrows():
        try:
            # Convert coordinates to WGS84
            point = Point(float(row['x']), float(row['y']))
            point_gdf = gpd.GeoDataFrame(geometry=[point], crs="EPSG:2193")
            point_gdf = point_gdf.to_crs("EPSG:4326")
            
            # Extract coordinates from the converted point
            coords = point_gdf.geometry.iloc[0]
            
            distribution_data.append({
                'id': int(row['OBJECTID']),
                'name': str(row['Primary Substation Name']),
                'coordinates': [float(coords.y), float(coords.x)],  # [lat, lon]
                'type': 'distribution'  # Add type for frontend filtering
            })
        except (ValueError, TypeError) as e:
            print(f"Error processing distribution substation {row['OBJECTID']}: {e}")
            continue
    
    return substation_locations, lines_data, distribution_data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/network_data')
def network_data():
    substation_locations, lines_data, distribution_data = load_network_data()
    return jsonify({
        'substations': substation_locations,
        'lines': lines_data,
        'distribution': distribution_data
    })

if __name__ == '__main__':
    app.run(debug=True) 