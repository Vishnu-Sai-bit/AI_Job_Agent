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

// File Upload Handler
async function handleFileUpload(file) {
    const formData = new FormData();
    formData.append("file", file);

    progressContainer.style.display = "block";
    progressBar.style.width = "30%";
    uploadStatus.textContent = "Uploading resume file...";

    try {
        // Step 1: Analyze Resume
        progressBar.style.width = "50%";
        uploadStatus.textContent = "Running AI ATS analysis...";
        
        const analysisResponse = await fetch(`${BACKEND_URL}/analyze-resume`, {
            method: "POST",
            body: formData
        });

        if (!analysisResponse.ok) {
            throw new Error(`ATS analysis failed: ${await analysisResponse.text()}`);
        }

        const analysisResult = await analysisResponse.json();
        resumeData = analysisResult.resume;
        progressBar.style.width = "75%";
        uploadStatus.textContent = "Searching matching jobs...";

        // Step 2: Fetch Matching Jobs (use a new FormData instance to rewind stream)
        const jobFormData = new FormData();
        jobFormData.append("file", file);
        
        const jobResponse = await fetch(`${BACKEND_URL}/search-jobs`, {
            method: "POST",
            body: jobFormData
        });

        if (!jobResponse.ok) {
            throw new Error(`Job search failed: ${await jobResponse.text()}`);
        }

        const jobResult = await jobResponse.json();
        jobData = jobResult.result;

        // Step 3: Complete upload
        progressBar.style.width = "100%";
        uploadStatus.textContent = "Analysis complete!";
        setTimeout(() => {
            progressContainer.style.display = "none";
        }, 1500);

        // Render UI
        renderDashboard();
        renderJobs();
        renderLearning();
        
        // Show the active tab (will show dashboard since data now exists)
        switchTabVisibility();

    } catch (err) {
        console.error(err);
        progressBar.style.width = "0%";
        uploadStatus.textContent = "Upload failed!";
        alert(`Error: ${err.message}`);
    }
}

// ==========================================================
// Render Engines
// ==========================================================

// 1. Dashboard
function renderDashboard() {
    if (!resumeData) return;

    // ATS Score Circular Gradient
    const atsScore = resumeData.ats_score || 0;
    const atsVal = document.getElementById("ats-val");
    atsVal.textContent = `${atsScore}%`;
    
    const atsCircle = document.querySelector(".ats-circle");
    atsCircle.style.background = `conic-gradient(#4f46e5 ${atsScore}%, #db2777 ${atsScore}%, rgba(226, 232, 240, 0.2) ${atsScore}%)`;

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
        { name: "LinkedIn", key: "linkedin", icon: "🔗" },
        { name: "GitHub", key: "github", icon: "💻" },
        { name: "Portfolio", key: "portfolio", icon: "💼" },
        { name: "Kaggle", key: "kaggle", icon: "📊" },
        { name: "LeetCode", key: "leetcode", icon: "🧠" },
        { name: "HackerRank", key: "hackerrank", icon: "🏆" }
    ];

    socials.forEach(s => {
        const val = resumeData[s.key];
        const badge = document.createElement("a");
        badge.className = "social-badge";
        
        if (val) {
            badge.href = val.startsWith("http") ? val : `https://${val}`;
            badge.target = "_blank";
            badge.innerHTML = `<span class="social-badge-icon">${s.icon}</span> ${s.name}`;
        } else {
            badge.classList.add("disabled");
            badge.innerHTML = `<span class="social-badge-icon">❌</span> ${s.name}`;
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
            
            card.innerHTML = `
                <div class="job-match-badge">${score}% Match</div>
                <h4>${job.title}</h4>
                <div class="job-company">${job.company}</div>
                <div class="job-details">
                    <p>📍 <strong>Location:</strong> ${job.location || "N/A"}</p>
                    <p>💰 <strong>Salary Range:</strong> ${job.salary || "N/A"}</p>
                    <p>🔗 <strong>Source:</strong> ${job.provider || "N/A"}</p>
                </div>
                <a href="${job.apply_link || "#"}" target="_blank" class="action-btn-small">Apply for Job</a>
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
            payload = {
                role: title,
                skills
            };
        } else if (activeTool === "email") {
            endpoint = "/generate-emails";
            payload = {
                name,
                skills,
                role: title,
                company
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
<strong>Q${idx + 1}: [${q.type}] ${q.question}</strong>
<em>💡 Answer Strategy:</em> ${q.answer_tips}
<em>🏆 Sample Response:</em> ${q.sample_answer}
--------------------------------------------------
        `).join("\n");
    } else if (activeTool === "email") {
        box.innerHTML = `
<h3>✉️ Direct Application Email</h3>
<strong>Subject:</strong> ${data.job_application ? data.job_application.subject : ""}\n
${data.job_application ? data.job_application.body : ""}

<hr class="divider">

<h3>🤝 Cold Networking Outreach</h3>
<strong>Subject:</strong> ${data.cold_outreach ? data.cold_outreach.subject : ""}\n
${data.cold_outreach ? data.cold_outreach.body : ""}

<hr class="divider">

<h3>✉️ Post-Interview Thank You</h3>
<strong>Subject:</strong> ${data.interview_follow_up ? data.interview_follow_up.subject : ""}\n
${data.interview_follow_up ? data.interview_follow_up.body : ""}
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
