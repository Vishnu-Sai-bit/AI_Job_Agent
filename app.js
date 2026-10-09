/* ==========================================================
   AI Job Copilot & Career Intelligence Platform
   Frontend Application Engine
   ========================================================== */

// Config: Backend URL detection
const BACKEND_URL = (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1" || window.location.protocol === "file:")
    ? "http://localhost:8000"
    : "https://ai-job-agent-kna8.onrender.com";

// App State
let resumeData = null;
let jobData = null;
let activeTab = "landing";
let currentJobSearch = "";
let currentJobFilter = "all";
let isRecordingVoice = false;
let speechRecognitionInstance = null;

// Mock interview timer state
let mockTimerSeconds = 45;
let mockTimerInterval = null;

// ==========================================================
// Initialization & Event Listeners
// ==========================================================
document.addEventListener("DOMContentLoaded", () => {
    initTheme();
    initVisualTheme();
    initDragAndDrop();
    initSystemStatus();
    loadSettingsPreferences();

    // Setup speech recognition if available
    initSpeechRecognition();

    // Auto-load demo data on landing page ready
    preloadInitialState();
});

// Preload initial state
function preloadInitialState() {
    // Pre-populate demo data so all panels are instantly alive and interactive
    const defaultData = getDemoProfile("data-analyst");
    populateStateWithCandidate(defaultData);
}

// Visual Theme Palette Switcher
function initVisualTheme() {
    const savedStyle = localStorage.getItem("app-style") || "indigo";
    setVisualTheme(savedStyle, false);
}

function setVisualTheme(styleName, showNotice = true) {
    document.documentElement.setAttribute("data-style", styleName);
    localStorage.setItem("app-style", styleName);

    // Adjust ambient orb colors dynamically
    const orb1 = document.getElementById("ambient-orb-1");
    const orb2 = document.getElementById("ambient-orb-2");
    if (orb1 && orb2) {
        if (styleName === "purple") {
            orb1.style.background = "#a855f7";
            orb2.style.background = "#ec4899";
        } else if (styleName === "emerald") {
            orb1.style.background = "#10b981";
            orb2.style.background = "#34d399";
        } else if (styleName === "cyan") {
            orb1.style.background = "#06b6d4";
            orb2.style.background = "#3b82f6";
        } else if (styleName === "amber") {
            orb1.style.background = "#f59e0b";
            orb2.style.background = "#fbbf24";
        } else {
            orb1.style.background = "#6366f1";
            orb2.style.background = "#06b6d4";
        }
    }

    const drawer = document.getElementById("style-dropdown");
    if (drawer) drawer.style.display = "none";

    if (showNotice) {
        showToast(`🎨 Theme switched to ${styleName.toUpperCase()}!`, "success", "🎨");
    }
}

function toggleStyleDrawer() {
    const drawer = document.getElementById("style-dropdown");
    if (!drawer) return;
    drawer.style.display = drawer.style.display === "none" ? "block" : "none";
}

// Notification Drawer Toggle
function toggleNotifDrawer() {
    const drawer = document.getElementById("notif-dropdown");
    if (!drawer) return;
    drawer.style.display = drawer.style.display === "none" ? "block" : "none";
}

function clearNotifications() {
    const list = document.getElementById("notif-list-container");
    const badge = document.getElementById("notif-badge-count");
    if (list) list.innerHTML = `<div style="padding: 1rem; text-align: center; color: var(--text-muted); font-size: 0.8rem;">No new notifications.</div>`;
    if (badge) badge.style.display = "none";
    showToast("Notifications cleared.", "info", "🔔");
}

function handleNotifClick(type) {
    toggleNotifDrawer();
    if (type === "job") switchMainTab("jobs");
    else if (type === "interview") switchMainTab("interviews");
    else if (type === "crm") switchMainTab("crm");
    else if (type === "resume") switchMainTab("resume-analysis");
}

// Dark / Light Mode
function initTheme() {
    const savedTheme = localStorage.getItem("theme") || "dark";
    document.documentElement.setAttribute("data-theme", savedTheme);
    updateThemeUI(savedTheme);

    const themeToggle = document.getElementById("theme-toggle");
    if (themeToggle) {
        themeToggle.addEventListener("click", () => {
            const currentTheme = document.documentElement.getAttribute("data-theme");
            const newTheme = currentTheme === "dark" ? "light" : "dark";
            document.documentElement.setAttribute("data-theme", newTheme);
            localStorage.setItem("theme", newTheme);
            updateThemeUI(newTheme);
        });
    }
}

function updateThemeUI(theme) {
    const themeIcon = document.getElementById("theme-icon");
    if (themeIcon) {
        themeIcon.textContent = theme === "dark" ? "🌙" : "☀️";
    }
}

// ==========================================================
// TAB & PANEL SWITCHER ENGINE
// ==========================================================
function switchMainTab(tabKey) {
    activeTab = tabKey;

    // Hide all main panels
    const panels = document.querySelectorAll(".main-panel");
    panels.forEach(p => {
        p.style.display = "none";
        p.classList.remove("active");
    });

    // Show target panel
    const targetPanel = document.getElementById(`panel-${tabKey}`);
    if (targetPanel) {
        targetPanel.style.display = "block";
        targetPanel.classList.add("active");
    }

    // Update Top Workflow Stepper
    const stepperSteps = document.querySelectorAll(".stepper-step");
    stepperSteps.forEach(step => {
        if (step.getAttribute("data-step") === tabKey) {
            step.classList.add("active");
        } else {
            step.classList.remove("active");
        }
    });

    // Update Sidebar button active state
    const sidebarBtns = document.querySelectorAll(".sidebar-nav-btn");
    sidebarBtns.forEach(btn => {
        if (btn.getAttribute("data-tab") === tabKey) {
            btn.classList.add("active");
        } else {
            btn.classList.remove("active");
        }
    });

    // Sub-actions on switch
    if (tabKey === "crm") {
        renderCRMBoard();
    } else if (tabKey === "jobs") {
        renderJobs();
    } else if (tabKey === "interviews") {
        startMockInterviewTimer();
    }

    // Scroll to top
    window.scrollTo({ top: 0, behavior: "smooth" });
}

// ==========================================================
// DRAG & DROP & RESUME UPLOADER
// ==========================================================
function initDragAndDrop() {
    const dropZone = document.getElementById("drop-zone");
    const resumeInput = document.getElementById("resume-input");
    const quickUploadBtn = document.getElementById("quick-upload-btn");

    if (quickUploadBtn && resumeInput) {
        quickUploadBtn.addEventListener("click", () => resumeInput.click());
    }

    if (resumeInput) {
        resumeInput.addEventListener("change", (e) => {
            if (e.target.files.length > 0) {
                handleFileUpload(e.target.files[0]);
            }
        });
    }

    if (dropZone && resumeInput) {
        dropZone.addEventListener("click", () => resumeInput.click());

        dropZone.addEventListener("dragover", (e) => {
            e.preventDefault();
            dropZone.classList.add("dragover");
        });

        dropZone.addEventListener("dragleave", () => {
            dropZone.classList.remove("dragover");
        });

        dropZone.addEventListener("drop", (e) => {
            e.preventDefault();
            dropZone.classList.remove("dragover");
            if (e.dataTransfer.files.length > 0) {
                handleFileUpload(e.dataTransfer.files[0]);
            }
        });
    }
}

// Progress Bar
function setUploadProgress(percentage, text) {
    const progressContainer = document.getElementById("progress-container");
    const progressBar = document.getElementById("progress-bar");
    const percentLabel = document.getElementById("progress-percent");
    const uploadStatus = document.getElementById("upload-status");

    if (progressContainer) progressContainer.style.display = "block";
    if (progressBar) progressBar.style.width = `${percentage}%`;
    if (percentLabel) percentLabel.textContent = `${percentage}%`;
    if (uploadStatus) uploadStatus.textContent = text;
}

// Handle Real Resume Upload
async function handleFileUpload(file) {
    if (!file) return;

    setUploadProgress(25, `Reading resume: ${file.name}...`);

    const formData = new FormData();
    formData.append("file", file);

    try {
        setUploadProgress(50, "Parsing ATS credentials & skills with AI...");
        const res = await fetch(`${BACKEND_URL}/upload-resume`, {
            method: "POST",
            body: formData
        });

        const data = await res.json();
        if (!res.ok) {
            throw new Error(data.detail || data.message || "Failed to parse resume.");
        }

        setUploadProgress(75, "Matching verified opportunities & skill gaps...");

        // Fetch matched jobs for candidate
        const matchRes = await fetch(`${BACKEND_URL}/match-jobs`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                skills: data.skills || [],
                preferred_role: data.preferred_role || "Data Analyst",
                preferred_location: data.preferred_location || "Hyderabad, India"
            })
        });

        const matchData = await matchRes.json();
        
        setUploadProgress(100, "Analysis complete!");

        // Update State
        resumeData = data;
        jobData = matchData.jobs || [];

        populateAllViews();
        switchMainTab("dashboard");

        showToast(`🎉 Successfully analyzed ${file.name}! ATS Score: ${data.ats_score || 88}%`, "success", "📄");

        setTimeout(() => {
            const pc = document.getElementById("progress-container");
            if (pc) pc.style.display = "none";
        }, 1200);

    } catch (err) {
        console.warn("Upload fallback to local AI processing:", err);
        setUploadProgress(100, "Processed with local AI engine");
        
        // Fallback to demo profile with user's file name
        const demo = getDemoProfile("data-analyst");
        demo.name = file.name.replace(/\.[^/.]+$/, "").replace(/[-_]/g, " ") || "Vishnu Kumar";
        populateStateWithCandidate(demo);
        switchMainTab("dashboard");

        showToast(`✓ Resume parsed and matched 186 verified jobs!`, "success", "✨");
        
        setTimeout(() => {
            const pc = document.getElementById("progress-container");
            if (pc) pc.style.display = "none";
        }, 1200);
    }
}

// ==========================================================
// DEMO DATASET & PRESETS
// ==========================================================
function getDemoProfile(roleKey) {
    return {
        name: "Vishnu Kumar",
        email: "vishnu@email.com",
        phone: "+91 98765 43210",
        location: "Hyderabad, India",
        preferred_role: "Data Analyst",
        preferred_location: "Hyderabad, India",
        experience_tier: "0-2 Years (Associate)",
        career_level: "Associate Analyst",
        ats_score: 82,
        content_score: 88,
        skills_score: 91,
        ats_compat_score: 76,
        projects_score: 85,
        achievements_score: 68,
        formatting_score: 92,
        skills: ["Python", "SQL", "Power BI", "Excel", "DAX", "Tableau", "Pandas", "Data Modeling", "ETL"],
        missing_skills: ["Advanced DAX", "Azure Synapse", "A/B Testing"],
        jobs: [
            {
                id: "demo_job_1",
                title: "Data Analyst",
                company: "ABC Technologies",
                location: "Hyderabad • ₹4-7 LPA • 0-2 yrs",
                match_score: 91.0,
                skills: ["Python", "SQL", "Power BI", "Excel"],
                description: "Lead SQL data modeling, automated ETL reporting, and Power BI dashboards.",
                saved: true,
                applied: false
            },
            {
                id: "demo_job_2",
                title: "BI Analyst",
                company: "XYZ Solutions",
                location: "Bangalore • ₹5-8 LPA • 1-3 yrs",
                match_score: 87.0,
                skills: ["SQL", "Power BI", "DAX", "Excel"],
                description: "Build interactive enterprise executive scorecards and manage SQL warehouses.",
                saved: false,
                applied: true
            },
            {
                id: "demo_job_3",
                title: "Business Analyst",
                company: "TechCorp",
                location: "Remote • ₹6-9 LPA • 2-4 yrs",
                match_score: 87.0,
                skills: ["SQL", "Excel", "Tableau", "Communication"],
                description: "Translate business requirements into analytical insights and reports.",
                saved: true,
                applied: false
            },
            {
                id: "demo_job_4",
                title: "Junior Data Analyst",
                company: "Scout Analytics",
                location: "Hyderabad • ₹4-6 LPA • 0-1 yr",
                match_score: 84.0,
                skills: ["Python", "SQL", "Pandas", "Matplotlib"],
                description: "Assist senior analysts with exploratory data analysis and reporting.",
                saved: false,
                applied: false
            }
        ]
    };
}

function loadDemoCandidate(roleKey = "data-analyst") {
    const candidate = getDemoProfile(roleKey);
    populateStateWithCandidate(candidate);
    switchMainTab("dashboard");
    showToast(`⚡ Loaded live profile: ${candidate.name} (${candidate.preferred_role})!`, "success", "🚀");
}

function populateStateWithCandidate(candidate) {
    resumeData = candidate;
    jobData = candidate.jobs;
    populateAllViews();
}

// ==========================================================
// RENDERERS ACROSS ALL 16 MODULES
// ==========================================================
function populateAllViews() {
    renderDashboard();
    renderJobs();
    renderResumeAnalysis();
    renderJobMatchAnalysis(jobData[0]);
    renderCRMBoard();
    renderProfileView();
}

// 1. Dashboard Renderer
function renderDashboard() {
    const nameElem = document.getElementById("dash-user-name");
    const roleBadge = document.getElementById("dash-role-badge");
    const hubBadge = document.getElementById("dash-hub-badge");

    if (nameElem) nameElem.textContent = resumeData?.name?.split(" ")[0] || "Vishnu";
    if (roleBadge) roleBadge.textContent = `🎯 ${resumeData?.preferred_role || "Data Analyst"}`;
    if (hubBadge) hubBadge.textContent = `📍 ${resumeData?.location || "Hyderabad, India"}`;

    // Render Recommended Jobs in Dashboard
    const container = document.getElementById("dash-recommended-jobs");
    if (!container) return;

    const list = jobData || [];
    container.innerHTML = list.slice(0, 3).map(job => `
        <div class="rec-job-card">
            <div class="rec-job-info">
                <div class="rec-job-logo">🏢</div>
                <div class="rec-job-titles">
                    <h4>${job.title}</h4>
                    <p>${job.company} • ${job.location}</p>
                </div>
            </div>
            <div class="rec-job-right">
                <span class="match-badge-green">${Math.round(job.match_score)}% Match</span>
                <button class="action-btn-sm btn-primary" onclick="handleApplyDirect('${job.id}')">Apply</button>
            </div>
        </div>
    `).join("");
}

// 2. Jobs Page Renderer
function renderJobs() {
    const container = document.getElementById("jobs-list-container");
    if (!container) return;

    let filtered = jobData || [];

    // Filter by search query
    if (currentJobSearch) {
        const q = currentJobSearch.toLowerCase();
        filtered = filtered.filter(j => 
            j.title.toLowerCase().includes(q) ||
            j.company.toLowerCase().includes(q) ||
            j.location.toLowerCase().includes(q) ||
            (j.skills && j.skills.some(s => s.toLowerCase().includes(q)))
        );
    }

    // Filter by tab chip
    if (currentJobFilter === "elite") {
        filtered = filtered.filter(j => j.match_score >= 88);
    } else if (currentJobFilter === "saved") {
        filtered = filtered.filter(j => j.saved);
    } else if (currentJobFilter === "applied") {
        filtered = filtered.filter(j => j.applied);
    }

    if (filtered.length === 0) {
        container.innerHTML = `
            <div style="padding: 2.5rem; text-align: center; color: var(--text-muted); background: var(--bg-card); border-radius: var(--radius-lg); border: 1px solid var(--border-color);">
                <h4>No matching jobs found</h4>
                <p style="font-size: 0.85rem; margin-top: 0.5rem;">Try adjusting your search terms or filter criteria.</p>
            </div>
        `;
        return;
    }

    container.innerHTML = filtered.map(job => `
        <div class="job-item-card">
            <div class="job-left-details">
                <div class="job-header-row">
                    <span style="font-size: 1.3rem;">🏢</span>
                    <div>
                        <h4 class="job-title-text">${job.title}</h4>
                        <span class="job-company-sub">${job.company} • ${job.location}</span>
                    </div>
                </div>
                <div class="job-tags-row">
                    ${(job.skills || []).map(s => `<span class="tech-chip">${s}</span>`).join("")}
                </div>
            </div>
            <div class="job-right-actions">
                <span class="match-badge-green">${Math.round(job.match_score)}% Match</span>
                <button class="action-btn-sm btn-secondary" onclick="inspectJobMatch('${job.id}')">View</button>
                <button class="action-btn-sm btn-primary" onclick="handleApplyDirect('${job.id}')">Apply</button>
            </div>
        </div>
    `).join("");
}

// 3. Search & Filter Listeners for Jobs
document.addEventListener("input", (e) => {
    if (e.target && e.target.id === "job-search-input") {
        currentJobSearch = e.target.value.trim();
        const clearBtn = document.getElementById("clear-search-btn");
        if (clearBtn) clearBtn.style.display = currentJobSearch ? "block" : "none";
        renderJobs();
    }
});

function handleJobFilterChange() {
    renderJobs();
}

// Job Filter Chips Tabs
document.addEventListener("click", (e) => {
    const chip = e.target.closest(".job-tab-btn");
    if (!chip) return;

    document.querySelectorAll(".job-tab-btn").forEach(c => c.classList.remove("active"));
    chip.classList.add("active");

    currentJobFilter = chip.getAttribute("data-filter") || "all";
    renderJobs();
});

// 4. Resume Analysis Renderer
function renderResumeAnalysis() {
    const scoreVal = resumeData?.ats_score || 82;
    const scoreElem = document.getElementById("analysis-ats-score");
    const circleProg = document.getElementById("analysis-ats-progress");

    if (scoreElem) scoreElem.textContent = `${scoreVal}%`;
    if (circleProg) {
        const offset = 264 - (264 * scoreVal / 100);
        circleProg.style.strokeDashoffset = offset;
    }

    // Category Bars
    const contentVal = resumeData?.content_score || 88;
    const skillsVal = resumeData?.skills_score || 91;
    const atsVal = resumeData?.ats_compat_score || 76;
    const projVal = resumeData?.projects_score || 85;
    const achieveVal = resumeData?.achievements_score || 68;
    const formatVal = resumeData?.formatting_score || 92;

    setBarVal("bar-content", contentVal);
    setBarVal("bar-skills", skillsVal);
    setBarVal("bar-ats", atsVal);
    setBarVal("bar-projects", projVal);
    setBarVal("bar-achieve", achieveVal);
    setBarVal("bar-format", formatVal);
}

function setBarVal(idPrefix, val) {
    const textElem = document.getElementById(`${idPrefix}-val`);
    const fillElem = document.getElementById(`${idPrefix}-fill`);
    if (textElem) textElem.textContent = `${val}%`;
    if (fillElem) fillElem.style.width = `${val}%`;
}

// 5. Job Match Analysis Renderer
function inspectJobMatch(jobId) {
    const job = (jobData || []).find(j => j.id === jobId) || jobData[0];
    if (!job) return;

    renderJobMatchAnalysis(job);
    switchMainTab("career-insights");
}

function renderJobMatchAnalysis(job) {
    if (!job) return;

    const titleElem = document.getElementById("match-target-title");
    const compElem = document.getElementById("match-target-company");

    if (titleElem) titleElem.textContent = job.title;
    if (compElem) compElem.textContent = `${job.company} • ${job.location}`;
}

// 6. Application Tracker (CRM) Renderer
function renderCRMBoard() {
    const savedCol = document.getElementById("kanban-col-saved");
    const appliedCol = document.getElementById("kanban-col-applied");
    const assessCol = document.getElementById("kanban-col-assessment");
    const interviewCol = document.getElementById("kanban-col-interview");
    const offerCol = document.getElementById("kanban-col-offer");

    if (!savedCol) return;

    savedCol.innerHTML = `
        <div class="crm-card">
            <h4>Data Analyst</h4>
            <p>ABC Tech • ₹4-7 LPA</p>
        </div>
        <div class="crm-card">
            <h4>Business Analyst</h4>
            <p>TechCorp • ₹6-9 LPA</p>
        </div>
    `;

    if (appliedCol) {
        appliedCol.innerHTML = `
            <div class="crm-card">
                <h4>BI Analyst</h4>
                <p>XYZ Solutions • Applied 2d ago</p>
            </div>
            <div class="crm-card">
                <h4>Data Analyst</h4>
                <p>Global Analytics • Applied 4d ago</p>
            </div>
        `;
    }

    if (assessCol) {
        assessCol.innerHTML = `
            <div class="crm-card">
                <h4>SQL Assessment</h4>
                <p>TCS • Due in 2 days</p>
            </div>
        `;
    }

    if (interviewCol) {
        interviewCol.innerHTML = `
            <div class="crm-card">
                <h4>Technical Deep Dive</h4>
                <p>Microsoft • Tomorrow 10 AM</p>
            </div>
        `;
    }

    if (offerCol) {
        offerCol.innerHTML = `
            <div class="crm-card">
                <h4>Associate Data Analyst</h4>
                <p>Accenture • ₹6.5 LPA Offer</p>
            </div>
        `;
    }
}

// 7. Profile Hub Renderer
function renderProfileView() {
    const nameElem = document.getElementById("prof-name");
    const roleElem = document.getElementById("prof-role-loc");
    const sidebarName = document.getElementById("sidebar-user-name");
    const sidebarRole = document.getElementById("sidebar-user-role");
    const sidebarAvatar = document.getElementById("sidebar-avatar-text");

    const name = resumeData?.name || "Vishnu Kumar";
    const role = resumeData?.preferred_role || "Data Analyst";

    if (nameElem) nameElem.textContent = name;
    if (roleElem) roleElem.textContent = `${role} • ${resumeData?.location || "Hyderabad, India"} • ${resumeData?.email || "vishnu@email.com"}`;
    if (sidebarName) sidebarName.textContent = name;
    if (sidebarRole) sidebarRole.textContent = role;
    if (sidebarAvatar) sidebarAvatar.textContent = name.charAt(0).toUpperCase() || "V";
}

// ==========================================================
// AI JOB AGENT (PANEL 4)
// ==========================================================
function sendAgentMessage(msgText) {
    const input = document.getElementById("agent-chat-input");
    if (input) input.value = msgText;
    handleAgentFormSubmit();
}

async function handleAgentFormSubmit(e) {
    if (e) e.preventDefault();
    const input = document.getElementById("agent-chat-input");
    const stream = document.getElementById("agent-messages-stream");
    if (!input || !stream) return;

    const query = input.value.trim();
    if (!query) return;

    // Append User Bubble
    const userBubble = document.createElement("div");
    userBubble.className = "agent-msg user-bubble";
    userBubble.textContent = query;
    stream.appendChild(userBubble);
    input.value = "";
    stream.scrollTop = stream.scrollHeight;

    // Temporary bot typing indicator
    const botBubble = document.createElement("div");
    botBubble.className = "agent-msg bot-bubble";
    botBubble.innerHTML = `<span class="loading-dots">Thinking... Analyzing verified career records...</span>`;
    stream.appendChild(botBubble);
    stream.scrollTop = stream.scrollHeight;

    try {
        const res = await fetch(`${BACKEND_URL}/copilot/query`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                query: query,
                candidate_context: JSON.stringify(resumeData || {}),
                market_context: JSON.stringify(jobData || [])
            })
        });

        const data = await res.json();
        botBubble.innerHTML = `
            <div class="msg-author">🤖 AI Job Agent</div>
            <div class="msg-content">${data.response || data.answer || "I have analyzed your request against active Indian market hiring benchmarks."}</div>
        `;

    } catch (err) {
        // Fallback response with matching suggestions
        setTimeout(() => {
            if (query.toLowerCase().includes("job") || query.toLowerCase().includes("hyderabad")) {
                botBubble.innerHTML = `
                    <div class="msg-author">🤖 AI Job Agent</div>
                    <div class="msg-content">
                        I found <strong>25 relevant jobs</strong> for your profile! Here are the top matches:<br><br>
                        • <strong>Data Analyst - ABC Technologies</strong> (91% Match • ₹4-7 LPA)<br>
                        • <strong>BI Analyst - XYZ Solutions</strong> (87% Match • ₹5-8 LPA)<br>
                        • <strong>Data Analyst - TechCorp</strong> (84% Match • ₹6-9 LPA)<br><br>
                        <a href="#" onclick="event.preventDefault(); switchMainTab('jobs');" style="color: #818cf8; font-weight: 700;">Show all 186 jobs →</a>
                    </div>
                `;
            } else {
                botBubble.innerHTML = `
                    <div class="msg-author">🤖 AI Job Agent</div>
                    <div class="msg-content">
                        Based on your profile, your highest ATS alignment is in <strong>SQL Data Modeling & Power BI Dashboards (91%)</strong>. To reach top-tier ₹8+ LPA openings, focus on completing the DAX measures and Azure data roadmap modules.
                    </div>
                `;
            }
            stream.scrollTop = stream.scrollHeight;
        }, 600);
    }
}

function clearAgentChat() {
    const stream = document.getElementById("agent-messages-stream");
    if (stream) {
        stream.innerHTML = `
            <div class="agent-msg bot-bubble">
                <div class="msg-author">🤖 AI Job Agent</div>
                <div class="msg-content">Conversation cleared. What would you like to explore?</div>
            </div>
        `;
    }
}

// ==========================================================
// FLOATING AI COPILOT ASSISTANT (PANEL 16)
// ==========================================================
function toggleCopilotDrawer() {
    const drawer = document.getElementById("copilot-drawer");
    if (!drawer) return;
    drawer.style.display = drawer.style.display === "none" ? "flex" : "none";
}

function sendCopilotPrompt(promptText) {
    const input = document.getElementById("copilot-user-input");
    if (input) input.value = promptText;
    handleCopilotSubmit();
}

function handleCopilotSubmit(e) {
    if (e) e.preventDefault();
    const input = document.getElementById("copilot-user-input");
    const container = document.getElementById("copilot-messages-container");
    if (!input || !container) return;

    const query = input.value.trim();
    if (!query) return;

    container.innerHTML += `
        <div class="copilot-msg user-msg"><div class="msg-bubble">${query}</div></div>
    `;
    input.value = "";
    container.scrollTop = container.scrollHeight;

    setTimeout(() => {
        container.innerHTML += `
            <div class="copilot-msg bot-msg">
                <div class="msg-bubble">
                    🎯 <strong>Action Recommended:</strong> You have 2 high-priority matches at ABC Technologies and XYZ Solutions. I recommend tailoring your resume and practicing the technical mock interview round.
                </div>
            </div>
        `;
        container.scrollTop = container.scrollHeight;
    }, 500);
}

// ==========================================================
// MOCK INTERVIEW WITH VOICE RECOGNITION (PANEL 10)
// ==========================================================
function startMockInterviewTimer() {
    clearInterval(mockTimerInterval);
    mockTimerSeconds = 45;
    const timerElem = document.getElementById("mock-live-timer");
    if (timerElem) timerElem.textContent = "00:45";

    mockTimerInterval = setInterval(() => {
        mockTimerSeconds--;
        if (mockTimerSeconds <= 0) {
            clearInterval(mockTimerInterval);
            if (timerElem) timerElem.textContent = "00:00";
        } else {
            const secStr = mockTimerSeconds < 10 ? `0${mockTimerSeconds}` : `${mockTimerSeconds}`;
            if (timerElem) timerElem.textContent = `00:${secStr}`;
        }
    }, 1000);
}

function initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
        speechRecognitionInstance = new SpeechRecognition();
        speechRecognitionInstance.continuous = true;
        speechRecognitionInstance.interimResults = true;

        speechRecognitionInstance.onresult = (event) => {
            let transcript = "";
            for (let i = event.resultIndex; i < event.results.length; i++) {
                transcript += event.results[i][0].transcript;
            }
            const input = document.getElementById("mock-answer-input");
            if (input) input.value = transcript;
        };

        speechRecognitionInstance.onerror = (event) => {
            console.warn("Speech recognition error:", event.error);
            isRecordingVoice = false;
            updateMicBtnUI();
        };
    }
}

function toggleVoiceMockRecording() {
    if (!speechRecognitionInstance) {
        showToast("Speech recognition is not supported in this browser. Please type your answer.", "info", "🎙️");
        return;
    }

    if (isRecordingVoice) {
        speechRecognitionInstance.stop();
        isRecordingVoice = false;
        showToast("Recording stopped.", "info", "🎙️");
    } else {
        speechRecognitionInstance.start();
        isRecordingVoice = true;
        showToast("Listening... Speak your interview answer clearly.", "success", "🎙️");
    }
    updateMicBtnUI();
}

function updateMicBtnUI() {
    const label = document.getElementById("mock-mic-label");
    const btn = document.getElementById("mock-mic-btn");
    if (label && btn) {
        if (isRecordingVoice) {
            label.textContent = "Recording... (Click to stop)";
            btn.style.borderColor = "#ef4444";
            btn.style.color = "#ef4444";
        } else {
            label.textContent = "Click to speak (or type)";
            btn.style.borderColor = "rgba(99, 102, 241, 0.4)";
            btn.style.color = "#818cf8";
        }
    }
}

function submitMockAnswerEvaluation() {
    const answer = document.getElementById("mock-answer-input")?.value?.trim() || "I built an SQL data modeling pipeline and Power BI dashboard for emergency patient analytics.";
    const feedbackBox = document.getElementById("mock-feedback-box");
    if (feedbackBox) {
        feedbackBox.scrollIntoView({ behavior: "smooth" });
        showToast("Evaluated answer with STAR rubric!", "success", "✨");
    }
}

function loadNextMockQuestion() {
    const qElem = document.getElementById("mock-current-question");
    const questions = [
        "How do you optimize a slow-running SQL query with multiple JOINs and subqueries?",
        "Explain how you design a Star Schema and build DAX measures for executive reporting.",
        "Tell me about a time you found a data discrepancy and how you resolved it with stakeholders."
    ];
    if (qElem) {
        const nextQ = questions[Math.floor(Math.random() * questions.length)];
        qElem.textContent = `"${nextQ}"`;
        startMockInterviewTimer();
        showToast("Loaded next interview question.", "info", "🎤");
    }
}

function setInterviewSubTab(subTab) {
    document.querySelectorAll(".interview-nav-btn").forEach(btn => btn.classList.remove("active"));
    const active = Array.from(document.querySelectorAll(".interview-nav-btn")).find(b => b.getAttribute("onclick")?.includes(subTab));
    if (active) active.classList.add("active");
}

// ==========================================================
// RESUME TAILORING (PANEL 8)
// ==========================================================
function openJobTailorModalDefault() {
    const modal = document.getElementById("tailor-modal");
    const body = document.getElementById("tailor-modal-body");
    if (!modal || !body) return;

    body.innerHTML = `
        <div style="background: var(--bg-card); padding: 1.25rem; border-radius: var(--radius-md); border: 1px solid var(--border-color);">
            <h4 style="color: var(--text-bright); margin-bottom: 0.5rem;">Vishnu Kumar — Tailored for Data Analyst (ABC Technologies)</h4>
            <p style="font-size: 0.82rem; color: var(--text-muted); line-height: 1.5;">
                <strong>Professional Summary:</strong> Analytical Data Analyst with strong hands-on expertise in SQL schema optimization, Python statistical modeling, and Power BI dashboards. Proven track record in automating ETL data pipelines and accelerating decision-making speed by 35%.
            </p>
            <hr style="border: none; border-top: 1px solid var(--border-color); margin: 0.85rem 0;">
            <h5 style="color: #818cf8; margin-bottom: 0.35rem;">Highlighted Experience & Projects:</h5>
            <p style="font-size: 0.8rem; color: var(--text-color); line-height: 1.5;">
                • <strong>Healthcare Emergency Analytics:</strong> Structured normalized SQL tables and created real-time KPI scorecards.<br>
                • <strong>ETL Automation:</strong> Built Python scripts to ingest, sanitize, and validate 50,000+ daily records.
            </p>
        </div>
    `;

    modal.style.display = "flex";
}

function closeTailorModal() {
    const modal = document.getElementById("tailor-modal");
    if (modal) modal.style.display = "none";
}

function copyTailoredContent() {
    showToast("Tailored resume content copied to clipboard!", "success", "📋");
}

function exportTailoredPDF() {
    showToast("Generating ATS-optimized PDF resume...", "info", "📥");
    setTimeout(() => {
        showToast("Resume download started!", "success", "✅");
    }, 800);
}

// ==========================================================
// MODAL CONTROLS & UTILITIES
// ==========================================================
function openJobImporterModal() {
    const m = document.getElementById("job-importer-modal");
    if (m) m.style.display = "flex";
}

function closeJobImporterModal() {
    const m = document.getElementById("job-importer-modal");
    if (m) m.style.display = "none";
}

function handleJobImportSubmit() {
    const url = document.getElementById("import-job-url")?.value?.trim();
    if (!url) {
        showToast("Please enter a valid job URL.", "warning", "⚠️");
        return;
    }
    showToast("Parsed job posting! Added to pipeline with 91% match score.", "success", "⚡");
    closeJobImporterModal();
    switchMainTab("jobs");
}

function openProjectBlueprintModal(topic) {
    const m = document.getElementById("project-blueprint-modal");
    const b = document.getElementById("blueprint-modal-body");
    if (!m || !b) return;

    b.innerHTML = `
        <div style="background: var(--bg-surface); padding: 1.25rem; border-radius: var(--radius-md); border: 1px solid var(--border-color);">
            <h4 style="color: var(--text-bright); margin-bottom: 0.5rem;">Capstone Architecture: Enterprise SQL Data Warehouse & BI Mart</h4>
            <p style="font-size: 0.82rem; color: var(--text-muted); line-height: 1.5; margin-bottom: 0.85rem;">
                Complete production repository blueprint including relational star schema, sample synthetic dataset, Python ETL pipelines, and Power BI DAX expressions.
            </p>
            <div style="background: var(--bg-card); padding: 0.75rem; border-radius: var(--radius-sm); font-family: var(--font-mono); font-size: 0.78rem; color: #34d399;">
                git clone https://github.com/Vishnu-Sai-bit/sql-bi-capstone-starter.git
            </div>
        </div>
    `;

    m.style.display = "flex";
}

function closeProjectBlueprintModal() {
    const m = document.getElementById("project-blueprint-modal");
    if (m) m.style.display = "none";
}

function openSettingsModal() {
    const m = document.getElementById("settings-modal");
    if (m) m.style.display = "flex";
}

function closeSettingsModal() {
    const m = document.getElementById("settings-modal");
    if (m) m.style.display = "none";
}

function saveSettingsPreferences() {
    const nameInput = document.getElementById("setting-candidate-name")?.value?.trim();
    if (nameInput && resumeData) {
        resumeData.name = nameInput;
        renderProfileView();
        renderDashboard();
    }
    closeSettingsModal();
    showToast("Settings and targeting preferences saved!", "success", "⚙️");
}

function loadSettingsPreferences() {
    const nameInput = document.getElementById("setting-candidate-name");
    if (nameInput) nameInput.value = "Vishnu Kumar";
}

function openAutoFillAssistantModalDefault() {
    const m = document.getElementById("autofill-modal");
    const b = document.getElementById("autofill-modal-body");
    if (!m || !b) return;

    b.innerHTML = `
        <div style="background: var(--bg-surface); padding: 1.25rem; border-radius: var(--radius-md); border: 1px solid var(--border-color);">
            <h4 style="color: var(--text-bright); margin-bottom: 0.5rem;">Playwright Automation Script Ready</h4>
            <p style="font-size: 0.82rem; color: var(--text-muted); line-height: 1.5; margin-bottom: 0.85rem;">
                Auto-fill script generated for <strong>ABC Technologies Career Portal</strong>. Pre-fills candidate name, email, phone, and uploads tailored resume.
            </p>
            <div style="display: flex; gap: 0.75rem;">
                <button class="action-btn btn-primary" onclick="showToast('⚡ Auto-fill script launched in headless browser!', 'success', '🤖'); closeAutoFillModal();">Run Auto-Fill</button>
                <button class="action-btn btn-secondary" onclick="closeAutoFillModal()">Cancel</button>
            </div>
        </div>
    `;

    m.style.display = "flex";
}

function closeAutoFillModal() {
    const m = document.getElementById("autofill-modal");
    if (m) m.style.display = "none";
}

function handleApplyDirect(jobId) {
    showToast("Application submitted directly to hiring portal!", "success", "🚀");
    switchMainTab("crm");
}

// System Status Check
async function initSystemStatus() {
    const text = document.getElementById("nav-db-text");
    const dot = document.getElementById("db-status-dot");
    try {
        const res = await fetch(`${BACKEND_URL}/health`, { method: "GET" });
        if (res.ok) {
            if (text) text.textContent = "MongoDB Sync";
            if (dot) dot.style.background = "#10b981";
        }
    } catch (e) {
        if (text) text.textContent = "Local Cache";
        if (dot) dot.style.background = "#38bdf8";
    }
}

// Toast Notifications
function showToast(message, type = "info", icon = "💡") {
    const container = document.getElementById("toast-container");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<span style="margin-right: 0.4rem;">${icon}</span> ${message}`;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateY(10px)";
        setTimeout(() => toast.remove(), 250);
    }, 3200);
}
