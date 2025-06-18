from flask import Flask, render_template, jsonify
import logging
import traceback
from sites import create_transpower_network
from lines import load_transmission_lines

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/network_data')
def network_data():
    try:
        net, bus_data = create_transpower_network()
        if net is None or bus_data is None:
            return jsonify({'error': 'Failed to create network'})
        
        # Load transmission lines into the network
        load_transmission_lines(net)
        
        # Create a mapping of bus indices to bus names
        bus_name_map = {bus['bus_idx']: bus['name'] for bus in bus_data}
        
        # Prepare data for the map
        map_data = {
            'substations': {
                bus['name']: {
                    'name': bus['name'],
                    'type': bus['type'],
                    'lat': bus['lat'],
                    'lon': bus['lon']
                }
                for bus in bus_data
            },
            'lines': [
                {
                    'name': line['name'],
                    'from_bus': bus_name_map.get(line['from_bus'], ''),
                    'to_bus': bus_name_map.get(line['to_bus'], '')
                }
                for _, line in net.line.iterrows()
            ]
        }
        
        logger.debug(f"Prepared map data with {len(map_data['substations'])} substations and {len(map_data['lines'])} lines")
        return jsonify(map_data)
    except Exception as e:
        logger.error(f"Error in network_data route: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5001) 