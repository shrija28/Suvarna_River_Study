console.log("Map Loaded Successfully");

// ==========================================
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

map.on(L.Draw.Event.CREATED, function(event) {

    drawnItems.clearLayers();

    const layer = event.layer;

    drawnItems.addLayer(layer);

    const bounds = layer.getBounds();

    const north = bounds.getNorth();
    const south = bounds.getSouth();
    const east = bounds.getEast();
    const west = bounds.getWest();

    console.clear();

    console.log("========== AOI ==========");

    console.log("North :", north);

    console.log("South :", south);

    console.log("East  :", east);

    console.log("West  :", west);

    console.log("=========================");

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