import pandas as pd
import pandapower as pp
from pyproj import Transformer
import logging
import traceback
import os
import json

logger = logging.getLogger(__name__)

def nztm_to_wgs84(x, y):
    """Convert NZTM coordinates to WGS84 (latitude/longitude)"""
    try:
        transformer = Transformer.from_crs("EPSG:2193", "EPSG:4326", always_xy=True)
        lon, lat = transformer.transform(float(x), float(y))
        return lat, lon
    except Exception as e:
        logger.error(f"Error converting coordinates: {e}")
        logger.error(traceback.format_exc())
        return None, None

def create_substation_files(net, bus_data):
    """Create individual files for each substation containing their data and connections."""
    try:
        # Create directory for substation files if it doesn't exist
        substation_dir = 'data/Transpower/substations'
        os.makedirs(substation_dir, exist_ok=True)
        
        # Process each bus/substation
        for idx, bus in net.bus.iterrows():
            try:
                # Get substation name
                substation_name = str(bus['name'])
                
                # Find all lines connected to this substation
                connected_lines = []
                for line_idx, line in net.line.iterrows():
                    if line['from_bus'] == idx or line['to_bus'] == idx:
                        # Get the other end of the line
                        other_bus_idx = line['to_bus'] if line['from_bus'] == idx else line['from_bus']
                        other_bus = net.bus.iloc[other_bus_idx]
                        
                        connected_lines.append({
                            'id': int(line_idx),
                            'name': str(line['name']),
                            'connected_to': str(other_bus['name']),
                            'voltage_kv': float(bus['vn_kv']),
                            'length_km': float(line['length_km']),
                            'r_ohm_per_km': float(line['r_ohm_per_km']),
                            'x_ohm_per_km': float(line['x_ohm_per_km']),
                            'c_nf_per_km': float(line['c_nf_per_km']),
                            'max_i_ka': float(line['max_i_ka'])
                        })
                
                # Create substation data object
                substation_data = {
                    'name': substation_name,
                    'voltage_kv': float(bus['vn_kv']),
                    'coordinates': {
                        'nztm': {
                            'x': float(bus['geodata'][0]),
                            'y': float(bus['geodata'][1])
                        }
                    },
                    'connected_lines': connected_lines,
                    'type': 'transpower'
                }
                
                # Convert coordinates to WGS84
                lat, lon = nztm_to_wgs84(bus['geodata'][0], bus['geodata'][1])
                if lat is not None and lon is not None:
                    substation_data['coordinates']['wgs84'] = {
                        'lat': lat,
                        'lon': lon
                    }
                
                # Save to file
                filename = f"{substation_dir}/{substation_name}.json"
                with open(filename, 'w') as f:
                    json.dump(substation_data, f, indent=2)
                
                logger.info(f"Created substation file for {substation_name}")
                
            except Exception as e:
                logger.error(f"Error processing substation {bus['name']}: {e}")
                logger.error(traceback.format_exc())
                continue
        
        logger.info(f"Created substation files in {substation_dir}")
        return True
    except Exception as e:
        logger.error(f"Error creating substation files: {e}")
        logger.error(traceback.format_exc())
        return False

def create_transpower_network():
    """Create a pandapower network and load Transpower sites as buses. Return the network and a list of bus info for mapping."""
    try:
        logger.info("Creating new pandapower network")
        net = pp.create_empty_network(name="TransNet")
        logger.info("Loading sites data from CSV")
        sites_df = pd.read_csv('data/Transpower/Sites.csv')
        logger.info(f"Loaded {len(sites_df)} sites")
        bus_data = []
        
        # Add buses to the network
        for idx, row in sites_df.iterrows():
            try:
                lat, lon = nztm_to_wgs84(row['X'], row['Y'])
                if lat is None or lon is None:
                    logger.warning(f"Could not convert coordinates for site {row['MXLOCATION']}")
                    continue
                
                # Create bus with geodata as a tuple (x, y)
                bus_idx = pp.create_bus(
                    net,
                    name=str(row['MXLOCATION']),
                    vn_kv=110.0,  # Default voltage level
                    in_service=True,
                    geodata=(float(row['X']), float(row['Y']))  # Store NZTM coordinates
                )
                
                # Store bus data with both coordinate systems
                bus_data.append({
                    'bus_idx': bus_idx,
                    'name': str(row['MXLOCATION']),
                    'type': str(row['type']),
                    'description': str(row['description']),
                    'lat': lat,
                    'lon': lon,
                    'x': float(row['X']),
                    'y': float(row['Y'])
                })
                logger.debug(f"Created bus {bus_idx} for site {row['MXLOCATION']}")
            except Exception as e:
                logger.error(f"Error processing site {row['MXLOCATION']}: {e}")
                logger.error(traceback.format_exc())
                continue
        
        logger.info(f"Created {len(bus_data)} buses in the network")
        
        # Create individual files for each substation
        create_substation_files(net, bus_data)
        
        return net, bus_data
    except Exception as e:
        logger.error(f"Error creating network: {e}")
        logger.error(traceback.format_exc())
        return None, None 