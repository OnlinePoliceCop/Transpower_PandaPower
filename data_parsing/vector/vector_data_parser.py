import pandas as pd
import logging
import traceback
from pyproj import Transformer
import pandapower as pp

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def nztm_to_wgs84(x, y):
    """Convert NZTM coordinates to WGS84 (latitude/longitude)."""
    try:
        transformer = Transformer.from_crs("EPSG:2193", "EPSG:4326", always_xy=True)
        lon, lat = transformer.transform(x, y)
        return lat, lon
    except Exception as e:
        logger.error(f"Error converting coordinates: {e}")
        logger.error(traceback.format_exc())
        return None, None

def create_vector_network():
    """Create a pandapower network and load Vector sites as buses. Return the network and a list of bus info for mapping."""
    try:
        logger.info("Creating new pandapower network for Vector")
        net = pp.create_empty_network(name="VectorNet")
        logger.info("Loading Vector sites data from CSV")
        sites_df = pd.read_csv('data/Vector/distribution_feeder_network_and_zone_substations_5064571612058702982.csv')
        logger.info(f"Loaded {len(sites_df)} Vector sites")
        bus_data = []
        
        # Add buses to the network
        for idx, row in sites_df.iterrows():
            try:
                lat, lon = nztm_to_wgs84(row['x'], row['y'])
                if lat is None or lon is None:
                    logger.warning(f"Could not convert coordinates for Vector site {row['Primary Substation Name']}")
                    continue
                
                # Create bus with geodata as a tuple (x, y)
                bus_idx = pp.create_bus(
                    net,
                    name=str(row['Primary Substation Name']),
                    vn_kv=110.0,  # Default voltage level
                    in_service=True,
                    geodata=(float(row['x']), float(row['y']))  # Store NZTM coordinates
                )
                
                # Extract voltage from the name (e.g., "MANUREWA 33/11KV" -> "33/11KV")
                voltage = row['Primary Substation Name'].split(' ')[-1] if ' ' in row['Primary Substation Name'] else 'Unknown'
                
                # Store bus data with both coordinate systems
                bus_data.append({
                    'bus_idx': bus_idx,
                    'name': str(row['Primary Substation Name']),
                    'type': 'Substation',
                    'description': f"Vector {voltage} Substation",
                    'lat': lat,
                    'lon': lon,
                    'x': float(row['x']),
                    'y': float(row['y'])
                })
                logger.debug(f"Created bus {bus_idx} for Vector site {row['Primary Substation Name']}")
            except Exception as e:
                logger.error(f"Error processing Vector site {row['Primary Substation Name']}: {e}")
                logger.error(traceback.format_exc())
                continue
        
        logger.info(f"Created {len(bus_data)} buses in the Vector network")
        return net, bus_data
    except Exception as e:
        logger.error(f"Error creating Vector network: {e}")
        logger.error(traceback.format_exc())
        return None, None 