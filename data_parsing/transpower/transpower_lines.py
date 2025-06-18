import pandas as pd
import logging
import traceback
import pandapower as pp

logger = logging.getLogger(__name__)

def load_transmission_lines(net):
    """Load transmission lines from CSV and create pandapower lines connecting the corresponding buses."""
    try:
        logger.info("Loading transmission lines from CSV")
        lines_df = pd.read_csv('data/Transpower/Transmission_Lines.csv')
        logger.info(f"Loaded {len(lines_df)} transmission lines")
        for idx, row in lines_df.iterrows():
            try:
                # Extract start and end bus names from MXLOCATION (e.g., 'AHA-DOB-A' -> 'AHA' and 'DOB')
                mxlocation = str(row['MXLOCATION'])
                parts = mxlocation.split('-')
                if len(parts) >= 2:
                    start_bus_name = parts[0]
                    end_bus_name = parts[1]
                    # Find the bus indices by name
                    start_bus_idx = net.bus[net.bus['name'] == start_bus_name].index
                    end_bus_idx = net.bus[net.bus['name'] == end_bus_name].index
                    if len(start_bus_idx) > 0 and len(end_bus_idx) > 0:
                        start_bus_idx = start_bus_idx[0]
                        end_bus_idx = end_bus_idx[0]
                        # Create a pandapower line connecting the buses
                        pp.create_line_from_parameters(
                            net,
                            from_bus=start_bus_idx,
                            to_bus=end_bus_idx,
                            length_km=1.0,  # Default length
                            r_ohm_per_km=0.1,  # Default resistance
                            x_ohm_per_km=0.1,  # Default reactance
                            c_nf_per_km=10.0,  # Default capacitance
                            max_i_ka=1.0,  # Default max current
                            name=mxlocation
                        )
                        logger.debug(f"Created line {mxlocation} connecting buses {start_bus_name} and {end_bus_name}")
                    else:
                        logger.warning(f"Could not find bus indices for line {mxlocation}")
                else:
                    logger.warning(f"Invalid MXLOCATION format for line {mxlocation}")
            except Exception as e:
                logger.error(f"Error processing line {row['MXLOCATION']}: {e}")
                logger.error(traceback.format_exc())
                continue
        logger.info(f"Created {len(net.line)} lines in the network")
    except Exception as e:
        logger.error(f"Error loading transmission lines: {e}")
        logger.error(traceback.format_exc()) 