import pandas as pd
import pandapower as pp
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_network_creation():
    try:
        # Create network
        net = pp.create_empty_network(name="TestNet")
        logger.info("Created empty network")

        # Load sites
        sites_df = pd.read_csv('data/Transpower/Sites.csv')
        logger.info(f"Loaded {len(sites_df)} sites")

        # Create buses
        for idx, row in sites_df.iterrows():
            pp.create_bus(
                net,
                name=str(row['MXLOCATION']),
                vn_kv=110.0,
                in_service=True
            )
        logger.info(f"Created {len(net.bus)} buses")

        # Load lines
        lines_df = pd.read_csv('data/Transpower/Transmission_Lines.csv')
        logger.info(f"Loaded {len(lines_df)} lines")

        # Create lines
        for idx, row in lines_df.iterrows():
            mxlocation = str(row['MXLOCATION'])
            parts = mxlocation.split('-')
            if len(parts) >= 2:
                start_bus_name = parts[0]
                end_bus_name = parts[1]
                start_bus_idx = net.bus[net.bus['name'] == start_bus_name].index
                end_bus_idx = net.bus[net.bus['name'] == end_bus_name].index
                if len(start_bus_idx) > 0 and len(end_bus_idx) > 0:
                    start_bus_idx = start_bus_idx[0]
                    end_bus_idx = end_bus_idx[0]
                    pp.create_line_from_parameters(
                        net,
                        from_bus=start_bus_idx,
                        to_bus=end_bus_idx,
                        length_km=1.0,
                        r_ohm_per_km=0.1,
                        x_ohm_per_km=0.1,
                        c_nf_per_km=10.0,
                        max_i_ka=1.0,
                        name=mxlocation
                    )
        logger.info(f"Created {len(net.line)} lines")

        return True
    except Exception as e:
        logger.error(f"Error in test: {e}")
        return False

if __name__ == "__main__":
    success = test_network_creation()
    print(f"Test {'succeeded' if success else 'failed'}") 