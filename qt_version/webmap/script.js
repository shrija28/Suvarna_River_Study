// ============================================================================
// Suvarna River Interactive Map - OpenStreetMap + Multi-Layer Leaflet Engine
// Study Area: Suvarna (Swarna) River Estuary near Kodi Bengre, Udupi, Karnataka
// Theme: Dark Emerald GIS
// ============================================================================

console.log("Initializing Suvarna River Dark Emerald GIS Map Engine...");

window.bridge = null;

// Initialize Qt WebChannel Bridge if available
if (typeof qt !== "undefined" && typeof QWebChannel !== "undefined") {
    new QWebChannel(qt.webChannelTransport, function(channel) {
        window.bridge = channel.objects.bridge;
        console.log("Qt WebChannel Bridge connected:", window.bridge);
        if (window.bridge && typeof window.bridge.setMapStatus === "function") {
            window.bridge.setMapStatus("Map Ready");
        }
        if (window.bridge && typeof window.bridge.setMapModeName === "function") {
            window.bridge.setMapModeName("OpenStreetMap Standard");
        }
    });
} else {
    console.log("QWebChannel not yet available or running in standalone browser");
}

// Safety check for Leaflet library
if (typeof L === "undefined") {
    console.error("Leaflet library is undefined. Ensure internet connectivity or local assets.");
    var banner = document.getElementById("offline-banner");
    if (banner) banner.style.display = "block";
} else {
    initMap();
}

function initMap() {
    // ========================================================================
    // 1. Map Initialization
    // Center: Suvarna (Swarna) River Estuary at Kodi Bengre, Udupi, Karnataka
    // Lat: 13.4380 N, Lon: 74.6980 E, Zoom: 13
    // ========================================================================
    const STUDY_AREA_CENTER = [13.4380, 74.6980];
    const INITIAL_ZOOM = 13;

    const map = L.map("map", {
        center: STUDY_AREA_CENTER,
        zoom: INITIAL_ZOOM,
        minZoom: 5,
        maxZoom: 19,
        zoomControl: true
    });

    window.leafletMap = map;

    // ========================================================================
    // 2. Base Tile Layers (Map, Satellite, Hybrid, Terrain)
    // ========================================================================

    // 1. OpenStreetMap Standard (Map)
    const osmStandard = L.tileLayer(
        "https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
            maxZoom: 19,
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> contributors'
        }
    );

    // 2. Esri World Imagery (Satellite)
    const esriSatellite = L.tileLayer(
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", {
            maxZoom: 19,
            attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, GIS Community'
        }
    );

    // Hybrid Reference Overlay (Boundaries & Places labels over Satellite)
    const esriLabels = L.tileLayer(
        "https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}", {
            maxZoom: 19,
            pane: "overlayPane"
        }
    );

    // 3. OpenTopoMap (Terrain)
    const openTopo = L.tileLayer(
        "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png", {
            maxZoom: 17,
            attribution: 'Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, SRTM | Style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a>'
        }
    );

    // Active Base Layer state
    let activeBase = osmStandard;
    let isHybrid = false;
    osmStandard.addTo(map);

    // Function to dynamically switch map modes from PySide6 or JS
    window.setMapMode = function(mode) {
        map.removeLayer(osmStandard);
        map.removeLayer(esriSatellite);
        map.removeLayer(openTopo);
        if (map.hasLayer(esriLabels)) {
            map.removeLayer(esriLabels);
        }

        let modeDisplayName = "OpenStreetMap Standard";

        if (mode === "satellite") {
            esriSatellite.addTo(map);
            activeBase = esriSatellite;
            modeDisplayName = "Satellite Imagery (Esri)";
        } else if (mode === "hybrid") {
            esriSatellite.addTo(map);
            esriLabels.addTo(map);
            activeBase = esriSatellite;
            modeDisplayName = "Hybrid (Satellite + Labels)";
        } else if (mode === "terrain") {
            openTopo.addTo(map);
            activeBase = openTopo;
            modeDisplayName = "OpenTopoMap (Terrain)";
        } else {
            // Default "map"
            osmStandard.addTo(map);
            activeBase = osmStandard;
            modeDisplayName = "OpenStreetMap Standard";
        }

        console.log("Map Mode changed to:", mode, `(${modeDisplayName})`);

        if (window.bridge && typeof window.bridge.setMapModeName === "function") {
            window.bridge.setMapModeName(modeDisplayName);
        }
    };

    // Offline / Tile Error Handling
    let tileErrorCount = 0;
    function onTileError() {
        tileErrorCount++;
        if (tileErrorCount >= 4) {
            const banner = document.getElementById("offline-banner");
            if (banner && banner.style.display !== "block") {
                banner.style.display = "block";
                const msg = document.getElementById("offline-msg");
                if (msg) {
                    msg.innerText = "Notice: Some map tiles could not be downloaded. Please verify internet connection.";
                }
            }
        }
        if (window.bridge && typeof window.bridge.setMapStatus === "function") {
            window.bridge.setMapStatus("Notice: Offline Tile Mode");
        }
    }

    osmStandard.on("tileerror", onTileError);
    esriSatellite.on("tileerror", onTileError);

    // ========================================================================
    // 3. Scale Bar
    // ========================================================================
    L.control.scale({
        metric: true,
        imperial: false,
        position: "bottomleft"
    }).addTo(map);

    // ========================================================================
    // 4. Dynamic Study Area Location Marker & Geocoding Engine
    // ========================================================================
    const markerLayerGroup = L.layerGroup().addTo(map);

    let currentMarkerPosition = [STUDY_AREA_CENTER[0], STUDY_AREA_CENTER[1]];
    let currentLocationName = "Kodi Bengre, Udupi, Karnataka, India";

    const studyMarker = L.marker(STUDY_AREA_CENTER, {
        title: "Study Area Location (Click or drag to change)",
        draggable: true,
        riseOnHover: true
    });

    function updateMarkerPopup(lat, lng, locName) {
        currentMarkerPosition = [lat, lng];
        currentLocationName = locName;

        const isSuvarna = Math.abs(lat - 13.438) < 0.08 && Math.abs(lng - 74.698) < 0.08;
        const estText = isSuvarna ? "Suvarna &amp; Sita confluence entering Arabian Sea" : "Coastal &amp; Estuarine Study Zone";

        const markerPopupContent = `
            <div style="font-family: inherit; min-width: 230px;">
                <h4 style="margin: 0 0 6px 0; color: #74E6B0; font-size: 14px; border-bottom: 1px solid #24574B; padding-bottom: 4px;">
                    Active Study Area
                </h4>
                <div style="font-size: 12px; margin-bottom: 4px; color: #F4F1E8;">
                    <b>Location:</b> ${locName}
                </div>
                <div style="font-size: 12px; margin-bottom: 4px; color: #74E6B0;">
                    <b>Coordinates:</b> ${lat.toFixed(4)}&deg; N, ${lng.toFixed(4)}&deg; E
                </div>
                <div style="font-size: 11px; margin-bottom: 5px; color: #A8C4B7;">
                    <b>Context:</b> ${estText}
                </div>
                <div style="font-size: 11px; color: #C8E889; font-weight: 500;">
                    Click or drag anywhere on map to reposition
                </div>
            </div>
        `;

        studyMarker.setLatLng([lat, lng]);
        studyMarker.bindPopup(markerPopupContent, {
            className: "study-area-popup",
            closeButton: true
        });
        studyMarker.bindTooltip(locName, {
            direction: "top",
            offset: [0, -10]
        });
        studyMarker.openPopup();
    }

    let geocodeTimer = null;
    function reverseGeocode(lat, lng, callback) {
        const coordFallback = `${lat >= 0 ? lat.toFixed(4) + "° N" : Math.abs(lat).toFixed(4) + "° S"}, ${lng >= 0 ? lng.toFixed(4) + "° E" : Math.abs(lng).toFixed(4) + "° W"}`;

        // Fast resolution if near Suvarna River / Kodi Bengre
        if (Math.abs(lat - 13.438) < 0.05 && Math.abs(lng - 74.698) < 0.05) {
            callback("Kodi Bengre, Udupi, Karnataka, India", lat, lng);
            return;
        }

        // Show formatted coordinates immediately for snappy feedback
        callback(coordFallback, lat, lng);

        // Reverse geocode via OpenStreetMap Nominatim
        if (geocodeTimer) clearTimeout(geocodeTimer);
        geocodeTimer = setTimeout(() => {
            const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=14&addressdetails=1`;
            fetch(url, { headers: { "Accept": "application/json" } })
                .then(res => res.json())
                .then(data => {
                    let locName = "";
                    if (data && data.address) {
                        const a = data.address;
                        const place = a.suburb || a.village || a.town || a.city || a.hamlet || a.county || a.river || "";
                        const district = a.state_district || a.district || a.state || "";
                        const country = a.country || "";
                        const parts = [place, district, country].filter(p => p && p.trim().length > 0);
                        locName = parts.slice(0, 3).join(", ");
                    }
                    if (!locName && data && data.display_name) {
                        locName = data.display_name.split(",").slice(0, 3).join(",");
                    }
                    if (locName) {
                        callback(locName, lat, lng);
                    }
                })
                .catch(err => {
                    console.log("Geocode note (offline or fallback):", err);
                });
        }, 250);
    }

    function setLocation(lat, lng, knownName) {
        if (knownName) {
            updateMarkerPopup(lat, lng, knownName);
            if (window.bridge && typeof window.bridge.updateLocation === "function") {
                window.bridge.updateLocation(knownName, lat, lng);
            }
        } else {
            reverseGeocode(lat, lng, function(locName) {
                updateMarkerPopup(lat, lng, locName);
                if (window.bridge && typeof window.bridge.updateLocation === "function") {
                    window.bridge.updateLocation(locName, lat, lng);
                }
            });
        }
    }
    window.setLocation = setLocation;

    // Click anywhere on map to reposition study area location
    map.on("click", function(e) {
        setLocation(e.latlng.lat, e.latlng.lng);
    });

    // Drag marker to reposition study area location
    studyMarker.on("dragend", function(e) {
        const pos = e.target.getLatLng();
        setLocation(pos.lat, pos.lng);
    });

    markerLayerGroup.addLayer(studyMarker);
    updateMarkerPopup(STUDY_AREA_CENTER[0], STUDY_AREA_CENTER[1], currentLocationName);

    // ========================================================================
    // Location Search Control (Search any river, estuary or place)
    // ========================================================================
    const SearchControl = L.Control.extend({
        options: { position: "topleft" },
        onAdd: function() {
            const container = L.DomUtil.create("div", "leaflet-bar map-search-bar");
            container.style.marginTop = "8px";
            container.innerHTML = `
                <div style="display:flex; align-items:center; background:#082B26; border:1px solid #24574B; border-radius:6px; padding:3px 8px; box-shadow:0 2px 10px rgba(0,0,0,0.6);">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#74E6B0" stroke-width="2.5" style="margin-right:6px; flex-shrink:0;">
                        <circle cx="11" cy="11" r="8"></circle>
                        <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                    </svg>
                    <input id="map-search-input" type="text" placeholder="Search river, coast or place..." 
                        style="background:transparent; border:none; color:#F4F1E8; font-size:11px; outline:none; width:175px;" />
                    <button id="map-search-btn" title="Search Location" 
                        style="background:#103B32; border:1px solid #24574B; color:#74E6B0; border-radius:4px; padding:2px 7px; font-size:10px; font-weight:700; cursor:pointer; margin-left:4px;">GO</button>
                </div>
            `;
            L.DomEvent.disableClickPropagation(container);
            L.DomEvent.disableScrollPropagation(container);

            setTimeout(() => {
                const input = document.getElementById("map-search-input");
                const btn = document.getElementById("map-search-btn");
                function executeSearch() {
                    const q = input.value.trim();
                    if (!q) return;
                    fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(q)}&limit=1`)
                        .then(r => r.json())
                        .then(res => {
                            if (res && res.length > 0) {
                                const lat = parseFloat(res[0].lat);
                                const lon = parseFloat(res[0].lon);
                                map.setView([lat, lon], 13);
                                setLocation(lat, lon, res[0].display_name.split(",").slice(0, 3).join(","));
                            }
                        })
                        .catch(err => console.log("Search error:", err));
                }
                if (btn) btn.onclick = executeSearch;
                if (input) {
                    input.addEventListener("keydown", function(e) {
                        if (e.key === "Enter") executeSearch();
                    });
                }
            }, 100);

            return container;
        }
    });
    new SearchControl().addTo(map);

    // ========================================================================
    // 5. Area of Interest (AOI) Drawing Toolbar (Preserved Existing Feature)
    // ========================================================================
    const drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    if (typeof L.Control.Draw !== "undefined") {
        const drawControl = new L.Control.Draw({
            position: "topleft",
            draw: {
                rectangle: {
                    shapeOptions: {
                        color: "#74E6B0",
                        weight: 2,
                        fillColor: "#00BFA5",
                        fillOpacity: 0.25
                    }
                },
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

        // AOI Rectangle Created Event
        map.on(L.Draw.Event.CREATED, function(event) {
            console.log("AOI Rectangle created");

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

            console.log("========== AOI Coordinates ==========");
            console.log("North Latitude :", north);
            console.log("South Latitude :", south);
            console.log("East Longitude :", east);
            console.log("West Longitude :", west);
            console.log("=====================================");

            // Automatically update dynamic location to AOI center
            const center = bounds.getCenter();
            setLocation(center.lat, center.lng);

            // Send AOI coordinates to PySide6 via Bridge
            if (window.bridge && typeof window.bridge.updateAOI === "function") {
                window.bridge.updateAOI(north, south, east, west);
                console.log("Successfully sent AOI to Python backend");
            } else {
                console.warn("Qt Bridge object not available to receive AOI");
            }
        });

        map.on(L.Draw.Event.DELETED, function() {
            console.log("AOI Rectangle removed");
            if (window.bridge && typeof window.bridge.clearAOI === "function") {
                window.bridge.clearAOI();
            }
        });
    }

    // ========================================================================
    // 6. Future Compatibility Layer Groups
    // ========================================================================
    const historicalBoundariesGroup = L.layerGroup();
    const deviationPredictionsGroup = L.layerGroup();
    const customOverlaysGroup = L.layerGroup();

    // ========================================================================
    // 7. Layer Switcher Control
    // ========================================================================
    const baseLayers = {
        "OpenStreetMap (Standard)": osmStandard,
        "Satellite Imagery (Esri)": esriSatellite,
        "Topography (OpenTopoMap)": openTopo
    };

    const overlayLayers = {
        "Study Area Marker": markerLayerGroup,
        "Drawn AOI Boundary": drawnItems,
        "Historical River Boundaries": historicalBoundariesGroup,
        "River Deviation Predictions": deviationPredictionsGroup,
        "Custom Overlays": customOverlaysGroup
    };

    L.control.layers(baseLayers, overlayLayers, {
        position: "topright",
        collapsed: true
    }).addTo(map);

    // ========================================================================
    // 8. Mouse Coordinates HUD & Python Bridge Dispatch
    // ========================================================================
    const CoordHUD = L.Control.extend({
        onAdd: function() {
            const div = L.DomUtil.create("div", "coord-hud");
            div.id = "coord-hud-display";
            div.innerHTML = "Lat: 13.438000 | Lon: 74.698000";
            return div;
        }
    });
    new CoordHUD({ position: "bottomright" }).addTo(map);

    map.on("mousemove", function(e) {
        const latStr = e.latlng.lat.toFixed(6);
        const lngStr = e.latlng.lng.toFixed(6);

        // Update document title
        document.title = "Latitude : " + latStr + " | Longitude : " + lngStr;

        // Update on-screen HUD
        const hud = document.getElementById("coord-hud-display");
        if (hud) {
            hud.innerHTML = `Lat: ${latStr} | Lon: ${lngStr}`;
        }

        // Send live cursor coordinates to Python bridge for bottom info card
        if (window.bridge && typeof window.bridge.updateCursorCoords === "function") {
            window.bridge.updateCursorCoords(e.latlng.lat, e.latlng.lng);
        }
    });

    // ========================================================================
    // 9. Window Resize Handling (Ensures full responsiveness)
    // ========================================================================
    function resizeMap() {
        if (map) {
            map.invalidateSize();
        }
    }

    window.addEventListener("resize", resizeMap);
    setTimeout(resizeMap, 300);
    setTimeout(resizeMap, 800);

    // ========================================================================
    // 10. Future Compatibility API (Callable from Python or JS)
    // ========================================================================

    window.focusStudyArea = function() {
        map.setView(currentMarkerPosition, INITIAL_ZOOM);
        studyMarker.openPopup();
    };

    window.focusCurrentLocation = function() {
        map.setView(currentMarkerPosition, 13);
        studyMarker.openPopup();
    };

    window.setHistoricalBoundary = function(geojsonData, styleOptions) {
        historicalBoundariesGroup.clearLayers();
        if (!geojsonData) return;

        const defaultStyle = {
            color: "#E9B866",
            weight: 2.5,
            opacity: 0.9,
            fillColor: "#E9B866",
            fillOpacity: 0.25
        };

        const layer = L.geoJSON(geojsonData, {
            style: styleOptions || defaultStyle,
            onEachFeature: function(feature, l) {
                if (feature.properties && feature.properties.year) {
                    l.bindPopup(`<b>Historical River Boundary:</b> ${feature.properties.year}`);
                }
            }
        });

        historicalBoundariesGroup.addLayer(layer);
        if (!map.hasLayer(historicalBoundariesGroup)) {
            map.addLayer(historicalBoundariesGroup);
        }
        try {
            map.fitBounds(layer.getBounds(), { padding: [20, 20] });
        } catch (e) {
            console.log("Could not fit bounds:", e);
        }
    };

    window.setRiverDeviationPrediction = function(geojsonData, styleOptions) {
        deviationPredictionsGroup.clearLayers();
        if (!geojsonData) return;

        const defaultStyle = {
            color: "#74E6B0",
            weight: 3,
            opacity: 0.95,
            fillColor: "#00BFA5",
            fillOpacity: 0.35
        };

        const layer = L.geoJSON(geojsonData, {
            style: styleOptions || defaultStyle,
            onEachFeature: function(feature, l) {
                const props = feature.properties || {};
                const year = props.prediction_year || props.year || "Future";
                l.bindPopup(`<b>Predicted River Path:</b> Year ${year}`);
            }
        });

        deviationPredictionsGroup.addLayer(layer);
        if (!map.hasLayer(deviationPredictionsGroup)) {
            map.addLayer(deviationPredictionsGroup);
        }
        try {
            map.fitBounds(layer.getBounds(), { padding: [20, 20] });
        } catch (e) {
            console.log("Could not fit bounds:", e);
        }
    };

    window.clearOverlayLayer = function(target) {
        if (target === "historical") historicalBoundariesGroup.clearLayers();
        else if (target === "prediction") deviationPredictionsGroup.clearLayers();
        else if (target === "custom") customOverlaysGroup.clearLayers();
        else if (target === "aoi") drawnItems.clearLayers();
        else {
            historicalBoundariesGroup.clearLayers();
            deviationPredictionsGroup.clearLayers();
            customOverlaysGroup.clearLayers();
        }
    };

    console.log("Suvarna River Web Map Engine successfully initialized.");
}