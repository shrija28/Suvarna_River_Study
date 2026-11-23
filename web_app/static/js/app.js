// ============================================================================
// Estuarine Mouth Dynamics - Main Web Application SPA Engine
// Manages Auth, View Routing, Analysis Workflows, and HTML5 Canvas Visualizations
// ============================================================================

(function() {
    "use strict";

    // Application Global State
    const AppState = {
        token: localStorage.getItem("suvarna_token") || null,
        user: null,
        currentView: "home",
        baseYear: 1989,
        targetYear: 2000,
        selectedYears: [1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000],
        lulcData: null,
        weatherData: null,
        deviationData: null,
    };

    window.AppState = AppState;

    // Helper: Auth Header
    function authHeader() {
        return AppState.token ? { "Authorization": `Bearer ${AppState.token}` } : {};
    }

    // ========================================================================
    // Initialization
    // ========================================================================
    document.addEventListener("DOMContentLoaded", () => {
        initAuthEvents();
        initNavigation();
        initHomeControls();
        checkExistingSession();
    });

    // ========================================================================
    // Authentication Workflow
    // ========================================================================
    function initAuthEvents() {
        const signinTab = document.getElementById("tab-signin-btn");
        const registerTab = document.getElementById("tab-register-btn");
        const forgotLink = document.getElementById("link-forgot-pwd");
        const backToSignIn1 = document.getElementById("link-back-signin-1");
        const backToSignIn2 = document.getElementById("link-back-signin-2");

        const formSignIn = document.getElementById("form-signin");
        const formRegister = document.getElementById("form-register");
        const formForgot = document.getElementById("form-forgot");

        const togglePwd = document.getElementById("toggle-signin-pwd");
        const btnLogout = document.getElementById("btn-logout");

        if (signinTab) {
            signinTab.onclick = () => {
                showAuthForm("signin");
            };
        }

        if (registerTab) {
            registerTab.onclick = () => {
                showAuthForm("register");
            };
        }

        if (forgotLink) {
            forgotLink.onclick = (e) => {
                e.preventDefault();
                showAuthForm("forgot");
            };
        }

        if (backToSignIn1) {
            backToSignIn1.onclick = (e) => {
                e.preventDefault();
                showAuthForm("signin");
            };
        }

        if (backToSignIn2) {
            backToSignIn2.onclick = (e) => {
                e.preventDefault();
                showAuthForm("signin");
            };
        }

        if (togglePwd) {
            togglePwd.onclick = () => {
                const inp = document.getElementById("signin-password");
                if (inp) {
                    inp.type = inp.type === "password" ? "text" : "password";
                }
            };
        }

        if (btnLogout) {
            btnLogout.onclick = () => {
                logout();
            };
        }

        if (formSignIn) {
            formSignIn.onsubmit = async (e) => {
                e.preventDefault();
                const u = document.getElementById("signin-username").value.trim();
                const p = document.getElementById("signin-password").value.trim();
                const rem = document.getElementById("signin-remember").checked;

                showAuthFeedback("Authenticating credentials...", "info");
                try {
                    const res = await fetch("/api/auth/login", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ username_or_email: u, password: p, remember_me: rem })
                    });
                    const data = await res.json();
                    if (!res.ok) {
                        showAuthFeedback(data.detail || "Authentication failed", "error");
                        return;
                    }

                    AppState.token = data.token;
                    AppState.user = data.user;
                    if (rem) {
                        localStorage.setItem("suvarna_token", data.token);
                    } else {
                        sessionStorage.setItem("suvarna_token", data.token);
                    }

                    onLoginSuccess(data.user);
                } catch (err) {
                    showAuthFeedback("Server connection error: " + err.message, "error");
                }
            };
        }

        if (formRegister) {
            formRegister.onsubmit = async (e) => {
                e.preventDefault();
                const u = document.getElementById("reg-username").value.trim();
                const em = document.getElementById("reg-email").value.trim();
                const fn = document.getElementById("reg-fullname").value.trim();
                const role = document.getElementById("reg-role").value;
                const p = document.getElementById("reg-password").value;
                const cp = document.getElementById("reg-confirm-password").value;

                showAuthFeedback("Registering account...", "info");
                try {
                    const res = await fetch("/api/auth/register", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            username: u, email: em, full_name: fn, role, password: p, confirm_password: cp
                        })
                    });
                    const data = await res.json();
                    if (!res.ok) {
                        showAuthFeedback(data.detail || "Registration failed", "error");
                        return;
                    }
                    showAuthFeedback("Account registered successfully! You can now sign in.", "success");
                    setTimeout(() => showAuthForm("signin"), 1500);
                } catch (err) {
                    showAuthFeedback("Registration error: " + err.message, "error");
                }
            };
        }

        if (formForgot) {
            formForgot.onsubmit = async (e) => {
                e.preventDefault();
                const u = document.getElementById("forgot-username").value.trim();
                const p = document.getElementById("forgot-password").value;
                const cp = document.getElementById("forgot-confirm-password").value;

                showAuthFeedback("Updating password...", "info");
                try {
                    const res = await fetch("/api/auth/reset-password", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ username_or_email: u, new_password: p, confirm_password: cp })
                    });
                    const data = await res.json();
                    if (!res.ok) {
                        showAuthFeedback(data.detail || "Password reset failed", "error");
                        return;
                    }
                    showAuthFeedback("Password updated successfully! Please sign in.", "success");
                    setTimeout(() => showAuthForm("signin"), 1500);
                } catch (err) {
                    showAuthFeedback("Error: " + err.message, "error");
                }
            };
        }
    }

    function showAuthForm(view) {
        document.querySelectorAll(".login-form").forEach(f => f.style.display = "none");
        document.querySelectorAll(".login-tab-btn").forEach(t => t.classList.remove("active"));
        hideAuthFeedback();

        if (view === "signin") {
            document.getElementById("form-signin").style.display = "flex";
            document.getElementById("tab-signin-btn").classList.add("active");
        } else if (view === "register") {
            document.getElementById("form-register").style.display = "flex";
            document.getElementById("tab-register-btn").classList.add("active");
        } else if (view === "forgot") {
            document.getElementById("form-forgot").style.display = "flex";
        }
    }

    function showAuthFeedback(msg, type) {
        const fb = document.getElementById("login-feedback");
        if (!fb) return;
        fb.className = `login-feedback ${type}`;
        fb.innerText = msg;
        fb.style.display = "block";
    }

    function hideAuthFeedback() {
        const fb = document.getElementById("login-feedback");
        if (fb) fb.style.display = "none";
    }

    async function checkExistingSession() {
        const token = localStorage.getItem("suvarna_token") || sessionStorage.getItem("suvarna_token");
        if (!token) {
            showLoginOverlay(true);
            return;
        }

        try {
            const res = await fetch("/api/auth/me", {
                headers: { "Authorization": `Bearer ${token}` }
            });
            if (res.ok) {
                const data = await res.json();
                AppState.token = token;
                AppState.user = data.user;
                onLoginSuccess(data.user);
            } else {
                showLoginOverlay(true);
            }
        } catch (e) {
            showLoginOverlay(true);
        }
    }

    function onLoginSuccess(user) {
        showLoginOverlay(false);

        const badge = document.getElementById("user-badge-text");
        if (badge) {
            badge.innerText = `${user.username} (${user.role || "Researcher"})`;
        }

        updateStatus({
            status: "Authenticated",
            readiness: `Active Session: ${user.username}`,
            dataText: "Landsat Multi-Spectral (1989-2026)"
        });

        // Initialize Home parameters
        navigateTo("home");
        if (window.leafletMap) {
            setTimeout(() => window.leafletMap.invalidateSize(), 200);
        }
    }

    function logout() {
        if (AppState.token) {
            fetch("/api/auth/logout", {
                method: "POST",
                headers: authHeader()
            }).catch(e => console.log(e));
        }

        AppState.token = null;
        AppState.user = null;
        localStorage.removeItem("suvarna_token");
        sessionStorage.removeItem("suvarna_token");

        showLoginOverlay(true);
        updateStatus({
            status: "Logged Out",
            readiness: "Authentication Required"
        });
    }

    function showLoginOverlay(show) {
        const overlay = document.getElementById("login-overlay");
        if (overlay) {
            overlay.style.display = show ? "flex" : "none";
        }
    }

    // ========================================================================
    // View Navigation & Sidebar Routing
    // ========================================================================
    function initNavigation() {
        document.querySelectorAll(".nav-item").forEach(item => {
            item.addEventListener("click", () => {
                const targetView = item.getAttribute("data-view");
                if (targetView) {
                    navigateTo(targetView);
                }
            });
        });
    }

    function navigateTo(viewId) {
        AppState.currentView = viewId;

        // Update active sidebar items across all pages
        document.querySelectorAll(".nav-item").forEach(item => {
            if (item.getAttribute("data-view") === viewId) {
                item.classList.add("active");
            } else {
                item.classList.remove("active");
            }
        });

        document.querySelectorAll(".nav-sidebar-btn").forEach(btn => {
            const oc = btn.getAttribute("onclick") || "";
            if (oc.includes(`'${viewId}'`) || oc.includes(`"${viewId}"`)) {
                btn.classList.add("active");
            } else {
                btn.classList.remove("active");
            }
        });

        // Update visible view
        document.querySelectorAll(".app-view").forEach(v => {
            v.classList.remove("active");
        });

        const activeViewEl = document.getElementById(`view-${viewId}`);
        if (activeViewEl) {
            activeViewEl.classList.add("active");
        }

        // Trigger view-specific data loaders
        if (viewId === "home") {
            if (window.leafletMap) {
                setTimeout(() => window.leafletMap.invalidateSize(), 150);
            }
            updateStatus({
                status: "Map Ready",
                mode: "OpenStreetMap Standard",
                readiness: "Ready for AOI selection"
            });
        } else if (viewId === "river-mouth") {
            loadRiverMouthGallery();
        } else if (viewId === "deviation") {
            loadDeviationAnalysis();
        } else if (viewId === "lulc") {
            loadLULCAnalysis();
        } else if (viewId === "weather") {
            loadWeatherAnalysis();
        } else if (viewId === "about") {
            updateStatus({
                status: "About Suvarna System",
                mode: "Documentation & Lab Info",
                readiness: "Active"
            });
        } else if (viewId === "settings") {
            updateStatus({
                status: "System Settings",
                mode: "CRS & Configuration",
                readiness: "Active"
            });
        }
    }
    window.navigateTo = navigateTo;

    function updateStatus({ status, mode, readiness, dataText }) {
        if (status) {
            const el = document.getElementById("status-map-text");
            if (el) el.innerText = status;
        }
        if (mode) {
            const el = document.getElementById("status-mode-pill");
            if (el) el.innerText = "Mode: " + mode;
        }
        if (readiness) {
            const el = document.getElementById("status-readiness");
            if (el) el.innerText = "Analysis: " + readiness;
        }
        if (dataText) {
            const el = document.getElementById("status-data");
            if (el) el.innerText = "Data: " + dataText;
        }
    }
    window.updateStatus = updateStatus;

    // ========================================================================
    // Home View Controls (Base Year, Prediction Year, Action Buttons)
    // ========================================================================
    function initHomeControls() {
        const bySelect = document.getElementById("base-year-select");
        const pySelect = document.getElementById("prediction-year-select");

        // Populate 1989-2026
        if (bySelect && pySelect) {
            bySelect.innerHTML = "";
            for (let y = 1989; y <= 2026; y++) {
                const opt = document.createElement("option");
                opt.value = y;
                opt.innerText = y;
                if (y === AppState.baseYear) opt.selected = true;
                bySelect.appendChild(opt);
            }

            function updatePredictionOptions() {
                const b = parseInt(bySelect.value, 10);
                AppState.baseYear = b;
                const prevP = parseInt(pySelect.value, 10) || 2000;

                pySelect.innerHTML = "";
                for (let y = b; y <= 2026; y++) {
                    const opt = document.createElement("option");
                    opt.value = y;
                    opt.innerText = y;
                    if (y === Math.max(b, prevP)) opt.selected = true;
                    pySelect.appendChild(opt);
                }
                AppState.targetYear = parseInt(pySelect.value, 10);
                syncSelectedYears();
            }

            bySelect.onchange = updatePredictionOptions;
            pySelect.onchange = () => {
                AppState.targetYear = parseInt(pySelect.value, 10);
                syncSelectedYears();
            };

            updatePredictionOptions();
        }

        // Action Buttons
        const btnFocus = document.getElementById("btn-focus-study");
        if (btnFocus) {
            btnFocus.onclick = () => {
                if (typeof window.focusStudyArea === "function") {
                    window.focusStudyArea();
                }
            };
        }

        const btnClear = document.getElementById("btn-clear-aoi");
        if (btnClear) {
            btnClear.onclick = () => {
                if (typeof window.clearAOI === "function") {
                    window.clearAOI();
                }
            };
        }

        const btnNext = document.getElementById("btn-next-step");
        if (btnNext) {
            btnNext.onclick = () => {
                syncServerParameters();
                navigateTo("river-mouth");
            };
        }

        const btnLulcDirect = document.getElementById("btn-quick-lulc");
        if (btnLulcDirect) {
            btnLulcDirect.onclick = () => {
                syncServerParameters();
                navigateTo("lulc");
            };
        }

        const btnDevDirect = document.getElementById("btn-quick-dev");
        if (btnDevDirect) {
            btnDevDirect.onclick = () => {
                syncServerParameters();
                navigateTo("deviation");
            };
        }

        // Map mode button triggers
        document.querySelectorAll(".mode-btn").forEach(btn => {
            btn.onclick = () => {
                const mode = btn.getAttribute("data-mode");
                if (typeof window.setMapMode === "function") {
                    window.setMapMode(mode);
                }
            };
        });
    }

    function syncSelectedYears() {
        const b = AppState.baseYear;
        const p = AppState.targetYear;
        AppState.selectedYears = [];
        for (let y = b; y <= p; y++) {
            AppState.selectedYears.push(y);
        }
        AppState.weatherStartYear = b;
        AppState.weatherEndYear = p;
        updateStatus({
            dataText: `Range: ${b}–${p} (${AppState.selectedYears.length} yrs)`
        });
    }

    function syncServerParameters() {
        const n = parseFloat(document.getElementById("north-lat")?.value || "");
        const s = parseFloat(document.getElementById("south-lat")?.value || "");
        const e = parseFloat(document.getElementById("east-lon")?.value || "");
        const w = parseFloat(document.getElementById("west-lon")?.value || "");

        const aoi = (!isNaN(n) && !isNaN(s) && !isNaN(e) && !isNaN(w)) ? { north: n, south: s, east: e, west: w } : null;

        fetch("/api/study-area/parameters", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                base_year: AppState.baseYear,
                target_year: AppState.targetYear,
                aoi: aoi
            })
        }).catch(err => console.log(err));
    }

    // ========================================================================
    // River Mouth Satellite Imagery Gallery (View 4)
    // ========================================================================
    async function loadRiverMouthGallery() {
        const grid = document.getElementById("gallery-grid-container");
        if (!grid) return;

        grid.innerHTML = `<div style="grid-column: 1/-1; text-align:center; padding: 40px; color: var(--mint);">Loading multi-decadal observations (${AppState.baseYear}–${AppState.targetYear})...</div>`;

        updateStatus({
            status: "River Mouth Imagery Gallery",
            mode: `${AppState.selectedYears.length} Observations (${AppState.baseYear}–${AppState.targetYear})`,
            readiness: "Ready for Analysis"
        });

        try {
            const res = await fetch(`/api/river-mouth/gallery?start_year=${AppState.baseYear}&end_year=${AppState.targetYear}`);
            const data = await res.json();
            const items = data.items || [];

            grid.innerHTML = "";
            items.forEach(item => {
                const card = document.createElement("div");
                card.className = "gallery-card";

                const footerText = item.width_m
                    ? `Mouth Width: ${item.width_m.toFixed(1)} m | First Opening (Drive)`
                    : (item.water_km2 ? `Estuary Water: ${item.water_km2.toFixed(2)} km² | Baseline Geometry` : `Observation: ${item.status}`);

                card.innerHTML = `
                    <div class="gallery-card-header">
                        <span class="gallery-year">${item.year}</span>
                        <a href="${item.image_url}" download="First_Opening_${item.year}.png" class="btn-chip" title="Download High-Res Observation">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                                <polyline points="7 10 12 15 17 10"></polyline>
                                <line x1="12" y1="15" x2="12" y2="3"></line>
                            </svg>
                        </a>
                    </div>
                    <div class="gallery-img-box">
                        <img src="${item.image_url}" alt="River Mouth ${item.year}" loading="lazy" onerror="this.onerror=null; this.parentElement.innerHTML='<span style=\\'font-size:11px; color:var(--muted-sage); font-style:italic;\\'>Observation plot loading...</span>';" />
                    </div>
                    <div class="gallery-footer">${footerText}</div>
                `;
                grid.appendChild(card);
            });
        } catch (e) {
            grid.innerHTML = `<div style="grid-column: 1/-1; color: var(--amber); text-align:center; padding: 20px;">Could not load gallery: ${e.message}</div>`;
        }
    }

    // ========================================================================
    // River-Mouth Deviation Analysis (View 5)
    // ========================================================================
    async function loadDeviationAnalysis() {
        const by = AppState.baseYear;
        const ty = AppState.targetYear;

        updateStatus({
            status: `River-Mouth Deviation Analysis (${by} → ${ty})`,
            mode: "Estuarine Morphodynamics",
            readiness: "Active"
        });

        // Update dropdown selectors in view header
        const bySelect = document.getElementById("dev-base-year");
        const tySelect = document.getElementById("dev-target-year");
        if (bySelect && tySelect && bySelect.options.length === 0) {
            for (let y = 1989; y <= 2026; y++) {
                bySelect.appendChild(new Option(y, y, false, y === by));
                tySelect.appendChild(new Option(y, y, false, y === ty));
            }
            bySelect.onchange = () => {
                AppState.baseYear = parseInt(bySelect.value, 10);
                loadDeviationAnalysis();
            };
            tySelect.onchange = () => {
                AppState.targetYear = parseInt(tySelect.value, 10);
                loadDeviationAnalysis();
            };
        }

        try {
            const res = await fetch(`/api/deviation/calculate?base_year=${by}&target_year=${ty}`);
            const data = await res.json();
            AppState.deviationData = data;

            // 1. Metric Summary Cards
            document.getElementById("dev-val-displacement").innerText = `${data.displacement_m.toFixed(1)} m`;
            document.getElementById("dev-badge-displacement").innerText = `${data.time_interval_years} Years`;
            document.getElementById("dev-sub-displacement").innerText = `Total Euclidean displacement from Year ${by}`;

            document.getElementById("dev-val-direction").innerText = data.direction_label;
            document.getElementById("dev-badge-direction").innerText = `${data.azimuth_deg.toFixed(0)}° Azimuth`;
            document.getElementById("dev-sub-direction").innerText = `Net migration direction of inlet mouth`;

            const areaSign = data.area_change_km2 >= 0 ? "+" : "";
            document.getElementById("dev-val-water").innerText = `${areaSign}${data.area_change_km2.toFixed(2)} km²`;
            document.getElementById("dev-badge-water").innerText = `${areaSign}${data.area_change_pct.toFixed(1)}%`;
            document.getElementById("dev-sub-water").innerText = `Water extent: ${data.base_water_area_km2.toFixed(2)} → ${data.target_water_area_km2.toFixed(2)} km²`;

            document.getElementById("dev-val-rate").innerText = `${data.annual_rate_m_yr.toFixed(2)} m/yr`;
            document.getElementById("dev-badge-rate").innerText = data.is_target_projection ? "Projected" : "Historical";
            document.getElementById("dev-sub-rate").innerText = `Average annual coastal migration velocity`;

            // 2. Render Time-Series Canvas Chart
            renderDeviationCanvas(data.timeseries, by, ty);

            // 3. Render Shift Data Table
            renderDeviationTable(data.timeseries, by, ty);

            // 4. Hook CSV Export Button
            const exportBtn = document.getElementById("btn-export-dev-csv");
            if (exportBtn) {
                exportBtn.href = `/api/deviation/export/csv?base_year=${by}&target_year=${ty}`;
            }
        } catch (e) {
            console.error("Deviation analysis error:", e);
        }
    }

    function renderDeviationCanvas(timeseries, baseYear, targetYear) {
        const canvas = document.getElementById("deviation-chart-canvas");
        if (!canvas) return;
        const ctx = canvas.getContext("2d");

        // High-DPI support
        const dpr = window.devicePixelRatio || 1;
        const rect = canvas.getBoundingClientRect();
        canvas.width = rect.width * dpr;
        canvas.height = rect.height * dpr;
        ctx.scale(dpr, dpr);

        const w = rect.width;
        const h = rect.height;

        // Background
        ctx.fillStyle = "#082B26";
        ctx.fillRect(0, 0, w, h);

        const minY = Math.min(baseYear, targetYear);
        const maxY = Math.max(baseYear, targetYear);
        const filtered = timeseries.filter(pt => pt.year >= minY && pt.year <= maxY);

        if (filtered.length === 0) {
            ctx.fillStyle = "#A8C4B7";
            ctx.font = "12px sans-serif";
            ctx.textAlign = "center";
            ctx.fillText("No displacement records in selected interval", w / 2, h / 2);
            return;
        }

        const padLeft = 65;
        const padRight = 30;
        const padTop = 30;
        const padBottom = 35;
        const plotW = w - padLeft - padRight;
        const plotH = h - padTop - padBottom;

        // Max displacement
        const maxDisp = Math.max(...filtered.map(pt => pt.displacement_m), 50.0);
        const yMax = Math.ceil(maxDisp / 50.0) * 50.0;

        // Grid lines
        ctx.strokeStyle = "#1B473D";
        ctx.lineWidth = 1;
        ctx.setLineDash([4, 4]);
        ctx.font = "10px sans-serif";
        ctx.fillStyle = "#A8C4B7";
        ctx.textAlign = "right";

        for (let i = 0; i <= 4; i++) {
            const val = (yMax / 4.0) * i;
            const yPos = padTop + plotH - (val / yMax) * plotH;
            ctx.beginPath();
            ctx.moveTo(padLeft, yPos);
            ctx.lineTo(padLeft + plotW, yPos);
            ctx.stroke();
            ctx.fillText(`${val.toFixed(0)} m`, padLeft - 8, yPos + 3);
        }
        ctx.setLineDash([]);

        // Axes
        ctx.strokeStyle = "#24574B";
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(padLeft, padTop + plotH);
        ctx.lineTo(padLeft + plotW, padTop + plotH);
        ctx.moveTo(padLeft, padTop);
        ctx.lineTo(padLeft, padTop + plotH);
        ctx.stroke();

        // Plot Line & Points
        const n = filtered.length;
        const points = [];
        for (let i = 0; i < n; i++) {
            const pt = filtered[i];
            const x = padLeft + (n === 1 ? plotW / 2 : (i / (n - 1)) * plotW);
            const y = padTop + plotH - (pt.displacement_m / yMax) * plotH;
            points.push({ x, y, pt });
        }

        // Draw Line Gradient
        ctx.beginPath();
        ctx.moveTo(points[0].x, points[0].y);
        for (let i = 1; i < points.length; i++) {
            ctx.lineTo(points[i].x, points[i].y);
        }
        ctx.strokeStyle = "#74E6B0";
        ctx.lineWidth = 2.5;
        ctx.stroke();

        // Draw Points
        points.forEach(p => {
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.pt.is_projection ? 5 : 4, 0, Math.PI * 2);
            ctx.fillStyle = p.pt.is_projection ? "#E9B866" : "#74E6B0";
            ctx.fill();
            ctx.strokeStyle = "#082B26";
            ctx.lineWidth = 1.5;
            ctx.stroke();
        });

        // X-Axis Year Labels
        ctx.fillStyle = "#A8C4B7";
        ctx.font = "9px sans-serif";
        ctx.textAlign = "center";
        const step = Math.max(1, Math.floor(n / 10));
        for (let i = 0; i < n; i += step) {
            ctx.fillText(filtered[i].year, points[i].x, padTop + plotH + 16);
        }

        // Legend
        ctx.textAlign = "left";
        ctx.fillStyle = "#74E6B0";
        ctx.fillText("● Ground Truth", w - 210, 18);
        ctx.fillStyle = "#E9B866";
        ctx.fillText("● AI Projection", w - 100, 18);
    }

    function renderDeviationTable(timeseries, baseYear, targetYear) {
        const tbody = document.querySelector("#deviation-data-table tbody");
        if (!tbody) return;
        tbody.innerHTML = "";

        const minY = Math.min(baseYear, targetYear);
        const maxY = Math.max(baseYear, targetYear);
        const filtered = timeseries.filter(pt => pt.year >= minY && pt.year <= maxY);

        filtered.forEach(row => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><b>${row.year}</b></td>
                <td><span class="btn-chip ${row.is_projection ? 'amber' : ''}">${row.obs_type}</span></td>
                <td>${row.mouth_lat ? row.mouth_lat.toFixed(4) + '° N' : '--'}</td>
                <td>${row.mouth_lon ? row.mouth_lon.toFixed(4) + '° E' : '--'}</td>
                <td><b>${row.displacement_m.toFixed(1)} m</b></td>
                <td>${row.direction}</td>
                <td>${row.water_area_km2.toFixed(2)} km²</td>
                <td>${row.opening_width_m ? row.opening_width_m.toFixed(1) + ' m' : 'N/A'}</td>
                <td>${row.rate_m_yr.toFixed(2)} m/yr</td>
            `;
            tbody.appendChild(tr);
        });
    }

    // ========================================================================
    // Land Use / Land Cover (LULC) Analysis (View 1)
    // ========================================================================
    async function loadLULCAnalysis() {
        updateStatus({
            status: "LULC Classification Page",
            mode: "4-Class Satellite Classification",
            readiness: "Active"
        });

        try {
            const res = await fetch("/api/lulc/master-records");
            const data = await res.json();
            AppState.lulcData = data.records || [];

            // Year selection dropdown in LULC header
            const yrSelect = document.getElementById("lulc-year-select");
            if (yrSelect && yrSelect.options.length === 0) {
                AppState.lulcData.forEach(r => {
                    yrSelect.appendChild(new Option(r.year, r.year, false, r.year === AppState.baseYear));
                });
                yrSelect.onchange = () => {
                    renderLULCSelectedYear(parseInt(yrSelect.value, 10));
                };
            }

            renderLULCSelectedYear(AppState.baseYear);
            renderLULCTimeseriesChart(AppState.lulcData, "water_body");
            renderLULCTable(AppState.lulcData);

            // Filter buttons
            document.querySelectorAll(".lulc-filter-btn").forEach(btn => {
                btn.onclick = () => {
                    document.querySelectorAll(".lulc-filter-btn").forEach(b => b.classList.remove("active"));
                    btn.classList.add("active");
                    const filter = btn.getAttribute("data-filter");
                    renderLULCTimeseriesChart(AppState.lulcData, filter);
                };
            });
        } catch (e) {
            console.error("LULC load error:", e);
        }
    }

    function renderLULCSelectedYear(year) {
        const rec = AppState.lulcData.find(r => r.year === year) || AppState.lulcData[0];
        if (!rec) return;

        document.getElementById("lulc-veg-val").innerText = `${rec.vegetation_km2.toFixed(2)} km²`;
        document.getElementById("lulc-veg-badge").innerText = `${rec.vegetation_pct.toFixed(1)} %`;

        document.getElementById("lulc-water-val").innerText = `${rec.water_km2.toFixed(2)} km²`;
        document.getElementById("lulc-water-badge").innerText = `${rec.water_pct.toFixed(1)} %`;

        document.getElementById("lulc-barren-val").innerText = `${rec.barren_km2.toFixed(2)} km²`;
        document.getElementById("lulc-barren-badge").innerText = `${rec.barren_pct.toFixed(1)} %`;

        document.getElementById("lulc-built-val").innerText = `${rec.builtup_km2.toFixed(2)} km²`;
        document.getElementById("lulc-built-badge").innerText = `${rec.builtup_pct.toFixed(1)} %`;

        // Update LULC Map Preview image
        const imgEl = document.getElementById("lulc-map-image");
        if (imgEl) {
            imgEl.src = `/api/lulc/image/${year}`;
            imgEl.onerror = () => {
                imgEl.src = "/assets/map_placeholder.png";
            };
        }
    }

    function renderLULCTimeseriesChart(records, filter) {
        const canvas = document.getElementById("lulc-chart-canvas");
        if (!canvas) return;
        const ctx = canvas.getContext("2d");

        const dpr = window.devicePixelRatio || 1;
        const rect = canvas.getBoundingClientRect();
        canvas.width = rect.width * dpr;
        canvas.height = rect.height * dpr;
        ctx.scale(dpr, dpr);

        const w = rect.width;
        const h = rect.height;

        ctx.fillStyle = "#082B26";
        ctx.fillRect(0, 0, w, h);

        const padLeft = 60;
        const padRight = 20;
        const padTop = 30;
        const padBottom = 35;
        const plotW = w - padLeft - padRight;
        const plotH = h - padTop - padBottom;

        const n = records.length;
        if (n === 0) return;

        // Max calculation
        let maxVal = 1000.0;
        if (filter === "water_body") maxVal = 850.0;
        else if (filter === "vegetation") maxVal = 750.0;
        else if (filter === "barren_land") maxVal = 250.0;
        else if (filter === "built_up") maxVal = 150.0;
        else maxVal = 1600.0; // stacked

        // Grid lines
        ctx.strokeStyle = "#1B473D";
        ctx.lineWidth = 1;
        ctx.setLineDash([4, 4]);
        ctx.fillStyle = "#A8C4B7";
        ctx.font = "9px sans-serif";
        ctx.textAlign = "right";

        for (let i = 0; i <= 4; i++) {
            const val = (maxVal / 4.0) * i;
            const yPos = padTop + plotH - (val / maxVal) * plotH;
            ctx.beginPath();
            ctx.moveTo(padLeft, yPos);
            ctx.lineTo(padLeft + plotW, yPos);
            ctx.stroke();
            ctx.fillText(`${val.toFixed(0)} km²`, padLeft - 6, yPos + 3);
        }
        ctx.setLineDash([]);

        // Bars
        const barSlot = plotW / n;
        const barW = Math.max(3, barSlot * 0.7);

        for (let i = 0; i < n; i++) {
            const r = records[i];
            const bx = padLeft + i * barSlot + (barSlot - barW) / 2.0;

            if (filter === "stacked") {
                // Stacked classes
                let currentY = padTop + plotH;
                const classes = [
                    { val: r.water_km2, col: "#1E88E5" },
                    { val: r.vegetation_km2, col: "#2E7D32" },
                    { val: r.barren_km2, col: "#E6C654" },
                    { val: r.builtup_km2, col: "#D84315" }
                ];
                classes.forEach(c => {
                    const bh = (c.val / maxVal) * plotH;
                    currentY -= bh;
                    ctx.fillStyle = c.col;
                    ctx.fillRect(bx, currentY, barW, bh);
                });
            } else {
                let v = r.water_km2;
                let color = "#1E88E5";
                if (filter === "vegetation") { v = r.vegetation_km2; color = "#2E7D32"; }
                else if (filter === "barren_land") { v = r.barren_km2; color = "#E6C654"; }
                else if (filter === "built_up") { v = r.builtup_km2; color = "#D84315"; }

                const bh = (v / maxVal) * plotH;
                const by = padTop + plotH - bh;
                ctx.fillStyle = color;
                ctx.fillRect(bx, by, barW, bh);
            }
        }

        // X Labels
        ctx.fillStyle = "#A8C4B7";
        ctx.font = "9px sans-serif";
        ctx.textAlign = "center";
        const step = Math.max(1, Math.floor(n / 10));
        for (let i = 0; i < n; i += step) {
            const x = padLeft + (i + 0.5) * barSlot;
            ctx.fillText(records[i].year, x, padTop + plotH + 16);
        }
    }

    function renderLULCTable(records) {
        const tbody = document.querySelector("#lulc-data-table tbody");
        if (!tbody) return;
        tbody.innerHTML = "";

        records.forEach(r => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><b>${r.year}</b></td>
                <td style="color:#2E7D32;">${r.vegetation_km2.toFixed(2)} (${r.vegetation_pct.toFixed(1)}%)</td>
                <td style="color:#1E88E5;">${r.water_km2.toFixed(2)} (${r.water_pct.toFixed(1)}%)</td>
                <td style="color:#E6C654;">${r.barren_km2.toFixed(2)} (${r.barren_pct.toFixed(1)}%)</td>
                <td style="color:#D84315;">${r.builtup_km2.toFixed(2)} (${r.builtup_pct.toFixed(1)}%)</td>
                <td><b>${r.total_km2.toFixed(2)} km²</b></td>
            `;
            tbody.appendChild(tr);
        });
    }

    // ========================================================================
    // Weather Data Analysis (View 2)
    // Synchronized strictly with user-selected years from Home page or Weather toolbar
    // ========================================================================
    let currentWeatherMode = "rain";

    async function loadWeatherAnalysis() {
        const startSel = document.getElementById("weather-start-year");
        const endSel = document.getElementById("weather-end-year");

        // Sync with AppState's active baseYear and targetYear selected on Home page
        let sy = AppState.weatherStartYear || AppState.baseYear || 1989;
        let ey = AppState.weatherEndYear || AppState.targetYear || 2026;
        if (sy > ey) {
            const tmp = sy; sy = ey; ey = tmp;
        }
        AppState.weatherStartYear = sy;
        AppState.weatherEndYear = ey;

        updateStatus({
            status: `Meteorological Records (${sy}–${ey})`,
            mode: "IMD / ERA5 Reanalysis Calibrated",
            readiness: "Active"
        });

        // Initialize dropdowns once or populate if empty
        if (startSel && endSel && startSel.options.length === 0) {
            for (let y = 1989; y <= 2026; y++) {
                startSel.appendChild(new Option(y, y, false, y === sy));
                endSel.appendChild(new Option(y, y, false, y === ey));
            }

            startSel.onchange = () => {
                let newS = parseInt(startSel.value, 10);
                let newE = parseInt(endSel.value, 10);
                if (newS > newE) {
                    newE = newS;
                    endSel.value = newE;
                }
                AppState.weatherStartYear = newS;
                AppState.weatherEndYear = newE;
                fetchAndRenderWeather(newS, newE);
            };

            endSel.onchange = () => {
                let newS = parseInt(startSel.value, 10);
                let newE = parseInt(endSel.value, 10);
                if (newE < newS) {
                    newS = newE;
                    startSel.value = newS;
                }
                AppState.weatherStartYear = newS;
                AppState.weatherEndYear = newE;
                fetchAndRenderWeather(newS, newE);
            };

            const btnReset = document.getElementById("btn-weather-reset");
            if (btnReset) {
                btnReset.onclick = () => {
                    const defaultS = AppState.baseYear || 1989;
                    const defaultE = AppState.targetYear || 2026;
                    AppState.weatherStartYear = defaultS;
                    AppState.weatherEndYear = defaultE;
                    startSel.value = defaultS;
                    endSel.value = defaultE;
                    fetchAndRenderWeather(defaultS, defaultE);
                };
            }

            document.querySelectorAll(".weather-mode-btn").forEach(btn => {
                btn.onclick = () => {
                    document.querySelectorAll(".weather-mode-btn").forEach(b => b.classList.remove("active"));
                    btn.classList.add("active");
                    currentWeatherMode = btn.getAttribute("data-mode");
                    renderWeatherView();
                };
            });
        } else if (startSel && endSel) {
            // Keep dropdowns in sync if user modified them on Home page
            startSel.value = sy;
            endSel.value = ey;
        }

        await fetchAndRenderWeather(sy, ey);
    }

    async function fetchAndRenderWeather(startYear, endYear) {
        try {
            const res = await fetch(`/api/weather/annual?start_year=${startYear}&end_year=${endYear}`);
            const data = await res.json();
            AppState.weatherRecords = data.records || [];
            renderWeatherView();
        } catch (e) {
            console.error("Weather load error:", e);
        }
    }

    function renderWeatherView() {
        const records = AppState.weatherRecords || [];
        const sy = AppState.weatherStartYear || 1989;
        const ey = AppState.weatherEndYear || 2026;

        // 1. Update Summary Statistics Bar for selected years
        const nYears = records.length;
        const periodBadge = document.getElementById("weather-stat-period-badge");
        if (periodBadge) periodBadge.innerText = `${nYears} Year${nYears === 1 ? '' : 's'}`;

        const periodEl = document.getElementById("weather-stat-period");
        if (periodEl) periodEl.innerText = `${sy} – ${ey}`;

        const rains = records.map(r => r.annual_rainfall_mm).filter(v => v != null);
        const temps = records.map(r => r.avg_temp).filter(v => v != null);
        const hums = records.map(r => r.avg_humidity).filter(v => v != null);

        const meanRain = rains.length ? (rains.reduce((a, b) => a + b, 0) / rains.length) : 0;
        const meanTemp = temps.length ? (temps.reduce((a, b) => a + b, 0) / temps.length) : 0;
        const meanHum = hums.length ? (hums.reduce((a, b) => a + b, 0) / hums.length) : 0;

        const rainEl = document.getElementById("weather-stat-rain");
        if (rainEl) rainEl.innerText = `${meanRain.toFixed(0)} mm/yr`;

        const tempEl = document.getElementById("weather-stat-temp");
        if (tempEl) tempEl.innerText = `${meanTemp.toFixed(2)} °C`;

        const humEl = document.getElementById("weather-stat-hum");
        if (humEl) humEl.innerText = `${meanHum.toFixed(1)} %`;

        // Update titles and legend
        const chartTitle = document.getElementById("weather-chart-title");
        const legendEl = document.getElementById("weather-chart-legend");
        const tableTitle = document.getElementById("weather-table-title");

        const modeNames = {
            rain: "Annual Precipitation & Runoff",
            temp: "Mean Coastal Temperature",
            hum: "Relative Air Humidity",
            all: "Combined Multi-Parameter Climate Trends"
        };

        if (chartTitle) chartTitle.innerText = `${modeNames[currentWeatherMode] || 'Weather Records'} (${sy} – ${ey})`;
        if (tableTitle) tableTitle.innerText = `Annual Meteorological Records for Selected Years (${sy} – ${ey})`;

        if (legendEl) {
            if (currentWeatherMode === "rain") {
                legendEl.innerText = `● Teal: Annual Rainfall (mm) | --- Amber: Selection Mean (${meanRain.toFixed(0)} mm) | ★ Amber: Partial/Projected Year`;
            } else if (currentWeatherMode === "temp") {
                legendEl.innerText = `● Amber Line: Avg Temperature (°C) | Shaded Area: Thermal Range (${meanTemp.toFixed(2)}°C Mean)`;
            } else if (currentWeatherMode === "hum") {
                legendEl.innerText = `● Mint Green Line: Relative Humidity (%) | Shaded Area: Marine Inflow (${meanHum.toFixed(1)}% Mean)`;
            } else {
                legendEl.innerText = `● Teal Bars: Rainfall (mm) | ● Amber: Temp (°C) | ● Mint: Humidity (%)`;
            }
        }

        // Update CSV download link
        const csvBtn = document.getElementById("btn-download-weather-csv");
        if (csvBtn) csvBtn.href = `/api/weather/export/csv?start_year=${sy}&end_year=${ey}`;

        // 2. Render Canvas Chart for only selected records
        renderWeatherCanvas(records, currentWeatherMode);

        // 3. Render Table for only selected records
        renderWeatherTable(records);
    }

    function renderWeatherCanvas(records, mode) {
        const canvas = document.getElementById("weather-chart-canvas");
        if (!canvas) return;
        const ctx = canvas.getContext("2d");

        const dpr = window.devicePixelRatio || 1;
        const rect = canvas.getBoundingClientRect();
        canvas.width = rect.width * dpr;
        canvas.height = rect.height * dpr;
        ctx.scale(dpr, dpr);

        const w = rect.width;
        const h = rect.height;

        ctx.fillStyle = "#082B26";
        ctx.fillRect(0, 0, w, h);

        const padLeft = 70;
        const padRight = (mode === "all" ? 65 : 30);
        const padTop = 32;
        const padBottom = 35;
        const plotW = w - padLeft - padRight;
        const plotH = h - padTop - padBottom;

        const n = records.length;
        if (n === 0) {
            ctx.fillStyle = "#A8C4B7";
            ctx.font = "12px sans-serif";
            ctx.textAlign = "center";
            ctx.fillText("No weather data records in selected year range", w / 2, h / 2);
            return;
        }

        // Mode 1: Rainfall (mm)
        if (mode === "rain") {
            const rains = records.map(r => r.annual_rainfall_mm || 0);
            const maxRain = Math.max(...rains, 2000);
            const yMax = Math.ceil(maxRain / 500) * 500;
            const meanRain = rains.reduce((a, b) => a + b, 0) / Math.max(1, rains.length);

            // Horizontal Grid Lines & Y-Axis Labels
            ctx.strokeStyle = "#1B473D";
            ctx.setLineDash([4, 4]);
            ctx.font = "10px sans-serif";
            ctx.fillStyle = "#A8C4B7";
            ctx.textAlign = "right";

            const step = yMax <= 3000 ? 500 : 1000;
            for (let v = 0; v <= yMax; v += step) {
                const yPos = padTop + plotH - (v / yMax) * plotH;
                ctx.beginPath();
                ctx.moveTo(padLeft, yPos);
                ctx.lineTo(padLeft + plotW, yPos);
                ctx.stroke();
                ctx.fillText(`${v.toLocaleString()} mm`, padLeft - 8, yPos + 3);
            }
            ctx.setLineDash([]);

            // Axes
            ctx.strokeStyle = "#24574B";
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.moveTo(padLeft, padTop + plotH);
            ctx.lineTo(padLeft + plotW, padTop + plotH);
            ctx.moveTo(padLeft, padTop);
            ctx.lineTo(padLeft + plotW, padTop);
            ctx.stroke();

            // Period Mean Baseline Guideline (Amber dashed)
            const yMean = padTop + plotH - (meanRain / yMax) * plotH;
            ctx.strokeStyle = "#E9B866";
            ctx.lineWidth = 1.2;
            ctx.setLineDash([5, 4]);
            ctx.beginPath();
            ctx.moveTo(padLeft, yMean);
            ctx.lineTo(padLeft + plotW, yMean);
            ctx.stroke();
            ctx.setLineDash([]);

            ctx.fillStyle = "#E9B866";
            ctx.font = "bold 9px sans-serif";
            ctx.textAlign = "right";
            ctx.fillText(`Period Mean: ${meanRain.toFixed(0)} mm`, padLeft + plotW - 6, yMean - 5);

            // Draw Bars for selected years
            const barSlot = plotW / n;
            const barW = Math.max(6, Math.min(45, barSlot * 0.68));

            for (let i = 0; i < n; i++) {
                const r = records[i];
                const val = r.annual_rainfall_mm || 0;
                const bh = (val / yMax) * plotH;
                const bx = padLeft + i * barSlot + (barSlot - barW) / 2.0;
                const by = padTop + plotH - bh;

                // Gradient Bar
                const grad = ctx.createLinearGradient(0, by, 0, padTop + plotH);
                if (r.is_incomplete) {
                    grad.addColorStop(0, "#E9B866");
                    grad.addColorStop(1, "rgba(233, 184, 102, 0.2)");
                } else {
                    grad.addColorStop(0, "#00BFA5");
                    grad.addColorStop(1, "rgba(8, 43, 38, 0.3)");
                }

                ctx.fillStyle = grad;
                ctx.fillRect(bx, by, barW, bh);

                ctx.strokeStyle = r.is_incomplete ? "#E9B866" : "#74E6B0";
                ctx.lineWidth = 1;
                ctx.strokeRect(bx, by, barW, bh);

                // Bar Top Value Label
                if (barW >= 18 || n <= 15) {
                    ctx.fillStyle = r.is_incomplete ? "#E9B866" : "#74E6B0";
                    ctx.font = "9px sans-serif";
                    ctx.textAlign = "center";
                    ctx.fillText(`${Math.round(val)}`, bx + barW / 2, by - 4);
                }
            }

            // X-Axis Year Labels
            ctx.fillStyle = "#A8C4B7";
            ctx.font = "10px sans-serif";
            ctx.textAlign = "center";
            const lblStep = n > 20 ? 2 : 1;
            for (let i = 0; i < n; i += lblStep) {
                const x = padLeft + (i + 0.5) * barSlot;
                ctx.fillText(records[i].year, x, padTop + plotH + 16);
            }
        }

        // Mode 2: Temperature (°C)
        else if (mode === "temp") {
            const temps = records.map(r => r.avg_temp).filter(v => v != null);
            const minT = Math.min(...temps, 25.0);
            const maxT = Math.max(...temps, 28.5);
            const yMin = Math.floor(minT * 2) / 2 - 0.5;
            const yMax = Math.ceil(maxT * 2) / 2 + 0.5;
            const tSpan = Math.max(0.5, yMax - yMin);

            // Grid lines
            ctx.strokeStyle = "#1B473D";
            ctx.setLineDash([4, 4]);
            ctx.font = "10px sans-serif";
            ctx.fillStyle = "#A8C4B7";
            ctx.textAlign = "right";

            for (let v = yMin; v <= yMax + 0.01; v += 0.5) {
                const yPos = padTop + plotH - ((v - yMin) / tSpan) * plotH;
                ctx.beginPath();
                ctx.moveTo(padLeft, yPos);
                ctx.lineTo(padLeft + plotW, yPos);
                ctx.stroke();
                ctx.fillText(`${v.toFixed(1)} °C`, padLeft - 8, yPos + 3);
            }
            ctx.setLineDash([]);

            // Axes
            ctx.strokeStyle = "#24574B";
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.moveTo(padLeft, padTop + plotH);
            ctx.lineTo(padLeft + plotW, padTop + plotH);
            ctx.moveTo(padLeft, padTop);
            ctx.lineTo(padLeft, padTop + plotH);
            ctx.stroke();

            // Calculate point coordinates
            const points = [];
            for (let i = 0; i < n; i++) {
                const r = records[i];
                const x = n === 1 ? padLeft + plotW / 2 : padLeft + (i / (n - 1)) * plotW;
                const y = padTop + plotH - ((r.avg_temp - yMin) / tSpan) * plotH;
                points.push({ x, y, r });
            }

            // Shaded Area Under Curve
            if (points.length > 1) {
                const grad = ctx.createLinearGradient(0, padTop, 0, padTop + plotH);
                grad.addColorStop(0, "rgba(233, 184, 102, 0.35)");
                grad.addColorStop(1, "rgba(8, 43, 38, 0.05)");

                ctx.beginPath();
                ctx.moveTo(points[0].x, padTop + plotH);
                points.forEach(p => ctx.lineTo(p.x, p.y));
                ctx.lineTo(points[points.length - 1].x, padTop + plotH);
                ctx.closePath();
                ctx.fillStyle = grad;
                ctx.fill();
            }

            // Line
            ctx.strokeStyle = "#E9B866";
            ctx.lineWidth = 2.5;
            ctx.beginPath();
            ctx.moveTo(points[0].x, points[0].y);
            for (let i = 1; i < points.length; i++) {
                ctx.lineTo(points[i].x, points[i].y);
            }
            ctx.stroke();

            // Points & Labels
            points.forEach(p => {
                ctx.beginPath();
                ctx.arc(p.x, p.y, 4, 0, Math.PI * 2);
                ctx.fillStyle = "#E9B866";
                ctx.fill();
                ctx.strokeStyle = "#082B26";
                ctx.lineWidth = 1.5;
                ctx.stroke();

                if (n <= 16) {
                    ctx.fillStyle = "#E9B866";
                    ctx.font = "9px sans-serif";
                    ctx.textAlign = "center";
                    ctx.fillText(`${p.r.avg_temp.toFixed(1)}°`, p.x, p.y - 7);
                }
            });

            // X-Axis Labels
            ctx.fillStyle = "#A8C4B7";
            ctx.font = "10px sans-serif";
            ctx.textAlign = "center";
            const lblStep = n > 20 ? 2 : 1;
            for (let i = 0; i < n; i += lblStep) {
                ctx.fillText(points[i].r.year, points[i].x, padTop + plotH + 16);
            }
        }

        // Mode 3: Relative Humidity (%)
        else if (mode === "hum") {
            const hums = records.map(r => r.avg_humidity).filter(v => v != null);
            const minH = Math.min(...hums, 70.0);
            const maxH = Math.max(...hums, 90.0);
            const yMin = Math.max(50, Math.floor(minH / 5) * 5 - 5);
            const yMax = Math.min(100, Math.ceil(maxH / 5) * 5 + 5);
            const hSpan = Math.max(5, yMax - yMin);

            // Grid lines
            ctx.strokeStyle = "#1B473D";
            ctx.setLineDash([4, 4]);
            ctx.font = "10px sans-serif";
            ctx.fillStyle = "#A8C4B7";
            ctx.textAlign = "right";

            for (let v = yMin; v <= yMax; v += 5) {
                const yPos = padTop + plotH - ((v - yMin) / hSpan) * plotH;
                ctx.beginPath();
                ctx.moveTo(padLeft, yPos);
                ctx.lineTo(padLeft + plotW, yPos);
                ctx.stroke();
                ctx.fillText(`${v}%`, padLeft - 8, yPos + 3);
            }
            ctx.setLineDash([]);

            // Axes
            ctx.strokeStyle = "#24574B";
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.moveTo(padLeft, padTop + plotH);
            ctx.lineTo(padLeft + plotW, padTop + plotH);
            ctx.moveTo(padLeft, padTop);
            ctx.lineTo(padLeft, padTop + plotH);
            ctx.stroke();

            // Points
            const points = [];
            for (let i = 0; i < n; i++) {
                const r = records[i];
                const x = n === 1 ? padLeft + plotW / 2 : padLeft + (i / (n - 1)) * plotW;
                const y = padTop + plotH - ((r.avg_humidity - yMin) / hSpan) * plotH;
                points.push({ x, y, r });
            }

            // Shaded Area
            if (points.length > 1) {
                const grad = ctx.createLinearGradient(0, padTop, 0, padTop + plotH);
                grad.addColorStop(0, "rgba(116, 230, 176, 0.35)");
                grad.addColorStop(1, "rgba(8, 43, 38, 0.05)");

                ctx.beginPath();
                ctx.moveTo(points[0].x, padTop + plotH);
                points.forEach(p => ctx.lineTo(p.x, p.y));
                ctx.lineTo(points[points.length - 1].x, padTop + plotH);
                ctx.closePath();
                ctx.fillStyle = grad;
                ctx.fill();
            }

            // Line
            ctx.strokeStyle = "#74E6B0";
            ctx.lineWidth = 2.5;
            ctx.beginPath();
            ctx.moveTo(points[0].x, points[0].y);
            for (let i = 1; i < points.length; i++) {
                ctx.lineTo(points[i].x, points[i].y);
            }
            ctx.stroke();

            // Points & Labels
            points.forEach(p => {
                ctx.beginPath();
                ctx.arc(p.x, p.y, 4, 0, Math.PI * 2);
                ctx.fillStyle = "#74E6B0";
                ctx.fill();
                ctx.strokeStyle = "#082B26";
                ctx.lineWidth = 1.5;
                ctx.stroke();

                if (n <= 16) {
                    ctx.fillStyle = "#74E6B0";
                    ctx.font = "9px sans-serif";
                    ctx.textAlign = "center";
                    ctx.fillText(`${p.r.avg_humidity.toFixed(0)}%`, p.x, p.y - 7);
                }
            });

            // X-Axis Labels
            ctx.fillStyle = "#A8C4B7";
            ctx.font = "10px sans-serif";
            ctx.textAlign = "center";
            const lblStep = n > 20 ? 2 : 1;
            for (let i = 0; i < n; i += lblStep) {
                ctx.fillText(points[i].r.year, points[i].x, padTop + plotH + 16);
            }
        }

        // Mode 4: Combined (Rainfall Bars + Temp & Humidity Lines)
        else if (mode === "all") {
            const rains = records.map(r => r.annual_rainfall_mm || 0);
            const maxRain = Math.max(...rains, 2000);
            const yMaxRain = Math.ceil(maxRain / 1000) * 1000;

            // Dual axis: Left is Rain, Right is 0-100 scale (for Humidity % & scaled Temp)
            ctx.strokeStyle = "#1B473D";
            ctx.setLineDash([4, 4]);
            ctx.font = "10px sans-serif";

            for (let i = 0; i <= 4; i++) {
                const rVal = (yMaxRain / 4) * i;
                const yPos = padTop + plotH - (i / 4) * plotH;
                ctx.beginPath();
                ctx.moveTo(padLeft, yPos);
                ctx.lineTo(padLeft + plotW, yPos);
                ctx.stroke();

                // Left label (Rain)
                ctx.fillStyle = "#00BFA5";
                ctx.textAlign = "right";
                ctx.fillText(`${rVal.toFixed(0)}mm`, padLeft - 6, yPos + 3);

                // Right label (%)
                ctx.fillStyle = "#74E6B0";
                ctx.textAlign = "left";
                ctx.fillText(`${(i * 25)}%`, padLeft + plotW + 6, yPos + 3);
            }
            ctx.setLineDash([]);

            // Draw Rainfall Bars
            const barSlot = plotW / n;
            const barW = Math.max(5, Math.min(36, barSlot * 0.6));
            for (let i = 0; i < n; i++) {
                const r = records[i];
                const val = r.annual_rainfall_mm || 0;
                const bh = (val / yMaxRain) * plotH;
                const bx = padLeft + i * barSlot + (barSlot - barW) / 2.0;
                const by = padTop + plotH - bh;

                ctx.fillStyle = "rgba(0, 191, 165, 0.4)";
                ctx.fillRect(bx, by, barW, bh);
                ctx.strokeStyle = "#00BFA5";
                ctx.lineWidth = 1;
                ctx.strokeRect(bx, by, barW, bh);
            }

            // Draw Humidity Line (Scaled 0-100 on Right Axis)
            ctx.strokeStyle = "#74E6B0";
            ctx.lineWidth = 2;
            ctx.beginPath();
            for (let i = 0; i < n; i++) {
                const r = records[i];
                const x = padLeft + (i + 0.5) * barSlot;
                const y = padTop + plotH - (r.avg_humidity / 100.0) * plotH;
                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            }
            ctx.stroke();

            // Draw Temperature Line (Scaled: e.g. 20-35°C mapped to 0-100)
            ctx.strokeStyle = "#E9B866";
            ctx.lineWidth = 2;
            ctx.beginPath();
            for (let i = 0; i < n; i++) {
                const r = records[i];
                const tScaled = Math.max(0, Math.min(100, (r.avg_temp - 20.0) / 15.0 * 100.0));
                const x = padLeft + (i + 0.5) * barSlot;
                const y = padTop + plotH - (tScaled / 100.0) * plotH;
                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            }
            ctx.stroke();

            // X-Axis Labels
            ctx.fillStyle = "#A8C4B7";
            ctx.font = "10px sans-serif";
            ctx.textAlign = "center";
            const lblStep = n > 20 ? 2 : 1;
            for (let i = 0; i < n; i += lblStep) {
                const x = padLeft + (i + 0.5) * barSlot;
                ctx.fillText(records[i].year, x, padTop + plotH + 16);
            }
        }
    }

    function renderWeatherTable(records) {
        const tbody = document.querySelector("#weather-data-table tbody");
        if (!tbody) return;
        tbody.innerHTML = "";

        if (records.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:20px; color:var(--muted-sage);">No meteorological records available for the selected years.</td></tr>`;
            return;
        }

        records.forEach(r => {
            const tr = document.createElement("tr");
            const isPartial = r.is_incomplete;
            tr.innerHTML = `
                <td><b style="${isPartial ? 'color:var(--amber);' : ''}">${r.year}</b></td>
                <td style="color:#E9B866; font-weight:600;">${r.avg_temp ? r.avg_temp.toFixed(2) + ' °C' : '--'}</td>
                <td style="color:var(--muted-sage);">${r.avg_temp_min && r.avg_temp_max ? r.avg_temp_min.toFixed(1) + ' – ' + r.avg_temp_max.toFixed(1) + ' °C' : '--'}</td>
                <td style="color:#74E6B0; font-weight:600;">${r.avg_humidity ? r.avg_humidity.toFixed(1) + ' %' : '--'}</td>
                <td style="color:#00BFA5; font-weight:700;">${r.annual_rainfall_mm != null ? r.annual_rainfall_mm.toLocaleString(undefined, {minimumFractionDigits: 1, maximumFractionDigits: 1}) + ' mm' : '--'}</td>
                <td style="color:var(--warm-ivory);">${r.monsoon_rainfall_mm != null ? r.monsoon_rainfall_mm.toLocaleString(undefined, {minimumFractionDigits: 1, maximumFractionDigits: 1}) + ' mm' : '--'}</td>
                <td><span class="btn-chip ${isPartial ? 'amber' : ''}">${r.status_note || (isPartial ? 'Partial Observation' : 'Complete Record')}</span></td>
            `;
            tbody.appendChild(tr);
        });
    }

})();
