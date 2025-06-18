import pandas as pd
import pandapower as pp
from pyproj import Transformer
import logging
import traceback

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
        return net, bus_data
    except Exception as e:
        logger.error(f"Error creating network: {e}")
        logger.error(traceback.format_exc())
        return None, None 