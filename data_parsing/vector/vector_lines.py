import pandas as pd
import logging
import traceback
import pandapower as pp
import re

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Mapping of feeder codes to substation names
FEEDER_TO_SUBSTATION = {
    'BKBY': 'BROOKBY 33kV',
    'MARA': 'MARAETAI 33/11kV',
    'CLEV': 'CLEVEDON 33/11kV',
    'TTAK': 'TAKANINI 33/11kV',
    'ORAT': 'ORATIA 33/11KV',
    'LAIN': 'LAINGHOLM 33/11KV',
    'TPTAK': 'TP TAKANINI 220/33KV',
    'SPUR': 'SPUR RD 33/11KV',
    'HORS': 'HORSESHOE BUSH',
    'KKAP': 'KAUKAPAKAPA',
    'HELE': 'HELENSVILLE 33/11KV',
    'TWEL': 'TP Wellsford 110/33 kV POS',
    'WARK': 'WARKWORTH 33/11KV',
    'SNEL': 'SNELLS BEACH 33/11KV',
    'WELL': 'WELLSFORD 33/11KV',
    'MTW': 'MT WELLINGTON 33/11kV',
}

def extract_substation_name(feeder_name):
    """Extract the base substation name from a feeder name.
    Example: 'BKBY H02 - MARA H06' -> ('BROOKBY 33kV', 'MARAETAI 33/11kV')
    """
    try:
        # Split on ' - ' and take the first part
        parts = feeder_name.split(' - ')
        if len(parts) != 2:
            logger.warning(f"Invalid feeder name format (no ' - ' separator): {feeder_name}")
            return None
        
        # Extract the base code (before any numbers or spaces)
        from_code = re.match(r'([A-Z]+)', parts[0])
        to_code = re.match(r'([A-Z]+)', parts[1])
        
        if not from_code or not to_code:
            logger.warning(f"Could not extract codes from feeder name: {feeder_name}")
            return None
        
        from_code = from_code.group(1)
        to_code = to_code.group(1)
        
        # Look up the actual substation names
        from_sub = FEEDER_TO_SUBSTATION.get(from_code)
        to_sub = FEEDER_TO_SUBSTATION.get(to_code)
        
        if not from_sub or not to_sub:
            logger.warning(f"Unknown substation code in feeder name {feeder_name}: from={from_code}, to={to_code}")
            return None
        
        return from_sub, to_sub
    except Exception as e:
        logger.error(f"Error parsing feeder name {feeder_name}: {e}")
        return None

def load_vector_lines(net):
    """Load Vector distribution lines from CSV and add them to the network"""
    try:
        logger.info("Loading Vector distribution lines from CSV")
        lines_df = pd.read_csv('data/Vector/distribution_feeder_network_and_zone_substations_4095785886967079183.csv')
        logger.info(f"Loaded {len(lines_df)} Vector lines")
        
        # Create a mapping of substation names to bus indices
        substation_to_bus = {}
        for bus_idx, bus in net.bus.iterrows():
            substation_to_bus[bus['name']] = bus_idx
            logger.debug(f"Mapped substation {bus['name']} to bus {bus_idx}")
        
        # Create lines between buses
        for idx, row in lines_df.iterrows():
            try:
                # Parse feeder name to get from and to substations
                feeder_name = row['Feeder Name']
                substation_names = extract_substation_name(feeder_name)
                
                if not substation_names:
                    continue
                
                from_sub, to_sub = substation_names
                from_bus_idx = substation_to_bus.get(from_sub)
                to_bus_idx = substation_to_bus.get(to_sub)
                
                if from_bus_idx is None or to_bus_idx is None:
                    logger.warning(f"Could not find bus indices for line {feeder_name} (from: {from_sub}, to: {to_sub})")
                    continue
                
                # Get voltage from OPVOLTAGE_ column
                voltage = 33.0  # Default to 33kV
                if '11' in str(row['OPVOLTAGE_']):
                    voltage = 11.0
                
                # Create line with parameters
                pp.create_line_from_parameters(
                    net,
                    from_bus=from_bus_idx,
                    to_bus=to_bus_idx,
                    length_km=float(row['Shape__Length']) / 1000.0,  # Convert to km
                    r_ohm_per_km=0.1,  # Default resistance
                    x_ohm_per_km=0.3,  # Default reactance
                    c_nf_per_km=10.0,  # Default capacitance
                    max_i_ka=1.0,  # Default max current
                    name=feeder_name
                )
                
                logger.debug(f"Created line {feeder_name} connecting buses {from_sub} and {to_sub}")
            except Exception as e:
                logger.error(f"Error processing line {feeder_name}: {e}")
                continue
        
        logger.info(f"Created {len(net.line)} lines in the Vector network")
        return net
    except Exception as e:
        logger.error(f"Error loading Vector lines: {e}")
        logger.error(traceback.format_exc())
        return None 