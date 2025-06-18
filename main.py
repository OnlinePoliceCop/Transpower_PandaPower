from flask import Flask, render_template, jsonify
import logging
import traceback
from data_parsing.transpower.transpower_data_parser import create_transpower_network
from data_parsing.transpower.transpower_lines import load_transmission_lines
from data_parsing.vector.vector_data_parser import create_vector_network

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/network_data')
def get_network_data():
    try:
        logger.info("Starting to fetch network data...")
        
        # Create Transpower network
        logger.info("Creating Transpower network...")
        transpower_net, transpower_bus_data = create_transpower_network()
        if transpower_net is None:
            logger.error("Failed to create Transpower network")
            return jsonify({"error": "Failed to create Transpower network"}), 500
        logger.info(f"Successfully created Transpower network with {len(transpower_bus_data)} buses")

        # Load Transpower transmission lines
        logger.info("Loading Transpower transmission lines...")
        load_transmission_lines(transpower_net)
        logger.info(f"Loaded {len(transpower_net.line)} Transpower lines")

        # Create Vector network
        logger.info("Creating Vector network...")
        vector_net, vector_bus_data = create_vector_network()
        if vector_net is None:
            logger.error("Failed to create Vector network")
            return jsonify({"error": "Failed to create Vector network"}), 500
        logger.info(f"Successfully created Vector network with {len(vector_bus_data)} buses")

        # Prepare data for the map
        map_data = {
            'transpower': {
                'substations': [],
                'lines': []
            },
            'vector': {
                'substations': [],
                'lines': []
            }
        }

        # Process Transpower data
        logger.info("Processing Transpower data for map...")
        for bus in transpower_bus_data:
            map_data['transpower']['substations'].append({
                'name': bus['name'],
                'type': bus['type'],
                'description': bus['description'],
                'lat': bus['lat'],
                'lon': bus['lon']
            })

        # Add Transpower lines
        logger.info("Processing Transpower lines...")
        logger.info(f"Line columns: {transpower_net.line.columns}")
        for _, line in transpower_net.line.iterrows():
            from_bus = transpower_net.bus.iloc[line['from_bus']]
            to_bus = transpower_net.bus.iloc[line['to_bus']]
            # Get voltage from the from_bus since that's where the line starts
            voltage = str(from_bus['vn_kv'])
            map_data['transpower']['lines'].append({
                'name': line['name'],
                'from_bus': from_bus['name'],
                'to_bus': to_bus['name'],
                'voltage': voltage,
                'description': line.get('description', '')
            })

        # Process Vector data
        logger.info("Processing Vector data for map...")
        for bus in vector_bus_data:
            map_data['vector']['substations'].append({
                'name': bus['name'],
                'type': bus['type'],
                'description': bus['description'],
                'lat': bus['lat'],
                'lon': bus['lon']
            })

        logger.info(f"Prepared {len(map_data['transpower']['substations'])} Transpower substations for map")
        logger.info(f"Prepared {len(map_data['transpower']['lines'])} Transpower lines for map")
        logger.info(f"Prepared {len(map_data['vector']['substations'])} Vector substations for map")
        
        return jsonify(map_data)
    except Exception as e:
        logger.error(f"Error in get_network_data: {e}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001) 