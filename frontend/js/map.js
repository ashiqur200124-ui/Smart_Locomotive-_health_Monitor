// Railway map and animation functions

let map;
let locomotiveMarkers = [];
let animationInterval;
let isAnimating = false;

// Initialize map
function initializeMap() {
    // Check if map is already initialized
    if (map) {
        console.log('Map already initialized');
        return;
    }
    
    // Check if Leaflet is loaded
    if (typeof L === 'undefined') {
        console.error('Leaflet library not loaded');
        return;
    }
    
    // Initialize Leaflet map centered on Bangladesh
    map = L.map('map').setView([23.685, 90.356], 7);
    
    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(map);
    
    // Add Bangladesh railway network
    addRailwayNetwork();
    
    // Add locomotives
    addLocomotivesToMap();
    
    // Fix rendering if the map was created while hidden
    setTimeout(() => {
        if (map) {
            map.invalidateSize();
        }
    }, 200);
}

// Add railway network (junctions and sheds)
function addRailwayNetwork() {
    // Major junctions
    const junctions = [
        { name: 'Dhaka Junction', lat: 23.7275, lon: 90.4086, type: 'junction' },
        { name: 'Chittagong Junction', lat: 22.3596, lon: 91.7623, type: 'junction' },
        { name: 'Khulna Junction', lat: 22.8043, lon: 89.1680, type: 'junction' },
        { name: 'Rajshahi Junction', lat: 24.3745, lon: 88.6042, type: 'junction' },
        { name: 'Sylhet Junction', lat: 24.9154, lon: 91.8746, type: 'junction' },
        { name: 'Gazipur Junction', lat: 23.9500, lon: 90.4150, type: 'junction' },
        { name: 'Mymensingh Junction', lat: 24.7465, lon: 90.4081, type: 'junction' }
    ];
    
    // Locomotive sheds
    const sheds = [
        { name: 'Dhaka Shed', lat: 23.7400, lon: 90.3950, type: 'shed' },
        { name: 'Chittagong Shed', lat: 22.3700, lon: 91.7700, type: 'shed' },
        { name: 'Khulna Shed', lat: 22.8100, lon: 89.1700, type: 'shed' },
        { name: 'Rajshahi Shed', lat: 24.3800, lon: 88.6000, type: 'shed' },
        { name: 'Gazipur Depot', lat: 23.9600, lon: 90.4200, type: 'shed' }
    ];
    
    // Add junction markers
    junctions.forEach(junction => {
        L.circleMarker([junction.lat, junction.lon], {
            radius: 6,
            fillColor: '#2196F3',
            color: '#1976D2',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8
        }).addTo(map).bindPopup(`<strong>${junction.name}</strong><br/>Type: Junction`);
    });
    
    // Add shed markers
    sheds.forEach(shed => {
        L.circleMarker([shed.lat, shed.lon], {
            radius: 8,
            fillColor: '#9C27B0',
            color: '#7B1FA2',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8
        }).addTo(map).bindPopup(`<strong>${shed.name}</strong><br/>Type: Locomotive Shed`);
    });
    
    // Draw railway routes (simplified)
    drawRailwayRoutes();
}

// Draw railway routes
function drawRailwayRoutes() {
    const routes = [
        // Dhaka to Chittagong
        [[23.7275, 90.4086], [22.3596, 91.7623]],
        // Dhaka to Khulna
        [[23.7275, 90.4086], [22.8043, 89.1680]],
        // Dhaka to Rajshahi
        [[23.7275, 90.4086], [24.3745, 88.6042]],
        // Dhaka to Sylhet
        [[23.7275, 90.4086], [24.9154, 91.8746]]
    ];
    
    routes.forEach(route => {
        L.polyline(route, {
            color: '#2c3e50',
            weight: 3,
            opacity: 0.6,
            dashArray: '5, 5'
        }).addTo(map);
    });
}

// Add locomotives to map
function addLocomotivesToMap() {
    const locomotives = [
        { id: 'BR1001', name: 'Rajdhani Express', lat: 23.7275, lon: 90.4086, health: 85, risk: 15 },
        { id: 'BR1002', name: 'Sundarbans Express', lat: 22.8043, lon: 89.1680, health: 60, risk: 60 },
        { id: 'BR1003', name: 'Chittagong Mail', lat: 22.3596, lon: 91.7623, health: 78, risk: 30 }
    ];
    
    locomotives.forEach(loco => {
        const color = loco.risk > 75 ? '#F44336' : loco.risk > 50 ? '#FF9800' : '#4CAF50';
        
        const marker = L.circleMarker([loco.lat, loco.lon], {
            radius: 12,
            fillColor: color,
            color: '#000',
            weight: 2,
            opacity: 1,
            fillOpacity: 1,
            className: 'locomotive-marker'
        }).addTo(map);
        
        const popupContent = `
            <div style="font-family: Arial; font-size: 12px;">
                <strong>${loco.name}</strong><br/>
                ID: ${loco.id}<br/>
                Health: ${loco.health}%<br/>
                Risk: ${loco.risk}%
            </div>
        `;
        
        marker.bindPopup(popupContent);
        
        // Add pulsing animation
        addPulsingAnimation(marker);
        
        locomotiveMarkers.push({
            marker: marker,
            data: loco,
            originalColor: color
        });
    });
}

// Add pulsing animation to markers
function addPulsingAnimation(marker) {
    const originalRadius = marker.options.radius;
    let isGrowing = true;
    
    setInterval(() => {
        if (isGrowing) {
            marker.setRadius(originalRadius + 3);
            if (marker.options.radius >= originalRadius + 3) {
                isGrowing = false;
            }
        } else {
            marker.setRadius(originalRadius);
            if (marker.options.radius <= originalRadius) {
                isGrowing = true;
            }
        }
    }, 500);
}

// Animate locomotives moving along routes
function toggleAnimatedMode() {
    isAnimating = !isAnimating;
    
    if (isAnimating) {
        startLocomotiveAnimation();
        document.querySelector('[onclick="toggleAnimatedMode()"]').innerHTML = '<i class="fas fa-pause"></i> Stop Animation';
    } else {
        stopLocomotiveAnimation();
        document.querySelector('[onclick="toggleAnimatedMode()"]').innerHTML = '<i class="fas fa-play"></i> Start Animation';
    }
}

// Start animation
function startLocomotiveAnimation() {
    const routes = [
        {
            id: 'BR1001',
            path: [[23.7275, 90.4086], [22.8043, 89.1680], [23.7275, 90.4086]]
        },
        {
            id: 'BR1002',
            path: [[22.8043, 89.1680], [22.3596, 91.7623], [22.8043, 89.1680]]
        },
        {
            id: 'BR1003',
            path: [[22.3596, 91.7623], [24.9154, 91.8746], [22.3596, 91.7623]]
        }
    ];
    
    const steps = 100;
    let currentStep = 0;
    
    animationInterval = setInterval(() => {
        currentStep++;
        if (currentStep > steps) currentStep = 0;
        
        const progress = currentStep / steps;
        
        routes.forEach(route => {
            const locoMarker = locomotiveMarkers.find(l => l.data.id === route.id);
            if (!locoMarker) return;
            
            // Interpolate position along path
            const pathIndex = Math.floor(progress * (route.path.length - 1));
            const nextIndex = Math.min(pathIndex + 1, route.path.length - 1);
            const segmentProgress = (progress * (route.path.length - 1)) - pathIndex;
            
            const from = route.path[pathIndex];
            const to = route.path[nextIndex];
            
            const newLat = from[0] + (to[0] - from[0]) * segmentProgress;
            const newLon = from[1] + (to[1] - from[1]) * segmentProgress;
            
            locoMarker.marker.setLatLng([newLat, newLon]);
        });
    }, 100);
}

// Stop animation
function stopLocomotiveAnimation() {
    if (animationInterval) {
        clearInterval(animationInterval);
    }
}

// Reset map
function resetMap() {
    stopLocomotiveAnimation();
    
    if (map) {
        map.setView([23.685, 90.356], 7);
    }
    
    isAnimating = false;
    document.querySelector('[onclick="toggleAnimatedMode()"]').innerHTML = '<i class="fas fa-play"></i> Start Animation';
}

// Update locomotive marker colors based on health
function updateLocomotiveMarkerColors(healthData) {
    healthData.forEach(loco => {
        const marker = locomotiveMarkers.find(m => m.data.id === loco.id);
        if (marker) {
            const newColor = loco.risk > 75 ? '#F44336' : loco.risk > 50 ? '#FF9800' : '#4CAF50';
            marker.marker.setStyle({ fillColor: newColor });
            marker.data.health = loco.health;
            marker.data.risk = loco.risk;
        }
    });
}

// Refresh map display when the section becomes visible
function refreshMap() {
    if (!map) {
        initializeMap();
        return;
    }

    // Invalidate size after the container is visible
    setTimeout(() => {
        map.invalidateSize();
    }, 100);
}

console.log('Map module loaded');
