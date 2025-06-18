// Initialize the map centered on New Zealand
const map = L.map('map').setView([-40.9006, 174.8860], 6);

// Add the OpenStreetMap tile layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Create layer groups for each network
const transpowerLayers = {
    substations: L.layerGroup().addTo(map),
    lines: L.layerGroup().addTo(map)
};

const vectorLayers = {
    substations: L.layerGroup().addTo(map),
    lines: L.layerGroup().addTo(map)
};

// Create custom icon for substations
const substationIcon = L.divIcon({
    className: 'substation-icon',
    html: '<div style="width: 12px; height: 10px; background-color: #FF0000; clip-path: polygon(50% 0%, 0% 100%, 100% 100%);"></div>',
    iconSize: [12, 10],
    iconAnchor: [6, 10]
});

// Function to show substation information
function showSubstationInfo(substation) {
    const infoDiv = document.getElementById('substation-details');
    infoDiv.innerHTML = `
        <p><strong>Name:</strong> ${substation.name}</p>
        <p><strong>Type:</strong> ${substation.type}</p>
        <p><strong>Description:</strong> ${substation.description}</p>
    `;
    document.getElementById('substation-info').style.display = 'block';
}

// Function to hide substation info
function hideSubstationInfo() {
    document.getElementById('substation-info').style.display = 'none';
}

// Store substation coordinates for line drawing
const substationCoords = {
    transpower: {},
    vector: {}
};

// Fetch network data from the backend
console.log('Fetching network data...');
fetch('/network_data')
    .then(response => {
        console.log('Received response:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('Received network data:', data);

        // Process Transpower data
        if (data.transpower) {
            console.log('Processing Transpower data...');
            // Process substations
            if (data.transpower.substations) {
                console.log(`Found ${data.transpower.substations.length} Transpower substations`);
                data.transpower.substations.forEach(substation => {
                    console.log('Creating marker for substation:', substation.name);
                    const marker = L.marker([substation.lat, substation.lon], { icon: substationIcon })
                        .bindPopup(`
                            <strong>${substation.name}</strong><br>
                            Type: ${substation.type}<br>
                            Description: ${substation.description}
                        `);
                    
                    marker.on('click', () => showSubstationInfo(substation));
                    transpowerLayers.substations.addLayer(marker);
                    
                    // Store coordinates for line drawing
                    substationCoords.transpower[substation.name] = [substation.lat, substation.lon];
                });
            }

            // Process lines
            if (data.transpower.lines) {
                console.log(`Found ${data.transpower.lines.length} Transpower lines`);
                data.transpower.lines.forEach(line => {
                    console.log('Processing line:', line.name);
                    const fromCoords = substationCoords.transpower[line.from_bus];
                    const toCoords = substationCoords.transpower[line.to_bus];
                    
                    if (fromCoords && toCoords) {
                        const polyline = L.polyline([fromCoords, toCoords], {
                            color: '#FF0000',
                            weight: 2,
                            opacity: 0.8
                        }).bindPopup(`
                            <strong>${line.name}</strong><br>
                            Voltage: ${line.voltage} kV<br>
                            From: ${line.from_bus}<br>
                            To: ${line.to_bus}
                        `);
                        transpowerLayers.lines.addLayer(polyline);
                    } else {
                        console.warn('Could not find coordinates for line:', line.name);
                    }
                });
            }
        } else {
            console.warn('No Transpower data found');
        }

        // Process Vector data
        if (data.vector) {
            console.log('Processing Vector data...');
            // Process substations
            if (data.vector.substations) {
                console.log(`Found ${data.vector.substations.length} Vector substations`);
                data.vector.substations.forEach(substation => {
                    console.log('Creating marker for substation:', substation.name);
                    const marker = L.marker([substation.lat, substation.lon], { icon: substationIcon })
                        .bindPopup(`
                            <strong>${substation.name}</strong><br>
                            Type: ${substation.type}<br>
                            Description: ${substation.description}
                        `);
                    
                    marker.on('click', () => showSubstationInfo(substation));
                    vectorLayers.substations.addLayer(marker);
                    
                    // Store coordinates for line drawing
                    substationCoords.vector[substation.name] = [substation.lat, substation.lon];
                });
            }

            // Process lines
            if (data.vector.lines) {
                console.log(`Found ${data.vector.lines.length} Vector lines`);
                data.vector.lines.forEach(line => {
                    console.log('Processing line:', line.name);
                    const fromCoords = substationCoords.vector[line.from_bus];
                    const toCoords = substationCoords.vector[line.to_bus];
                    
                    if (fromCoords && toCoords) {
                        const polyline = L.polyline([fromCoords, toCoords], {
                            color: '#0000FF',
                            weight: 2,
                            opacity: 0.8
                        }).bindPopup(`
                            <strong>${line.name}</strong><br>
                            Voltage: ${line.voltage} kV<br>
                            From: ${line.from_bus}<br>
                            To: ${line.to_bus}
                        `);
                        vectorLayers.lines.addLayer(polyline);
                    } else {
                        console.warn('Could not find coordinates for line:', line.name);
                    }
                });
            }
        } else {
            console.warn('No Vector data found');
        }
    })
    .catch(error => {
        console.error('Error fetching network data:', error);
    });

// Add event listeners for checkboxes
document.getElementById('transpower-substations').addEventListener('change', function(e) {
    if (e.target.checked) {
        map.addLayer(transpowerLayers.substations);
    } else {
        map.removeLayer(transpowerLayers.substations);
    }
});

document.getElementById('transpower-lines').addEventListener('change', function(e) {
    if (e.target.checked) {
        map.addLayer(transpowerLayers.lines);
    } else {
        map.removeLayer(transpowerLayers.lines);
    }
});

document.getElementById('vector-substations').addEventListener('change', function(e) {
    if (e.target.checked) {
        map.addLayer(vectorLayers.substations);
    } else {
        map.removeLayer(vectorLayers.substations);
    }
});

document.getElementById('vector-lines').addEventListener('change', function(e) {
    if (e.target.checked) {
        map.addLayer(vectorLayers.lines);
    } else {
        map.removeLayer(vectorLayers.lines);
    }
});

// Hide substation info when clicking on the map
map.on('click', hideSubstationInfo); 