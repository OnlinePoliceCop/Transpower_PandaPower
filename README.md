<<<<<<< HEAD
# New Zealand Power Network Visualization

This project provides an interactive visualization of New Zealand's power network, including transmission lines and substations. The visualization allows users to explore different voltage levels and network components through an interactive map interface.

## Features

- Interactive map visualization of the NZ power network
- Layer controls for different voltage levels (400kV, 350kV, 220kV, 110kV, 66kV)
- Filtering by network component types (Transmission Lines, Cables, AC Substations, HVDC Stations)
- Detailed information about substations and their connections
- Color-coded transmission lines based on voltage levels
- Responsive design for desktop and mobile devices

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Flask application:
```bash
python app.py
```

3. Open your web browser and navigate to:
```
http://localhost:5000
```

## Data Sources

The application uses two main data files:
- `Transmission_Lines.csv`: Contains information about transmission lines and cables
- `Sites.csv`: Contains information about substations and their locations

## Future Enhancements

- Substation isolation functionality
- Connection studies for network components
- Real-time network status updates
- Additional network analysis tools
- Export functionality for network data

## Technologies Used

- Backend: Python/Flask
- Frontend: HTML, CSS, JavaScript
- Mapping: Leaflet.js
- Data Processing: Pandas, GeoPandas
- Styling: Bootstrap 5 
=======
# Transpower_PandaPower
A project with the aim of being able to do small power systems studies by adding a network node and being able to get the distance to the nearest substation and be able to perform power systems analysis studies on a new potential load or generator.
>>>>>>> 1911934d68f4cdda077caadb7c47af1e4fa46dc6
