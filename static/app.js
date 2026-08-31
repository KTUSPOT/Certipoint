/**
 * Certipoint - KTU Activity Point Analysis Application Logic
 */

document.addEventListener("DOMContentLoaded", () => {
    // State
    let currentRules = {};
    let activePreset = "blood_donation";

    // DOM Elements
    const certForm = document.getElementById("cert-form");
    const selectCategory = document.getElementById("select-category");
    const selectLevel = document.getElementById("select-level");
    const resultContent = document.getElementById("result-content");
    const resultStatusBadge = document.getElementById("result-status-badge");
    const rawResponseJson = document.getElementById("raw-response-json");
    const rawJsonToggle = document.getElementById("raw-json-toggle");
    
    // Tab switching
    const tabForm = document.getElementById("tab-form");
    const tabJson = document.getElementById("tab-json");
    const formInput = document.getElementById("cert-form");
    const jsonInputContainer = document.getElementById("json-input-container");
    const rawJsonEditor = document.getElementById("raw-json-editor");
    const btnSubmitJson = document.getElementById("btn-submit-json");

    // Presets
    const presetButtons = document.querySelectorAll(".btn-preset");

    // Dashboard Elements
    const statTotalPoints = document.getElementById("stat-total-points");
    const statProgressFill = document.getElementById("stat-progress-fill");
    const statValidCount = document.getElementById("stat-valid-count");
    const statDuplicateCount = document.getElementById("stat-duplicate-count");
    const statStudentName = document.getElementById("stat-student-name");
    const historyTableBody = document.getElementById("history-table-body");
    const tableLogCount = document.getElementById("table-log-count");

    // Rules
    const rulesMatrixGrid = document.getElementById("rules-matrix-grid");
    const btnResetRules = document.getElementById("btn-reset-rules");
    const btnEditRulesJson = document.getElementById("btn-edit-rules-json");
    const rulesModal = document.getElementById("rules-modal");
    const modalRulesTextarea = document.getElementById("modal-rules-textarea");
    const modalSaveBtn = document.getElementById("modal-save-btn");
    const modalCancelBtn = document.getElementById("modal-cancel-btn");
    const modalCloseBtn = document.getElementById("modal-close-btn");

    // DB Clear
    const btnClearDb = document.getElementById("btn-clear-db");

    // Theme Toggle
    const themeToggleBtn = document.getElementById("theme-toggle-btn");

    // Quick Preset Definitions
    const PRESETS = {
        blood_donation: {
            student_name: "Jithu",
            activity: "Blood Donation",
            organization: "NSS Unit",
            date: "15-08-2026",
            certificate_id: "NSS12345",
            category: "Social Service",
            level: "Participation",
            confidence: 0.95
        },
        nss_camp: {
            student_name: "Jithu",
            activity: "7-Day Special Camp",
            organization: "NSS Cell",
            date: "20-07-2026",
            certificate_id: "NSS-CAMP-401",
            category: "NSS / NCC",
            level: "Camp",
            confidence: 0.98
        },
        hackathon_winner: {
            student_name: "Anjali",
            activity: "National AI Hackathon",
            organization: "IEEE Kerala Section",
            date: "10-06-2026",
            certificate_id: "IEEE-HACK-88",
            category: "Technical Event",
            level: "Winner",
            confidence: 0.92
        },
        sports_national: {
            student_name: "Rahul",
            activity: "Inter-University Badminton",
            organization: "KTU Sports Council",
            date: "05-04-2026",
            certificate_id: "SPORTS-KTU-102",
            category: "Sports",
            level: "National Level",
            confidence: 0.96
        },
        paper_presentation: {
            student_name: "Jithu",
            activity: "International Tech Conference",
            organization: "CSI Student Chapter",
            date: "12-05-2026",
            certificate_id: "CSI-PAPER-331",
            category: "Technical Event",
            level: "Paper Presentation",
            confidence: 0.91
        },
        cultural_state: {
            student_name: "Sneha",
            activity: "KTU Arts Fest - Classical Dance",
            organization: "KTU Union",
            date: "28-02-2026",
            certificate_id: "KTU-ARTS-707",
            category: "Cultural",
            level: "State Level",
            confidence: 0.94
        }
    };

    // --- Initialize ---
    loadRules();
    loadHistory();

    // --- Theme Toggle ---
    themeToggleBtn.addEventListener("click", () => {
        document.body.classList.toggle("light-theme");
        showToast("Theme switched");
    });

    // --- Tab Switching (Form vs JSON) ---
    tabForm.addEventListener("click", () => {
        tabForm.classList.add("active");
        tabJson.classList.remove("active");
        formInput.style.display = "flex";
        jsonInputContainer.style.display = "none";
    });

    tabJson.addEventListener("click", () => {
        tabJson.classList.add("active");
        tabForm.classList.remove("active");
        formInput.style.display = "none";
        jsonInputContainer.style.display = "block";
        syncFormToJsonEditor();
    });

    function syncFormToJsonEditor() {
        const payload = getFormData();
        rawJsonEditor.value = JSON.stringify(payload, null, 4);
    }

    function getFormData() {
        return {
            student_name: document.getElementById("input-student-name").value.trim(),
            activity: document.getElementById("input-activity").value.trim(),
            organization: document.getElementById("input-organization").value.trim(),
            date: document.getElementById("input-date").value.trim(),
            certificate_id: document.getElementById("input-cert-id").value.trim(),
            category: selectCategory.value,
            level: selectLevel.value,
            confidence: parseFloat(document.getElementById("input-confidence").value) || 0.95
        };
    }

    function populateForm(data) {
        document.getElementById("input-student-name").value = data.student_name || "";
        document.getElementById("input-activity").value = data.activity || "";
        document.getElementById("input-organization").value = data.organization || "";
        document.getElementById("input-date").value = data.date || "";
        document.getElementById("input-cert-id").value = data.certificate_id || "";
        
        if (data.category) {
            selectCategory.value = data.category;
            updateLevelOptions(data.category);
        }
        if (data.level) {
            selectLevel.value = data.level;
        }
        document.getElementById("input-confidence").value = data.confidence !== undefined ? data.confidence : 0.95;
        syncFormToJsonEditor();
    }

    // --- Preset Buttons ---
    presetButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            presetButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            activePreset = btn.dataset.preset;
            if (PRESETS[activePreset]) {
                populateForm(PRESETS[activePreset]);
                showToast(`Loaded preset: ${btn.textContent.trim()}`);
            }
        });
    });

    // --- Category Change -> Update Levels ---
    selectCategory.addEventListener("change", () => {
        updateLevelOptions(selectCategory.value);
        syncFormToJsonEditor();
    });

    selectLevel.addEventListener("change", () => {
        syncFormToJsonEditor();
    });

    function updateLevelOptions(category) {
        selectLevel.innerHTML = "";
        const levels = currentRules[category] ? Object.keys(currentRules[category]) : [];
        if (levels.length === 0) {
            const opt = document.createElement("option");
            opt.value = "";
            opt.textContent = "-- No Levels Found --";
            selectLevel.appendChild(opt);
            return;
        }
        levels.forEach(lvl => {
            const opt = document.createElement("option");
            opt.value = lvl;
            opt.textContent = `${lvl} (${currentRules[category][lvl]} pts)`;
            selectLevel.appendChild(opt);
        });
    }

    // --- Form Submit (Run Person 3 Analysis) ---
    certForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const payload = getFormData();
        await executeAnalysis(payload);
    });

    btnSubmitJson.addEventListener("click", async () => {
        try {
            const payload = JSON.parse(rawJsonEditor.value);
            await executeAnalysis(payload);
        } catch (err) {
            showToast("Invalid JSON in editor: " + err.message, "error");
        }
    });

    async function executeAnalysis(payload) {
        try {
            resultStatusBadge.className = "status-badge status-ready";
            resultStatusBadge.textContent = "Processing...";

            const response = await fetch("/api/analyse", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const result = await response.json();
            displayResult(result);
            rawResponseJson.textContent = JSON.stringify(result, null, 4);
            loadHistory();
        } catch (err) {
            showToast("Failed to run analysis: " + err.message, "error");
        }
    }

    function displayResult(res) {
        const status = res.status;
        const pts = res.points !== undefined ? res.points : 0;
        const msg = res.message || "";

        if (status === "Valid") {
            resultStatusBadge.className = "status-badge status-valid";
            resultStatusBadge.textContent = "✓ Status: Valid";
            
            resultContent.innerHTML = `
                <div class="result-hero-box">
                    <div class="result-points-box">
                        <span class="result-points-label">Awarded KTU Points</span>
                        <span class="result-points-value">+${pts}</span>
                    </div>
                    <div class="result-msg-box">
                        <div class="result-msg-title">Analysis Successful</div>
                        <div class="result-msg-desc">${msg}</div>
                    </div>
                </div>
                <div class="result-details-grid">
                    <div class="detail-item">
                        <div class="detail-label">Student Name</div>
                        <div class="detail-val">${escapeHtml(res.student_name || "-")}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Activity</div>
                        <div class="detail-val">${escapeHtml(res.activity || "-")}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Category</div>
                        <div class="detail-val">${escapeHtml(res.category || "-")}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Level</div>
                        <div class="detail-val">${escapeHtml(res.level || "-")}</div>
                    </div>
                </div>
            `;
            showToast(`Certificate validated! +${pts} KTU Points allocated.`, "success");
        } else if (status === "Duplicate") {
            resultStatusBadge.className = "status-badge status-duplicate";
            resultStatusBadge.textContent = "⚠ Status: Duplicate";

            resultContent.innerHTML = `
                <div class="result-hero-box">
                    <div class="result-points-box">
                        <span class="result-points-label">Points Awarded</span>
                        <span class="result-points-value zero">0</span>
                    </div>
                    <div class="result-msg-box">
                        <div class="result-msg-title" style="color: var(--amber);">Duplicate Certificate Detected</div>
                        <div class="result-msg-desc">${msg}</div>
                    </div>
                </div>
                <div class="alert-box alert-info" style="margin-bottom: 0;">
                    <div class="alert-icon">🛡️</div>
                    <div class="alert-body">
                        <strong>Duplicate Prevention Guard:</strong> This certificate ID or matching activity signature was already registered. Zero additional points awarded.
                    </div>
                </div>
            `;
            showToast("Duplicate certificate detected. 0 points awarded.", "warning");
        } else {
            resultStatusBadge.className = "status-badge status-invalid";
            resultStatusBadge.textContent = "✕ Status: Invalid";

            resultContent.innerHTML = `
                <div class="result-hero-box">
                    <div class="result-points-box">
                        <span class="result-points-label">Points Awarded</span>
                        <span class="result-points-value error">0</span>
                    </div>
                    <div class="result-msg-box">
                        <div class="result-msg-title" style="color: var(--rose);">Validation Failed</div>
                        <div class="result-msg-desc">${msg}</div>
                    </div>
                </div>
                <div class="alert-box alert-info" style="border-color: rgba(239, 68, 68, 0.3); background: rgba(239, 68, 68, 0.08); color: #fca5a5;">
                    <div class="alert-icon">⚠️</div>
                    <div class="alert-body">
                        <strong>Missing / Invalid Parameters:</strong> Please verify that mandatory fields are provided and category/level match registered rules.
                    </div>
                </div>
            `;
            showToast("Validation failed: " + msg, "error");
        }
    }

    // --- Load KTU Rules ---
    async function loadRules() {
        try {
            const res = await fetch("/api/rules");
            const data = await res.json();
            currentRules = data.rules || {};
            renderRulesMatrix(currentRules);
            populateCategorySelect();
        } catch (e) {
            console.error("Error loading rules:", e);
        }
    }

    function populateCategorySelect() {
        const prevSelected = selectCategory.value;
        selectCategory.innerHTML = "";
        const categories = Object.keys(currentRules);
        categories.forEach(cat => {
            const opt = document.createElement("option");
            opt.value = cat;
            opt.textContent = cat;
            selectCategory.appendChild(opt);
        });
        if (categories.includes(prevSelected)) {
            selectCategory.value = prevSelected;
        } else if (categories.length > 0) {
            selectCategory.value = categories[0];
        }
        updateLevelOptions(selectCategory.value);
    }

    function renderRulesMatrix(rules) {
        rulesMatrixGrid.innerHTML = "";
        for (const [catName, levels] of Object.entries(rules)) {
            const card = document.createElement("div");
            card.className = "rule-category-card";

            let levelsHtml = "";
            for (const [lvl, pts] of Object.entries(levels)) {
                levelsHtml += `
                    <div class="rule-level-row">
                        <span class="rule-level-name">${escapeHtml(lvl)}</span>
                        <span class="rule-level-points">${pts} Pts</span>
                    </div>
                `;
            }

            card.innerHTML = `
                <div class="rule-category-header">
                    <span class="rule-category-title">${escapeHtml(catName)}</span>
                    <span class="p3-badge card-badge">${Object.keys(levels).length} Levels</span>
                </div>
                <div class="rule-levels-list">
                    ${levelsHtml}
                </div>
            `;
            rulesMatrixGrid.appendChild(card);
        }
    }

    // --- Edit Rules JSON Modal ---
    btnEditRulesJson.addEventListener("click", () => {
        modalRulesTextarea.value = JSON.stringify(currentRules, null, 4);
        rulesModal.style.display = "flex";
    });

    modalCloseBtn.addEventListener("click", () => rulesModal.style.display = "none");
    modalCancelBtn.addEventListener("click", () => rulesModal.style.display = "none");

    modalSaveBtn.addEventListener("click", async () => {
        try {
            const updated = JSON.parse(modalRulesTextarea.value);
            const res = await fetch("/api/rules", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(updated)
            });
            const data = await res.json();
            if (data.status === "success") {
                currentRules = data.rules;
                renderRulesMatrix(currentRules);
                populateCategorySelect();
                rulesModal.style.display = "none";
                showToast("KTU Point Rules updated successfully!");
            } else {
                showToast("Failed to save rules: " + (data.error || "Unknown error"), "error");
            }
        } catch (e) {
            showToast("Invalid JSON format in rules editor", "error");
        }
    });

    btnResetRules.addEventListener("click", async () => {
        if (confirm("Reset all point rules to standard default placeholders?")) {
            const res = await fetch("/api/rules/reset", { method: "POST" });
            const data = await res.json();
            currentRules = data.rules;
            renderRulesMatrix(currentRules);
            populateCategorySelect();
            showToast("Rules reset to default.");
        }
    });

    // --- Load History & Dashboard Stats ---
    async function loadHistory() {
        try {
            const res = await fetch("/api/history");
            const data = await res.json();
            const records = data.records || [];
            const summary = data.student_summary || {};
            const duplicateCount = data.duplicate_count || 0;

            // Stats Update (Primary student: Jithu or first student)
            const studentKeys = Object.keys(summary);
            const activeStudent = studentKeys.length > 0 ? studentKeys[0] : "Jithu";
            const studentData = summary[activeStudent] || { total_points: 0, valid_certs: 0 };

            statStudentName.textContent = activeStudent;
            statTotalPoints.innerHTML = `${studentData.total_points} <span class="stat-target">/ 100 Req</span>`;
            
            const pct = Math.min(100, Math.round((studentData.total_points / 100) * 100));
            statProgressFill.style.width = `${pct}%`;

            let totalValid = 0;
            let dupCount = 0;
            records.forEach(r => {
                if (r.result && r.result.status === "Valid") totalValid++;
                if (r.result && r.result.status === "Duplicate") dupCount++;
            });

            statValidCount.textContent = totalValid;
            statDuplicateCount.textContent = dupCount;
            tableLogCount.textContent = `${records.length} Submissions Recorded`;

            // Table Render
            if (records.length === 0) {
                historyTableBody.innerHTML = `
                    <tr>
                        <td colspan="7" class="table-empty">No activity submissions in this session. Run an analysis above to begin.</td>
                    </tr>
                `;
            } else {
                historyTableBody.innerHTML = records.map(entry => {
                    const inp = entry.input || {};
                    const out = entry.result || {};
                    const statusClass = out.status === "Valid" ? "status-valid" : out.status === "Duplicate" ? "status-duplicate" : "status-invalid";
                    const ptsDisplay = out.status === "Valid" ? `+${out.points}` : "0";

                    return `
                        <tr>
                            <td>${escapeHtml(inp.date || "Today")}</td>
                            <td><strong>${escapeHtml(out.student_name || inp.student_name || "-")}</strong></td>
                            <td><code>${escapeHtml(inp.certificate_id || "N/A")}</code></td>
                            <td>${escapeHtml(out.activity || inp.activity || "-")}</td>
                            <td><span class="detail-label">${escapeHtml(out.category || inp.category || "-")}</span> &bull; ${escapeHtml(out.level || inp.level || "-")}</td>
                            <td><span class="status-badge ${statusClass}">${out.status}</span></td>
                            <td><strong style="color: ${out.status === 'Valid' ? 'var(--emerald)' : 'var(--text-muted)'}">${ptsDisplay}</strong></td>
                        </tr>
                    `;
                }).join("");
            }
        } catch (e) {
            console.error("Error loading history:", e);
        }
    }

    // --- Clear DB / Reset Submissions ---
    btnClearDb.addEventListener("click", async () => {
        if (confirm("Clear duplicate signature cache and submission history?")) {
            await fetch("/api/reset", { method: "POST" });
            loadHistory();
            showToast("Duplicate database & history reset.");
        }
    });

    // --- Copy Code Buttons ---
    document.querySelectorAll(".copy-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const targetId = btn.dataset.target;
            const codeEl = document.getElementById(targetId);
            if (codeEl) {
                navigator.clipboard.writeText(codeEl.textContent.trim());
                btn.textContent = "Copied!";
                setTimeout(() => btn.textContent = "Copy", 2000);
            }
        });
    });

    // --- Raw JSON Collapsible ---
    rawJsonToggle.addEventListener("click", () => {
        const isHidden = rawResponseJson.style.display === "none";
        rawResponseJson.style.display = isHidden ? "block" : "none";
        document.querySelector(".toggle-icon").textContent = isHidden ? "▼" : "▶";
    });

    // --- Helper Utilities ---
    function showToast(message, type = "info") {
        const container = document.getElementById("toast-container");
        const toast = document.createElement("div");
        toast.className = "toast";
        if (type === "error") toast.style.borderColor = "var(--rose)";
        if (type === "warning") toast.style.borderColor = "var(--amber)";
        if (type === "success") toast.style.borderColor = "var(--emerald)";
        toast.textContent = message;
        container.appendChild(toast);
        setTimeout(() => {
            toast.remove();
        }, 3500);
    }

    function escapeHtml(str) {
        if (!str) return "";
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});
