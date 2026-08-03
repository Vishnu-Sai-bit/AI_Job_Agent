/* ==========================================================
   AI JobAgent - Unified Frontend Logic
   Author : Antigravity
   ========================================================== */

// Config
const BACKEND_URL = "https://ai-job-agent-kna8.onrender.com";

// App State
let resumeData = null;
let jobData = null;
let activeTab = "dashboard";
let activeTool = "cover-letter";

// DOM Elements
const dropZone = document.getElementById("drop-zone");
const resumeInput = document.getElementById("resume-input");
const uploadStatus = document.getElementById("upload-status");
const progressContainer = document.getElementById("progress-container");
const progressBar = document.getElementById("progress-bar");

const welcomePlaceholder = document.getElementById("welcome-placeholder");
const tabDashboard = document.getElementById("tab-dashboard");
const tabJobs = document.getElementById("tab-jobs");
const tabTools = document.getElementById("tab-tools");
const tabLearning = document.getElementById("tab-learning");

const themeToggle = document.getElementById("theme-toggle");
const themeIcon = document.getElementById("theme-icon");

// ==========================================================
// Initialization & Event Listeners
// ==========================================================

document.addEventListener("DOMContentLoaded", () => {
    initTheme();
    initTabs();
    initDragAndDrop();
    initTools();
});

// Theme Selector
function initTheme() {
    const savedTheme = localStorage.getItem("theme") || "light";
    document.documentElement.setAttribute("data-theme", savedTheme);
    updateThemeUI(savedTheme);
    
    themeToggle.addEventListener("click", () => {
        const currentTheme = document.documentElement.getAttribute("data-theme");
        const newTheme = currentTheme === "dark" ? "light" : "dark";
        document.documentElement.setAttribute("data-theme", newTheme);
        localStorage.setItem("theme", newTheme);
        updateThemeUI(newTheme);
    });
}

function updateThemeUI(theme) {
    if (theme === "dark") {
        themeIcon.textContent = "☀️";
        themeToggle.innerHTML = `<span>☀️</span> Light Mode`;
    } else {
        themeIcon.textContent = "🌙";
        themeToggle.innerHTML = `<span>🌙</span> Dark Mode`;
    }
}

// Tab switcher
function initTabs() {
    const navButtons = document.querySelectorAll(".nav-btn");
    navButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const targetTab = btn.getAttribute("data-tab");
            
            // Toggle active state on buttons
            navButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            
            // Switch tabs
            activeTab = targetTab;
            switchTabVisibility();
        });
    });
}

function switchTabVisibility() {
    // Hide all
    tabDashboard.style.display = "none";
    tabJobs.style.display = "none";
    tabTools.style.display = "none";
    tabLearning.style.display = "none";
    welcomePlaceholder.style.display = "none";

    // If no resume parsed yet, show welcome placeholder (except on tools tab)
    if (!resumeData && activeTab !== "tools") {
        welcomePlaceholder.style.display = "block";
        return;
    }

    // Show active tab
    if (activeTab === "dashboard") tabDashboard.style.display = "block";
    else if (activeTab === "jobs") tabJobs.style.display = "block";
    else if (activeTab === "tools") tabTools.style.display = "block";
    else if (activeTab === "learning") tabLearning.style.display = "block";
}

// Drag & Drop
function initDragAndDrop() {
    dropZone.addEventListener("click", () => resumeInput.click());
    
    resumeInput.addEventListener("change", (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });

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

// Upload Progress Helper
function setUploadProgress(percentage, text) {
    progressBar.style.width = `${percentage}%`;
    const percentLabel = document.getElementById("progress-percent");
    if (percentLabel) percentLabel.textContent = `${percentage}%`;
    
    uploadStatus.textContent = text;
    
    const statusText = document.getElementById("upload-status-text");
    const statusDot = document.querySelector(".status-dot");
    if (statusText) statusText.textContent = text;
    if (statusDot) {
        if (percentage > 0 && percentage < 100) {
            statusDot.classList.add("loading");
        } else {
            statusDot.classList.remove("loading");
        }
    }
}

// File Upload Handler
async function handleFileUpload(file) {
    const formData = new FormData();
    formData.append("file", file);

    progressContainer.style.display = "block";
    setUploadProgress(30, "Uploading resume file...");

    try {
        // Step 1: Analyze Resume & Search Matching Jobs in one unified pipeline
        setUploadProgress(60, "Running AI ATS analysis & matching jobs...");
        
        const analysisResponse = await fetch(`${BACKEND_URL}/analyze-resume`, {
            method: "POST",
            body: formData
        });

        if (!analysisResponse.ok) {
            throw new Error(`ATS analysis failed: ${await analysisResponse.text()}`);
        }

        const analysisResult = await analysisResponse.json();
        resumeData = analysisResult.resume;
        jobData = analysisResult.result;

        // Fallback: If jobData is somehow not in the unified response, fetch it
        if (!jobData) {
            setUploadProgress(80, "Searching matching jobs...");
            const jobFormData = new FormData();
            jobFormData.append("file", file);
            const jobResponse = await fetch(`${BACKEND_URL}/search-jobs`, {
                method: "POST",
                body: jobFormData
            });
            if (jobResponse.ok) {
                const jobResult = await jobResponse.json();
                jobData = jobResult.result;
            }
        }

        // Step 2: Complete upload
        setUploadProgress(100, "Analysis complete!");
        setTimeout(() => {
            progressContainer.style.display = "none";
            const statusText = document.getElementById("upload-status-text");
            if (statusText) statusText.textContent = "Profile Active";
        }, 1500);

        // Render UI
        renderDashboard();
        renderJobs();
        renderLearning();
        
        // Show the active tab (will show dashboard since data now exists)
        switchTabVisibility();

    } catch (err) {
        console.error(err);
        setUploadProgress(0, "Upload failed!");
        const statusText = document.getElementById("upload-status-text");
        if (statusText) statusText.textContent = "Error Occurred";
        alert(`Error: ${err.message}`);
    }
}

// ==========================================================
// Render Engines
// ==========================================================

// 1. Dashboard
function renderDashboard() {
    if (!resumeData) return;

    // ATS Score SVG Ring Animation
    const atsScore = resumeData.ats_score || 0;
    const atsVal = document.getElementById("ats-val");
    atsVal.textContent = `${atsScore}%`;
    
    const progressCircle = document.getElementById("ats-progress");
    if (progressCircle) {
        // Circumference of our circle is ~264
        const strokeDashOffset = 264 - (atsScore / 100) * 264;
        progressCircle.style.strokeDashoffset = strokeDashOffset;
    }

    // Personal Info
    document.getElementById("info-name").textContent = resumeData.name || "N/A";
    document.getElementById("info-email").textContent = resumeData.email || "N/A";
    document.getElementById("info-phone").textContent = resumeData.phone || "N/A";
    document.getElementById("info-location").textContent = resumeData.location || "N/A";

    // Target preferences
    document.getElementById("pref-role").textContent = resumeData.preferred_role || "N/A";
    document.getElementById("pref-location").textContent = resumeData.preferred_location || "N/A";
    document.getElementById("pref-experience").textContent = resumeData.experience_years || "0";
    document.getElementById("pref-level").textContent = resumeData.career_level || "N/A";

    // Social profile badges
    const socialsContainer = document.getElementById("socials-container");
    socialsContainer.innerHTML = "";
    
    const socials = [
        { name: "Email", key: "email", icon: "✉️", isEmail: true },
        { name: "LinkedIn", key: "linkedin", icon: "🔗" },
        { name: "GitHub", key: "github", icon: "💻" },
        { name: "Portfolio", key: "portfolio", icon: "💼" }
    ];

    socials.forEach(s => {
        const val = resumeData[s.key];
        const badge = document.createElement("a");
        badge.className = "social-badge";
        
        if (val && typeof val === "string" && val.trim() && val.trim() !== "None") {
            const cleanVal = val.trim();
            if (s.isEmail) {
                badge.href = `mailto:${cleanVal}`;
                badge.title = `Send Email to ${cleanVal}`;
            } else {
                badge.href = cleanVal.startsWith("http") ? cleanVal : `https://${cleanVal}`;
                badge.target = "_blank";
                badge.rel = "noopener noreferrer";
                badge.title = `Open ${s.name} (${cleanVal})`;
            }
            badge.innerHTML = `<span class="social-badge-icon">${s.icon}</span> ${s.name}`;
        } else {
            badge.classList.add("disabled");
            badge.innerHTML = `<span class="social-badge-icon">❌</span> ${s.name}`;
            badge.title = `${s.name} not detected`;
            badge.addEventListener("click", (e) => e.preventDefault());
        }
        socialsContainer.appendChild(badge);
    });

    // Profile Suitability details
    const suitabilityDiv = document.getElementById("suitability-report");
    const roleMap = {
        "bi": "Business Intelligence & Visualization (Power BI / Tableau)",
        "ds": "Data Science & Machine Learning (Python / AI / ML)",
        "de": "Data Engineering & Database (SQL / ETL / MySQL)",
        "da": "Data Analyst & Business Analytics"
    };

    const targetRoleLower = (resumeData.preferred_role || "").toLowerCase();
    let primaryRoles = [];
    let secondaryRoles = [];
    
    if (targetRoleLower.includes("power bi") || targetRoleLower.includes("tableau") || targetRoleLower.includes("bi")) {
        primaryRoles = [roleMap.bi, roleMap.da];
        secondaryRoles = [roleMap.de, "IT Support Consultant"];
    } else if (targetRoleLower.includes("machine") || targetRoleLower.includes("scientist") || targetRoleLower.includes("ai")) {
        primaryRoles = [roleMap.ds, roleMap.da];
        secondaryRoles = [roleMap.de, roleMap.bi];
    } else if (targetRoleLower.includes("engineer") || targetRoleLower.includes("sql") || targetRoleLower.includes("database")) {
        primaryRoles = [roleMap.de, roleMap.da];
        secondaryRoles = [roleMap.bi, "Cloud Database Analyst"];
    } else {
        primaryRoles = [roleMap.da, roleMap.bi];
        secondaryRoles = [roleMap.ds, roleMap.de];
    }

    // Populate Suitability UI lists
    const populateList = (id, items) => {
        const el = document.getElementById(id);
        el.innerHTML = items.map(item => `<li>${item}</li>`).join("");
    };
    
    populateList("suitability-roles", primaryRoles);
    populateList("suitability-secondary", secondaryRoles);

    // Key Competitive Strengths
    const strengths = [];
    const skills = resumeData.skills || [];
    const skillsSet = new Set(skills.map(s => s.toLowerCase()));
    
    if (resumeData.certifications && resumeData.certifications.length > 0) {
        strengths.append = strengths.push(`Has ${resumeData.certifications.length} certifications listed, indicating ongoing development.`);
    }
    if (skillsSet.has("python") && skillsSet.has("sql")) {
        strengths.push("Proficient in core scripting and query languages (Python & SQL).");
    }
    if (skillsSet.has("power bi") || skillsSet.has("tableau")) {
        strengths.push("Strong dashboard visualization experience across enterprise tools.");
    }
    if (strengths.length === 0) {
        strengths.push("Solid foundation in analytical projects and business datasets.");
    }
    populateList("suitability-strengths", strengths);

    // Industries
    const industries = ["IT Consulting & Services", "Product-Based Tech MNCs", "Business Intelligence Hubs"];
    populateList("suitability-industries", industries);

    suitabilityDiv.style.display = "block";
}

// 2. Job Matches
function renderJobs() {
    if (!jobData) return;

    // Set stats
    document.getElementById("jobs-stat-found").textContent = jobData.total_jobs_found || 0;
    document.getElementById("jobs-stat-returned").textContent = jobData.total_jobs_returned || 0;
    document.getElementById("jobs-stat-time").textContent = `${jobData.search_time || 0.0}s`;

    const groupByInput = document.querySelector('input[name="group-by"]:checked');
    const groupBy = groupByInput ? groupByInput.value : "category";

    const container = document.getElementById("jobs-list-container");
    container.innerHTML = "";

    const grouped = jobData.grouped_jobs || {};
    const groupKeys = Object.keys(grouped);

    if (groupKeys.length === 0) {
        container.innerHTML = `<div class="card text-center"><p class="muted">No jobs matching your profile score threshold could be found.</p></div>`;
        return;
    }

    // Set listener for radio change
    const radios = document.querySelectorAll('input[name="group-by"]');
    radios.forEach(radio => {
        radio.onclick = () => renderJobs();
    });

    // Perform Grouping
    groupKeys.forEach(groupName => {
        const jobs = grouped[groupName] || [];
        if (jobs.length === 0) return;

        const groupDiv = document.createElement("div");
        groupDiv.className = "job-group";
        
        groupDiv.innerHTML = `
            <div class="job-group-header">
                <span>📁</span> ${groupName} (${jobs.length} jobs)
            </div>
            <div class="job-cards-container"></div>
        `;
        
        const cardsContainer = groupDiv.querySelector(".job-cards-container");
        
        jobs.forEach(job => {
            const card = document.createElement("div");
            card.className = "card job-card";
            
            // Format match score color
            const score = Math.round(job.match_score || 0);
            
            // Render skills matching and missing badges
            const matchPills = (job.matching_skills || []).map(s => `<span class="pill-match">${s} ✔</span>`).join("");
            const missPills = (job.missing_skills || []).map(s => `<span class="pill-missing">${s}</span>`).join("");
            
            card.innerHTML = `
                <div class="job-match-badge">${score}% Match</div>
                <h4>${job.title}</h4>
                <div class="job-company">${job.company}</div>
                <div class="job-details">
                    <p>📍 <strong>Location:</strong> ${job.location || "N/A"}</p>
                    <p>💰 <strong>Salary Range:</strong> ${job.salary || "N/A"}</p>
                    <p>🔗 <strong>Source:</strong> ${job.provider || "N/A"}</p>
                </div>
                
                <div class="job-card-pills">
                    ${matchPills}
                    ${missPills}
                </div>
                
                <div class="job-score-breakdown">
                    <div class="breakdown-item">
                        Role Match
                        <span class="breakdown-val">${Math.round(job.role_match || 0)}%</span>
                    </div>
                    <div class="breakdown-item">
                        Skill Match
                        <span class="breakdown-val">${Math.round(job.skill_match || 0)}%</span>
                    </div>
                    <div class="breakdown-item">
                        Semantic Match
                        <span class="breakdown-val">${Math.round(job.semantic_match || 0)}%</span>
                    </div>
                </div>
                
                <a href="${job.apply_url || "#"}" target="_blank" class="action-btn-small">Apply for Job</a>
            `;
            cardsContainer.appendChild(card);
        });

        container.appendChild(groupDiv);
    });
}

// 3. Learning Roadmaps
function renderLearning() {
    if (!jobData) return;

    // Render skill gaps
    const gapsContainer = document.getElementById("gaps-list");
    gapsContainer.innerHTML = "";

    const roadmapData = jobData.roadmap || {};
    const skillGaps = roadmapData.skill_gaps || [];

    if (skillGaps.length === 0) {
        gapsContainer.innerHTML = `<span class="muted">No significant skill gaps identified for your target preferences!</span>`;
    } else {
        skillGaps.forEach(gap => {
            const badge = document.createElement("span");
            badge.className = "badge-gap";
            badge.textContent = gap;
            gapsContainer.appendChild(badge);
        });
    }

    // Render Learning Path Cards
    const container = document.getElementById("roadmaps-list-container");
    container.innerHTML = "";

    const pathways = roadmapData.roadmaps || [];
    pathways.forEach(path => {
        const card = document.createElement("div");
        card.className = "card roadmap-card";

        const coursesBadges = (path.courses || []).map(c => `<span class="badge-course">📚 ${c}</span>`).join("");
        const certBadges = (path.recommended_certifications || []).map(ce => `<span class="badge-cert">🏆 ${ce}</span>`).join("");

        card.innerHTML = `
            <h4>🎯 Learn ${path.skill}</h4>
            <div class="roadmap-step">
                <strong>📈 Recommended Pathway:</strong>
                <p class="muted">${path.learning_path}</p>
            </div>
            
            <div class="roadmap-step">
                <strong>🛠️ Suggested Portfolio Project:</strong>
                <p class="muted">${path.suggested_project}</p>
            </div>

            <div class="roadmap-step">
                <strong>🏅 Suggested Learning Courses & Certs:</strong>
                <div class="roadmap-badges">
                    ${coursesBadges}
                    ${certBadges}
                </div>
            </div>
        `;
        container.appendChild(card);
    });
}

// ==========================================================
// AI Tools Workspace Logic
// ==========================================================

function initTools() {
    const toolButtons = document.querySelectorAll(".tool-btn");
    toolButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            toolButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            activeTool = btn.getAttribute("data-tool");
            renderToolForm();
        });
    });

    renderToolForm();

    const runBtn = document.getElementById("run-tool-btn");
    runBtn.addEventListener("click", executeTool);

    const copyBtn = document.getElementById("copy-output-btn");
    copyBtn.addEventListener("click", copyToolOutput);
}

function renderToolForm() {
    const container = document.getElementById("tool-form-container");
    container.innerHTML = "";

    const name = resumeData ? resumeData.name : "";
    const role = resumeData ? resumeData.preferred_role : "";
    const skills = resumeData ? (resumeData.skills || []).join(", ") : "";

    if (activeTool === "cover-letter") {
        container.innerHTML = `
            <div class="form-group">
                <label>Candidate Name</label>
                <input type="text" id="tool-name" value="${name}" placeholder="e.g. John Doe">
            </div>
            <div class="form-group">
                <label>Job Title</label>
                <input type="text" id="tool-title" value="${role}" placeholder="e.g. Junior Data Analyst">
            </div>
            <div class="form-group">
                <label>Company Name</label>
                <input type="text" id="tool-company" placeholder="e.g. Google">
            </div>
            <div class="form-group">
                <label>Key Skills (comma separated)</label>
                <input type="text" id="tool-skills" value="${skills}" placeholder="e.g. Python, SQL, Tableau">
            </div>
            <div class="form-group">
                <label>Job Description (Optional)</label>
                <textarea id="tool-desc" rows="4" placeholder="Paste target description to customize metrics..."></textarea>
            </div>
        `;
    } else if (activeTool === "interview") {
        container.innerHTML = `
            <div class="form-group">
                <label>Target Interview Role</label>
                <input type="text" id="tool-title" value="${role}" placeholder="e.g. Data Analyst">
            </div>
            <div class="form-group">
                <label>Core Technical Skills (comma separated)</label>
                <input type="text" id="tool-skills" value="${skills}" placeholder="e.g. SQL, Python, Excel">
            </div>
            <div class="form-group">
                <label>Number of Questions</label>
                <select id="tool-question-count" class="form-select">
                    <option value="5" selected>5 Questions</option>
                    <option value="10">10 Questions</option>
                    <option value="15">15 Questions</option>
                    <option value="20">20 Questions</option>
                </select>
            </div>
            <div class="form-group">
                <label>Interviewer Perspective / Tone</label>
                <select id="tool-interviewer-role" class="form-select">
                    <option value="Senior Technical Recruiter" selected>Senior Technical Recruiter</option>
                    <option value="HR Director / Manager">HR Director / Manager</option>
                    <option value="VP of Engineering / Hiring Manager">VP of Engineering / Hiring Manager</option>
                </select>
            </div>
        `;
    } else if (activeTool === "email") {
        container.innerHTML = `
            <div class="form-group">
                <label>Your Name</label>
                <input type="text" id="tool-name" value="${name}" placeholder="e.g. John Doe">
            </div>
            <div class="form-group">
                <label>Target Role</label>
                <input type="text" id="tool-title" value="${role}" placeholder="e.g. Data Analyst">
            </div>
            <div class="form-group">
                <label>Company Name</label>
                <input type="text" id="tool-company" placeholder="e.g. Microsoft">
            </div>
            <div class="form-group">
                <label>Key Skills (comma separated)</label>
                <input type="text" id="tool-skills" value="${skills}" placeholder="e.g. Python, SQL">
            </div>
        `;
    } else if (activeTool === "linkedin") {
        container.innerHTML = `
            <div class="form-group">
                <label>Your Name</label>
                <input type="text" id="tool-name" value="${name}" placeholder="e.g. John Doe">
            </div>
            <div class="form-group">
                <label>Target Role Focus</label>
                <input type="text" id="tool-title" value="${role}" placeholder="e.g. Business Intelligence Developer">
            </div>
            <div class="form-group">
                <label>Core Skills (comma separated)</label>
                <input type="text" id="tool-skills" value="${skills}" placeholder="e.g. Power BI, DAX, SQL">
            </div>
        `;
    } else if (activeTool === "salary") {
        container.innerHTML = `
            <div class="form-group">
                <label>Target Role</label>
                <input type="text" id="tool-title" value="${role}" placeholder="e.g. Senior Data Analyst">
            </div>
            <div class="form-group">
                <label>Years of Experience</label>
                <input type="number" id="tool-experience" value="${resumeData ? resumeData.experience_years : 1}" step="0.5" placeholder="e.g. 3">
            </div>
            <div class="form-group">
                <label>Location Hub</label>
                <input type="text" id="tool-location" value="${resumeData ? resumeData.location : 'Hyderabad'}" placeholder="e.g. Bengaluru, India">
            </div>
            <div class="form-group">
                <label>Key Skills (comma separated)</label>
                <input type="text" id="tool-skills" value="${skills}" placeholder="e.g. Python, SQL">
            </div>
        `;
    }
}

async function executeTool() {
    const outputBox = document.getElementById("tool-output");
    const copyBtn = document.getElementById("copy-output-btn");
    
    outputBox.textContent = "Thinking... Generating your suggestions using Google Gemini cloud servers...";
    copyBtn.style.display = "none";

    try {
        let endpoint = "";
        let payload = {};

        const name = document.getElementById("tool-name") ? document.getElementById("tool-name").value : "";
        const title = document.getElementById("tool-title") ? document.getElementById("tool-title").value : "";
        const company = document.getElementById("tool-company") ? document.getElementById("tool-company").value : "";
        const skills = document.getElementById("tool-skills") ? document.getElementById("tool-skills").value.split(",").map(s => s.trim()) : [];

        if (activeTool === "cover-letter") {
            endpoint = "/generate-cover-letter";
            payload = {
                name,
                skills,
                job_title: title,
                company,
                job_desc: document.getElementById("tool-desc").value
            };
        } else if (activeTool === "interview") {
            endpoint = "/generate-interview-questions";
            
            let contextText = "";
            if (resumeData) {
                const projectsText = (resumeData.projects || []).map(p => `Project: ${p.title || p.name || ""}. Description: ${p.description || ""}`).join("\n");
                const expText = (resumeData.experience || []).map(e => `Role: ${e.designation || e.role || ""} at ${e.company || ""}. Description: ${e.description || ""}`).join("\n");
                contextText = `Candidate Summary: ${resumeData.career_summary || ""}\n\nWork History:\n${expText}\n\nProjects:\n${projectsText}`;
            }
            
            payload = {
                role: title,
                skills,
                resume_context: contextText,
                question_count: parseInt(document.getElementById("tool-question-count").value) || 5,
                interviewer_role: document.getElementById("tool-interviewer-role").value
            };
        } else if (activeTool === "email") {
            endpoint = "/generate-emails";
            
            let contextText = "";
            if (resumeData) {
                const projectsText = (resumeData.projects || []).map(p => `• Project: ${p.title || p.name || ""}. Details: ${p.description || ""}`).join("\n");
                const expText = (resumeData.experience || []).map(e => `• Experience: ${e.designation || e.role || ""} at ${e.company || ""}. Details: ${e.description || ""}`).join("\n");
                const certText = (resumeData.certifications || []).map(c => `• Certification: ${c}`).join("\n");
                contextText = `Summary: ${resumeData.career_summary || ""}\n\nWork History:\n${expText}\n\nProjects:\n${projectsText}\n\nCertifications:\n${certText}`;
            }

            payload = {
                name,
                skills,
                role: title,
                company: company || "Target Company",
                email: (resumeData && resumeData.email) || "",
                phone: (resumeData && resumeData.phone) || "",
                linkedin: (resumeData && resumeData.linkedin) || "",
                github: (resumeData && resumeData.github) || "",
                portfolio: (resumeData && resumeData.portfolio) || "",
                resume_context: contextText
            };
        } else if (activeTool === "linkedin") {
            endpoint = "/optimize-linkedin";
            payload = {
                name,
                role: title,
                skills,
                experience_text: ""
            };
        } else if (activeTool === "salary") {
            endpoint = "/predict-salary";
            payload = {
                role: title,
                experience_years: parseFloat(document.getElementById("tool-experience").value) || 0,
                skills,
                location: document.getElementById("tool-location").value
            };
        }

        const response = await fetch(`${BACKEND_URL}${endpoint}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`API call failed: ${await response.text()}`);
        }

        const data = await response.json();
        formatToolOutput(data);
        copyBtn.style.display = "block";

    } catch (err) {
        console.error(err);
        outputBox.textContent = `Failed to generate response: ${err.message}`;
    }
}

function formatToolOutput(data) {
    const box = document.getElementById("tool-output");
    box.innerHTML = "";

    if (activeTool === "cover-letter") {
        box.innerHTML = `
<strong>Subject:</strong> ${data.subject}

${data.salutation}

${data.introduction}

${data.body_paragraphs ? data.body_paragraphs.join("\n\n") : ""}

${data.conclusion}

${data.sign_off}
        `;
    } else if (activeTool === "interview") {
        const list = data.questions || [];
        box.innerHTML = list.map((q, idx) => `
<div class="interview-question-block" style="margin-bottom: 1.5rem; padding: 1.5rem; background: rgba(255, 255, 255, 0.03); border-radius: 12px; border-left: 4px solid #db2777; backdrop-filter: blur(10px);">
    <h4 style="color: #f472b6; margin: 0 0 0.8rem 0; font-size: 1.1rem; font-weight: 600;">Q${idx + 1}: [${q.type}] ${q.question}</h4>
    <p style="margin: 0.5rem 0; font-size: 0.95rem; line-height: 1.5;"><strong>💡 Recruiter Strategy & Tips:</strong> ${q.answer_tips}</p>
    <p style="margin: 0.5rem 0; font-size: 0.95rem; line-height: 1.5; color: rgba(255, 255, 255, 0.8);"><strong>🏆 Model Response:</strong> ${q.sample_answer}</p>
</div>
        `).join("");
    } else if (activeTool === "email") {
        box.innerHTML = `
<div class="email-template-card" style="margin-bottom: 2rem; padding: 1.5rem; background: rgba(255, 255, 255, 0.03); border-radius: 12px; border-left: 4px solid #6366f1;">
    <h3 style="color: #818cf8; margin-top: 0; font-size: 1.2rem;">📧 Template 1: Direct Cold Outreach to Hiring Manager</h3>
    <p style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem; margin-bottom: 1rem;"><em>Best for pitching Team Leads, Engineering Managers, or Department Heads directly.</em></p>
    <div style="background: rgba(0, 0, 0, 0.25); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
        <strong>Subject:</strong> ${data.cold_outreach ? data.cold_outreach.subject : ""}<br><br>
        <div style="white-space: pre-wrap; line-height: 1.6;">${data.cold_outreach ? data.cold_outreach.body : ""}</div>
    </div>
</div>

<div class="email-template-card" style="margin-bottom: 2rem; padding: 1.5rem; background: rgba(255, 255, 255, 0.03); border-radius: 12px; border-left: 4px solid #0ea5e9;">
    <h3 style="color: #38bdf8; margin-top: 0; font-size: 1.2rem;">💬 Template 2: LinkedIn Connection Request Note (&lt;300 chars)</h3>
    <p style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem; margin-bottom: 1rem;"><em>Personalized message to attach when sending connection requests on LinkedIn.</em></p>
    <div style="background: rgba(0, 0, 0, 0.25); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
        <div style="white-space: pre-wrap; line-height: 1.6;">${data.linkedin_inmail ? data.linkedin_inmail.body : ""}</div>
    </div>
</div>

<div class="email-template-card" style="margin-bottom: 2rem; padding: 1.5rem; background: rgba(255, 255, 255, 0.03); border-radius: 12px; border-left: 4px solid #f59e0b;">
    <h3 style="color: #fbbf24; margin-top: 0; font-size: 1.2rem;">⏳ Template 3: Strategic Follow-Up Email (4–5 Days Later)</h3>
    <p style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem; margin-bottom: 1rem;"><em>Follow-up note highlighting a project achievement if no response received.</em></p>
    <div style="background: rgba(0, 0, 0, 0.25); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
        <strong>Subject:</strong> ${data.follow_up_email ? data.follow_up_email.subject : ""}<br><br>
        <div style="white-space: pre-wrap; line-height: 1.6;">${data.follow_up_email ? data.follow_up_email.body : ""}</div>
    </div>
</div>

<div class="email-template-card" style="margin-bottom: 2rem; padding: 1.5rem; background: rgba(255, 255, 255, 0.03); border-radius: 12px; border-left: 4px solid #10b981;">
    <h3 style="color: #34d399; margin-top: 0; font-size: 1.2rem;">✉️ Template 4: Formal Job Application Email</h3>
    <p style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem; margin-bottom: 1rem;"><em>Formal cover letter application attaching your resume to HR / Talent Acquisition.</em></p>
    <div style="background: rgba(0, 0, 0, 0.25); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
        <strong>Subject:</strong> ${data.job_application ? data.job_application.subject : ""}<br><br>
        <div style="white-space: pre-wrap; line-height: 1.6;">${data.job_application ? data.job_application.body : ""}</div>
    </div>
</div>
        `;
    } else if (activeTool === "linkedin") {
        const headlines = data.suggested_headlines || [];
        const keywords = data.seo_keywords_to_add || [];
        box.innerHTML = `
<h3>🏆 Suggested Headlines</h3>
${headlines.map(h => `- "${h}"`).join("\n")}

<hr class="divider">

<h3>📝 About Summary</h3>
${data.about_summary}

<hr class="divider">

<h3>🚀 SEO Profile Keywords</h3>
${keywords.map(k => `\`${k}\``).join(", ")}
        `;
    } else if (activeTool === "salary") {
        box.innerHTML = `
<h3>💰 Predicted Market Salary Range</h3>
<strong>Low:</strong> ${data.low.toLocaleString()} ${data.currency}
<strong>Median:</strong> ${data.median.toLocaleString()} ${data.currency}
<strong>High:</strong> ${data.high.toLocaleString()} ${data.currency}

<hr class="divider">

<strong>📈 Local Market Dynamics:</strong>
${data.market_trend}

<hr class="divider">

<strong>🧠 Profile Valuation Justification:</strong>
${data.justification}
        `;
    }
}

function copyToolOutput() {
    const box = document.getElementById("tool-output");
    const text = box.innerText;
    
    navigator.clipboard.writeText(text).then(() => {
        const copyBtn = document.getElementById("copy-output-btn");
        copyBtn.textContent = "✅ Copied!";
        setTimeout(() => {
            copyBtn.textContent = "📋 Copy Output";
        }, 2000);
    }).catch(err => {
        alert("Failed to copy text: ", err);
    });
}
