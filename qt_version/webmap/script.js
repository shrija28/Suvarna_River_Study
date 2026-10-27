console.log("Map Loaded Successfully");
console.log("Map Loaded Successfully");

window.bridge = null;

console.log("typeof qt =", typeof qt);
console.log("typeof QWebChannel =", typeof QWebChannel);

if (typeof qt !== "undefined" && typeof QWebChannel !== "undefined") {

    new QWebChannel(qt.webChannelTransport, function(channel) {

        console.log("Inside callback");

        window.bridge = channel.objects.bridge;

        console.log("Bridge =", window.bridge);

    });

} else {

    console.log("WebChannel unavailable");

}

//==========================================
// Create Map
// ==========================================

const map = L.map("map").setView([13.46, 74.69], 13);

// ==========================================
// Base Layers
// ==========================================

// Street Map

const street = L.tileLayer(
    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {

        maxZoom: 19,

        attribution: "&copy; OpenStreetMap"

    }
);

// Satellite

const satellite = L.tileLayer(
    "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", {

        maxZoom: 19,

        attribution: "Esri"

    }
);

// Load satellite first

satellite.addTo(map);

// ==========================================
// Layer Switcher
// ==========================================

L.control.layers({

        "Satellite": satellite,

        "Street Map": street

    }

).addTo(map);

// ==========================================
// Scale
// ==========================================

L.control.scale().addTo(map);

// ==========================================
// Feature Group
// ==========================================

const drawnItems = new L.FeatureGroup();

map.addLayer(drawnItems);

// ==========================================
// Draw Toolbar
// ==========================================

const drawControl = new L.Control.Draw({

    position: "topleft",

    draw: {

        rectangle: true,

        polygon: false,

        polyline: false,

        marker: false,

        circle: false,

        circlemarker: false

    },

    edit: {

        featureGroup: drawnItems,

        remove: true

    }

});

map.addControl(drawControl);

// ==========================================
// Rectangle Event
// ==========================================

// ==========================================
// Rectangle Event
// ==========================================

map.on(L.Draw.Event.CREATED, function(event) {
    console.log("Rectangle created");

    // Remove previous AOI
    drawnItems.clearLayers();

    // Add new AOI
    const layer = event.layer;
    drawnItems.addLayer(layer);

    // Get AOI bounds
    const bounds = layer.getBounds();

    const north = bounds.getNorth();
    const south = bounds.getSouth();
    const east = bounds.getEast();
    const west = bounds.getWest();
    // Check if AOI is inside river mouth

    console.clear();


    console.log("North Latitude :", north);
    console.log("South Latitude :", south);
    console.log("East Longitude :", east);
    console.log("West Longitude :", west);

    console.log("Bridge object =", window.bridge);

    // Send AOI coordinates to Python
    if (window.bridge) {
        console.log("Calling updateAOI()");
        window.bridge.updateAOI(north, south, east, west);
        console.log("updateAOI() finished");
    } else {
        console.log("Bridge is NULL");
    }

});


// ==========================================
// Mouse Coordinates
// ==========================================

map.on("mousemove", function(e) {

    document.title =
        "Latitude : " +
        e.latlng.lat.toFixed(6) +
        " | Longitude : " +
        e.latlng.lng.toFixed(6);

});