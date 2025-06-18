// Initialize map centered on New Zealand
const map = L.map('map').setView([-40.9006, 174.8860], 6);

// Add OpenStreetMap base layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Layer groups for different voltage levels
const voltageLayers = {
    '220kV': L.layerGroup().addTo(map),
    '110kV': L.layerGroup().addTo(map),
    '66kV': L.layerGroup().addTo(map),
    '50kV': L.layerGroup().addTo(map),
    '33kV': L.layerGroup().addTo(map),
    '22kV': L.layerGroup().addTo(map),
    '11kV': L.layerGroup().addTo(map)
};

// Layer group for lines
const linesLayer = L.layerGroup().addTo(map);

// Layer groups for different component types
const componentLayers = {
    'Substations': L.layerGroup().addTo(map)
};

// Function to get color based on voltage
function getVoltageColor(voltage) {
    switch (voltage) {
        case '220kV': return '#FF0000';
        case '110kV': return '#FFA500';
        case '66kV': return '#FFFF00';
        case '50kV': return '#00FF00';
        case '33kV': return '#00FFFF';
        case '22kV': return '#0000FF';
        case '11kV': return '#800080';
        default: return '#808080';
    }
}

// Function to get line weight based on voltage
function getVoltageWeight(voltage) {
    const voltageWeights = {
        '220kV': 5,
        '110kV': 4,
        '66kV': 3.5,
        '50kV': 3,
        '33kV': 2.5,
        '22kV': 2,
        '11kV': 1.5
    };
    return voltageWeights[voltage] || 1;
}

// Function to update layer visibility
function updateLayerVisibility() {
    const voltageCheckboxes = document.querySelectorAll('input[name="voltage"]');
    voltageCheckboxes.forEach(checkbox => {
        const voltage = checkbox.value;
        if (checkbox.checked) {
            voltageLayers[voltage].addTo(map);
        } else {
            voltageLayers[voltage].remove();
        }
    });
    const componentCheckboxes = document.querySelectorAll('input[name="component"]');
    componentCheckboxes.forEach(checkbox => {
        const component = checkbox.value;
        if (component === 'Substations' && checkbox.checked) {
            Object.values(voltageLayers).forEach(layer => layer.addTo(map));
        } else if (component === 'Substations' && !checkbox.checked) {
            Object.values(voltageLayers).forEach(layer => layer.remove());
        }
        if (component === 'Lines' && checkbox.checked) {
            linesLayer.addTo(map);
        } else if (component === 'Lines' && !checkbox.checked) {
            linesLayer.remove();
        }
    });
}

// Function to show substation information
function showSubstationInfo(substation) {
    const infoDiv = document.getElementById('substation-info');
    infoDiv.innerHTML = `
        <h3>${substation.name}</h3>
        <p>Type: ${substation.type}</p>
    `;
    infoDiv.style.display = 'block';
}

// Function to hide substation information
function hideSubstationInfo() {
    const infoDiv = document.getElementById('substation-info');
    infoDiv.style.display = 'none';
}

// Fetch network data from the backend
fetch('/network_data')
    .then(response => response.json())
    .then(data => {
        console.log('Received network data:', data); // Debug log

        // Process substations
        Object.entries(data.substations).forEach(([code, substation]) => {
            const marker = L.marker([substation.lat, substation.lon])
                .bindPopup(`<b>${substation.name}</b><br>Type: ${substation.type}`)
                .on('click', () => showSubstationInfo(substation));
            voltageLayers['110kV'].addLayer(marker);
        });

        // Process lines
        if (data.lines && Array.isArray(data.lines)) {
            console.log('Processing lines:', data.lines); // Debug log
            data.lines.forEach(line => {
                // Find the substations by their names
                const fromSubstation = Object.values(data.substations).find(sub => sub.name === line.from_bus);
                const toSubstation = Object.values(data.substations).find(sub => sub.name === line.to_bus);
                
                if (fromSubstation && toSubstation) {
                    console.log('Drawing line:', line.name, 'from', fromSubstation.name, 'to', toSubstation.name); // Debug log
                    const polyline = L.polyline(
                        [[fromSubstation.lat, fromSubstation.lon], [toSubstation.lat, toSubstation.lon]],
                        { 
                            color: '#FF0000', 
                            weight: 2,
                            opacity: 0.8
                        }
                    ).bindPopup(`<b>${line.name}</b>`);
                    linesLayer.addLayer(polyline);
                } else {
                    console.warn('Could not find substations for line:', line.name); // Debug log
                }
            });
        } else {
            console.warn('No lines data received or invalid format'); // Debug log
        }
    })
    .catch(error => console.error('Error fetching network data:', error));

// Add event listeners for layer controls
document.querySelectorAll('input[name="voltage"], input[name="component"]').forEach(checkbox => {
    checkbox.addEventListener('change', updateLayerVisibility);
}); 