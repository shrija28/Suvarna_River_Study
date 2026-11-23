// ============================================================================
// Suvarna River Interactive Map - OpenStreetMap + Multi-Layer Leaflet Engine
// Study Area: Suvarna (Swarna) River Estuary near Kodi Bengre, Udupi, Karnataka
// Pure Web Engine - Standard REST Fetch (QWebChannel completely removed)
// ============================================================================

console.log("Initializing Suvarna River Dark Emerald Web Map Engine...");

// Safety check for Leaflet library
if (typeof L === "undefined") {
    console.error("Leaflet library is undefined. Ensure vendor files or internet connectivity are active.");
    var banner = document.getElementById("offline-banner");
    if (banner) banner.style.display = "block";
} else {
    // Wait until DOM is loaded if needed
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initMap);
    } else {
        initMap();
    }
}

function initMap() {
    const STUDY_AREA_CENTER = [13.4380, 74.6980];
    const INITIAL_ZOOM = 13;

    const mapElement = document.getElementById("map");
    if (!mapElement) {
        console.warn("Map container '#map' not found in DOM");
        return;
    }

    const map = L.map("map", {
        center: STUDY_AREA_CENTER,
        zoom: INITIAL_ZOOM,
        minZoom: 5,
        maxZoom: 19,
        zoomControl: true
    });

    window.leafletMap = map;

    // Helper functions for updating top banner & status bar UI
    function setMapStatusText(text, isWarning) {
        const dot = document.getElementById("status-dot");
        const statusEl = document.getElementById("status-map-text");
        if (statusEl) statusEl.innerText = text;
        if (dot) {
            dot.style.color = isWarning ? "var(--amber)" : "var(--mint)";
        }
    }

    function setMapModePill(modeName) {
        const pill = document.getElementById("status-mode-pill");
        if (pill) pill.innerText = "Mode: " + modeName;
    }

    setMapStatusText("Map Ready", false);
    setMapModePill("OpenStreetMap Standard");

    // ========================================================================
    // Base Tile Layers (Map, Satellite, Hybrid, Terrain)
    // ========================================================================
    const osmStandard = L.tileLayer(
        "https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
            maxZoom: 19,
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> contributors'
        }
    );

    const esriSatellite = L.tileLayer(
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", {
            maxZoom: 19,
            attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, GIS Community'
        }
    );

    const esriLabels = L.tileLayer(
        "https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}", {
            maxZoom: 19,
            pane: "overlayPane"
        }
    );

    const openTopo = L.tileLayer(
        "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png", {
            maxZoom: 17,
            attribution: 'Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>, SRTM | Style: &copy; OpenTopoMap'
        }
    );

    let activeBase = osmStandard;
    osmStandard.addTo(map);

    // Switch map modes
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
            osmStandard.addTo(map);
            activeBase = osmStandard;
            modeDisplayName = "OpenStreetMap Standard";
        }

        setMapModePill(modeDisplayName);

        // Update button active state
        document.querySelectorAll(".mode-btn").forEach(btn => {
            if (btn.getAttribute("data-mode") === mode) {
                btn.classList.add("active");
            } else {
                btn.classList.remove("active");
            }
        });
    };

    // Tile error handling
    let tileErrorCount = 0;
    function onTileError() {
        tileErrorCount++;
        if (tileErrorCount >= 4) {
            const banner = document.getElementById("offline-banner");
            if (banner && banner.style.display !== "block") {
                banner.style.display = "block";
            }
            setMapStatusText("Notice: Offline Tile Mode", true);
        }
    }

    osmStandard.on("tileerror", onTileError);
    esriSatellite.on("tileerror", onTileError);

    // Scale control
    L.control.scale({
        metric: true,
        imperial: false,
        position: "bottomleft"
    }).addTo(map);

    // ========================================================================
    // Dynamic Study Area Location Marker & Reverse Geocoding
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
            <div style="font-family: inherit; min-width: 220px; color: #F4F1E8; padding: 4px;">
                <h4 style="margin: 0 0 6px 0; color: #74E6B0; font-size: 13px; border-bottom: 1px solid #24574B; padding-bottom: 4px;">
                    Active Study Area
                </h4>
                <div style="font-size: 11px; margin-bottom: 4px;">
                    <b>Location:</b> ${locName}
                </div>
                <div style="font-size: 11px; margin-bottom: 4px; color: #74E6B0;">
                    <b>Coordinates:</b> ${lat.toFixed(4)}&deg; N, ${lng.toFixed(4)}&deg; E
                </div>
                <div style="font-size: 10px; margin-bottom: 5px; color: #A8C4B7;">
                    <b>Context:</b> ${estText}
                </div>
                <div style="font-size: 10px; color: #C8E889; font-weight: 500;">
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

        // Update Top Banner Badge & Status Bar
        const badgeEl = document.getElementById("loc-badge-text");
        if (badgeEl) badgeEl.innerText = locName;
        const statusArea = document.getElementById("status-study-area");
        if (statusArea) statusArea.innerText = "Study Area: " + locName;
    }

    let geocodeTimer = null;
    function reverseGeocode(lat, lng, callback) {
        const coordFallback = `${lat >= 0 ? lat.toFixed(4) + "° N" : Math.abs(lat).toFixed(4) + "° S"}, ${lng >= 0 ? lng.toFixed(4) + "° E" : Math.abs(lng).toFixed(4) + "° W"}`;

        if (Math.abs(lat - 13.438) < 0.05 && Math.abs(lng - 74.698) < 0.05) {
            callback("Kodi Bengre, Udupi, Karnataka, India", lat, lng);
            return;
        }

        callback(coordFallback, lat, lng);

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
                    console.log("Geocode offline/fallback:", err);
                });
        }, 250);
    }

    function setLocation(lat, lng, knownName) {
        const syncServer = (name, lt, lg) => {
            updateMarkerPopup(lt, lg, name);
            // Send location to FastAPI endpoint via REST fetch
            fetch("/api/study-area/location", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ location_name: name, lat: lt, lon: lg })
            }).catch(e => console.log("Location sync notice:", e));
        };

        if (knownName) {
            syncServer(knownName, lat, lng);
        } else {
            reverseGeocode(lat, lng, function(locName) {
                syncServer(locName, lat, lng);
            });
        }
    }
    window.setLocation = setLocation;

    map.on("click", function(e) {
        setLocation(e.latlng.lat, e.latlng.lng);
    });

    studyMarker.on("dragend", function(e) {
        const pos = e.target.getLatLng();
        setLocation(pos.lat, pos.lng);
    });

    markerLayerGroup.addLayer(studyMarker);
    updateMarkerPopup(STUDY_AREA_CENTER[0], STUDY_AREA_CENTER[1], currentLocationName);

    // ========================================================================
    // Location Search Control (Nominatim)
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
    // Area of Interest (AOI) Drawing Toolbar
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

        // AOI Created Event
        map.on(L.Draw.Event.CREATED, function(event) {
            drawnItems.clearLayers();
            const layer = event.layer;
            drawnItems.addLayer(layer);

            const bounds = layer.getBounds();
            const north = bounds.getNorth();
            const south = bounds.getSouth();
            const east = bounds.getEast();
            const west = bounds.getWest();

            console.log("AOI Created:", { north, south, east, west });

            // Update DOM inputs directly
            const nInput = document.getElementById("north-lat");
            const sInput = document.getElementById("south-lat");
            const eInput = document.getElementById("east-lon");
            const wInput = document.getElementById("west-lon");
            if (nInput) nInput.value = north.toFixed(6);
            if (sInput) sInput.value = south.toFixed(6);
            if (eInput) eInput.value = east.toFixed(6);
            if (wInput) wInput.value = west.toFixed(6);

            const aoiStatus = document.getElementById("aoi-status-note");
            if (aoiStatus) {
                aoiStatus.innerText = "✓ Area of Interest captured successfully";
                aoiStatus.style.color = "var(--mint)";
            }

            const readiness = document.getElementById("status-readiness");
            if (readiness) readiness.innerText = "Analysis: Ready for ML Analysis";

            // Automatically reposition study marker to AOI center
            const center = bounds.getCenter();
            setLocation(center.lat, center.lng);

            // Send AOI coordinates to FastAPI via REST
            fetch("/api/study-area/aoi", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ north, south, east, west })
            }).catch(e => console.log("AOI sync notice:", e));
        });

        map.on(L.Draw.Event.DELETED, function() {
            clearAOI();
        });
    }

    function clearAOI() {
        drawnItems.clearLayers();
        const nInput = document.getElementById("north-lat");
        const sInput = document.getElementById("south-lat");
        const eInput = document.getElementById("east-lon");
        const wInput = document.getElementById("west-lon");
        if (nInput) nInput.value = "";
        if (sInput) sInput.value = "";
        if (eInput) eInput.value = "";
        if (wInput) wInput.value = "";

        const aoiStatus = document.getElementById("aoi-status-note");
        if (aoiStatus) {
            aoiStatus.innerText = "Use top-left map toolbar to draw rectangle AOI";
            aoiStatus.style.color = "var(--muted-sage)";
        }

        const readiness = document.getElementById("status-readiness");
        if (readiness) readiness.innerText = "Analysis: Ready for AOI selection";

        fetch("/api/study-area/aoi", { method: "DELETE" }).catch(e => console.log(e));
    }
    window.clearAOI = clearAOI;

    // Mouse coordinates HUD
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
        const hud = document.getElementById("coord-hud-display");
        if (hud) hud.innerHTML = `Lat: ${latStr} | Lon: ${lngStr}`;
    });

    window.focusStudyArea = function() {
        map.setView(currentMarkerPosition, INITIAL_ZOOM);
        studyMarker.openPopup();
    };

    window.focusCurrentLocation = function() {
        map.setView(currentMarkerPosition, 13);
        studyMarker.openPopup();
    };

    window.addEventListener("resize", () => {
        if (map) map.invalidateSize();
    });

    console.log("Suvarna River Web Map Engine successfully initialized.");
}
