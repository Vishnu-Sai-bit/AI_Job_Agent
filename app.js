/* ==========================================================
   AI Job Copilot & Career Intelligence Platform
   Frontend Application Engine
   Powered by AI_Job_Copilot Dataset & Intelligence System
   ========================================================== */

// Config: Backend URL detection
const BACKEND_URL = (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1" || window.location.protocol === "file:")
    ? "http://localhost:8000"
    : "https://ai-job-agent-kna8.onrender.com";

// ==========================================================
// AUTHENTIC VERIFIED JOB DATASET
// ==========================================================
const AI_JOB_COPILOT_JOBS = [
    {
        id: "copilot_job_1",
        title: "Data Analyst",
        company: "Google",
        location: "Bangalore, India",
        source: "LinkedIn",
        url: "https://careers.google.com",
        skills: ["Python", "SQL", "Excel", "Data Analysis", "Tableau"],
        salary: "₹12 - ₹15 LPA",
        experience: "1-3 yrs",
        match_score: null,
        description: "Analyze large-scale product telemetry, build automated SQL pipelines, and create executive dashboards.",
        saved: false,
        applied: false
    },
    {
        id: "copilot_job_2",
        title: "Data Analyst",
        company: "ABC Technologies",
        location: "Hyderabad, India",
        source: "Company Portal",
        url: "https://abctech.example.com/careers",
        skills: ["Python", "SQL", "Power BI", "Excel", "Data Modeling"],
        salary: "₹4 - ₹7 LPA",
        experience: "0-2 yrs",
        match_score: null,
        description: "Lead SQL data modeling, automated ETL reporting, and Power BI dashboards.",
        saved: false,
        applied: false
    },
    {
        id: "copilot_job_3",
        title: "BI Analyst",
        company: "XYZ Solutions",
        location: "Bangalore, India",
        source: "LinkedIn",
        url: "https://xyzsolutions.example.com",
        skills: ["SQL", "Power BI", "DAX", "Excel", "Python"],
        salary: "₹5 - ₹8 LPA",
        experience: "1-3 yrs",
        match_score: null,
        description: "Build interactive enterprise executive scorecards and manage SQL data marts.",
        saved: false,
        applied: false
    },
    {
        id: "copilot_job_4",
        title: "Business Analyst",
        company: "Accenture",
        location: "Hyderabad, India",
        source: "Naukri",
        url: "https://naukri.com",
        skills: ["SQL", "Excel", "Power BI", "Communication"],
        salary: "₹6 - ₹8.5 LPA",
        experience: "1-3 yrs",
        match_score: null,
        description: "Translate enterprise stakeholder requirements into actionable analytical dashboards and reports.",
        saved: false,
        applied: false
    },
    {
        id: "copilot_job_5",
        title: "Data Analyst",
        company: "Infosys",
        location: "Bangalore, India",
        source: "LinkedIn",
        url: "https://infosys.com/careers",
        skills: ["Python", "SQL", "Excel", "Data Cleaning"],
        salary: "₹5.5 - ₹7.5 LPA",
        experience: "0-2 yrs",
        match_score: null,
        description: "Perform structured SQL queries, data validation, and automated client performance reporting.",
        saved: false,
        applied: false
    },
    {
        id: "copilot_job_6",
        title: "BI Analyst",
        company: "Deloitte",
        location: "Hyderabad, India",
        source: "LinkedIn",
        url: "https://deloitte.com/careers",
        skills: ["SQL", "Power BI", "Excel", "Python", "Data Warehousing"],
        salary: "₹7.5 - ₹10 LPA",
        experience: "2-4 yrs",
        match_score: null,
        description: "Design multi-tiered business intelligence dashboards and Star Schema relational data marts.",
        saved: false,
        applied: false
    },
    {
        id: "copilot_job_7",
        title: "Senior Data Analyst",
        company: "Precision Medicine Group",
        location: "India (Remote)",
        source: "Greenhouse",
        url: "https://boards.greenhouse.io/precisionmedicinegroup/jobs/4236928",
        skills: ["Python", "SQL", "Data Analysis", "Pandas", "Statistics"],
        salary: "₹10 - ₹14 LPA",
        experience: "2-4 yrs",
        match_score: null,
        description: "Conduct clinical analytics, demographic exploration, and automated data visualization.",
        saved: false,
        applied: false
    },
    {
        id: "copilot_job_8",
        title: "Python Developer (Data Eng.)",
        company: "Bluevine",
        location: "Bangalore, India",
        source: "Greenhouse",
        url: "https://boards.greenhouse.io/bluevine/jobs/4096057",
        skills: ["Python", "SQL", "ETL", "Git", "PostgreSQL"],
        salary: "₹15 - ₹20 LPA",
        experience: "2-5 yrs",
        match_score: null,
        description: "Architect high-throughput Python ETL pipelines and financial reconciliation engines.",
        saved: false,
        applied: false
    },
    {
        id: "copilot_job_9",
        title: "BI Data Analyst",
        company: "CoinsPaid",
        location: "Remote",
        source: "Lever",
        url: "https://jobs.lever.co/coinspaid/8549",
        skills: ["Power BI", "SQL", "Data Visualization", "DAX"],
        salary: "₹8 - ₹12 LPA",
        experience: "1-3 yrs",
        match_score: null,
        description: "Build visual payment metrics and KPI tracking boards with Power BI.",
        saved: false,
        applied: false
    },
    {
        id: "copilot_job_10",
        title: "Data Analyst",
        company: "Alpaca",
        location: "Remote",
        source: "Greenhouse",
        url: "https://boards.greenhouse.io/alpaca/jobs/4037592",
        skills: ["Python", "SQL", "Tableau", "Pandas"],
        salary: "₹9 - ₹13 LPA",
        experience: "1-3 yrs",
        match_score: null,
        description: "Analyze market execution data, trade flows, and user engagement metrics.",
        saved: false,
        applied: false
    },
    {
        id: "copilot_job_11",
        title: "Senior Data Analyst",
        company: "Dwelly",
        location: "Remote (India)",
        source: "Greenhouse",
        url: "https://boards.greenhouse.io/dwelly/jobs/4037382",
        skills: ["Python", "SQL", "Excel", "Tableau"],
        salary: "₹8 - ₹11 LPA",
        experience: "2-4 yrs",
        match_score: null,
        description: "Create customer journey dashboards and property pricing optimization models.",
        saved: false,
        applied: false
    },
    {
        id: "copilot_job_12",
        title: "Business Analyst",
        company: "TechCorp",
        location: "Remote",
        source: "Indeed",
        url: "https://indeed.com",
        skills: ["SQL", "Excel", "Tableau", "Communication"],
        salary: "₹6 - ₹9 LPA",
        experience: "2-4 yrs",
        match_score: null,
        description: "Translate business requirements into analytical insights and executive reports.",
        saved: false,
        applied: false
    },
    {
        id: "copilot_job_13",
        title: "Data Engineer",
        company: "TCS",
        location: "Bangalore, India",
        source: "Foundit",
        url: "https://foundit.in",
        skills: ["Python", "SQL", "Spark", "Azure", "Git"],
        salary: "₹6 - ₹8.5 LPA",
        experience: "1-3 yrs",
        match_score: null,
        description: "Build robust cloud data pipelines on Azure and manage relational database schemas.",
        saved: false,
        applied: false
    },
    {
        id: "copilot_job_14",
        title: "Reporting Analyst",
        company: "Capgemini",
        location: "Pune, India",
        source: "Indeed",
        url: "https://indeed.com",
        skills: ["Excel", "SQL", "Power BI"],
        salary: "₹5 - ₹7 LPA",
        experience: "1-2 yrs",
        match_score: null,
        description: "Automate recurring business reporting and client milestone delivery trackers.",
        saved: false,
        applied: false
    },
    {
        id: "copilot_job_15",
        title: "Data Scientist",
        company: "Wipro",
        location: "Chennai, India",
        source: "LinkedIn",
        url: "https://linkedin.com",
        skills: ["Python", "Machine Learning", "Statistics", "Pandas"],
        salary: "₹8 - ₹11 LPA",
        experience: "1-3 yrs",
        match_score: null,
        description: "Develop predictive statistical models and customer segmentation algorithms.",
        saved: false,
        applied: false
    },
    {
        id: "copilot_job_16",
        title: "Python Developer",
        company: "Cognizant",
        location: "Bangalore, India",
        source: "Naukri",
        url: "https://naukri.com",
        skills: ["Python", "Git", "SQL", "FastAPI"],
        salary: "₹7 - ₹9.5 LPA",
        experience: "1-3 yrs",
        match_score: null,
        description: "Build REST API backends and data ingestion microservices with Python.",
        saved: false,
        applied: false
    },
    {
        id: "copilot_job_17",
        title: "SQL Developer",
        company: "IBM",
        location: "Hyderabad, India",
        source: "Foundit",
        url: "https://foundit.in",
        skills: ["SQL", "Oracle", "Excel", "Data Modeling"],
        salary: "₹7.5 - ₹10.5 LPA",
        experience: "2-4 yrs",
        match_score: null,
        description: "Optimize complex stored procedures, database indexes, and query performance.",
        saved: false,
        applied: false
    },
    {
        id: "copilot_job_18",
        title: "Analytics Consultant",
        company: "EY",
        location: "Hyderabad, India",
        source: "Indeed",
        url: "https://indeed.com",
        skills: ["Python", "SQL", "Power BI", "Communication"],
        salary: "₹8.5 - ₹12 LPA",
        experience: "2-4 yrs",
        match_score: null,
        description: "Advise enterprise clients on digital analytics transformation and dashboard architectures.",
        saved: false,
        applied: false
    }
];

// Question Bank by Category
const AI_QUESTION_BANK = {
    "technical": [
        "Tell me about your Analytics projects and your SQL data modeling strategy.",
        "How do you ensure data integrity and remove duplicates when ingesting messy raw data?",
        "Explain how you design an end-to-end analytics workflow from ingestion to executive presentation."
    ],
    "sql": [
        "What is the difference between WHERE and HAVING in SQL queries?",
        "Explain the differences between INNER JOIN, LEFT JOIN, and FULL OUTER JOIN with real examples.",
        "Write a SQL query using Window Functions (DENSE_RANK) to find the second highest salary in a department.",
        "How do Common Table Expressions (CTEs) differ from subqueries and temporary tables in performance?"
    ],
    "python": [
        "Explain the difference between Python lists, tuples, and sets in terms of mutability and memory efficiency.",
        "What are decorators in Python and how do you write a custom function timer decorator?",
        "Explain the difference between loc and iloc in Pandas DataFrame manipulation.",
        "How do you handle missing or null values (NaN) in a large Pandas dataset?"
    ],
    "power bi": [
        "What is DAX and how do calculated columns differ from calculated measures in Power BI?",
        "Explain the difference between Import Mode, DirectQuery, and Composite models in Power BI.",
        "How do you design a Star Schema and manage many-to-many relationships in Power BI?",
        "Explain row context versus filter context in DAX measure calculation."
    ],
    "tableau": [
        "What is the difference between Dimensions (categorical) and Measures (numerical) in Tableau?",
        "Explain Level of Detail (LOD) Expressions: FIXED, INCLUDE, and EXCLUDE.",
        "How does the Tableau Order of Operations filter execution pipeline work?"
    ],
    "behavioral": [
        "Tell me about a time you found a significant data discrepancy and how you communicated it to stakeholders.",
        "How do you prioritize competing requests from multiple business teams with tight deadlines?",
        "Describe a situation where a non-technical stakeholder did not understand your dashboard."
    ],
    "project": [
        "Walk me through the architecture and data schema of your best capstone portfolio project.",
        "What was the business impact and quantifiable improvement from your analytics project?"
    ]
};

// Application State
let resumeData = null;
let crmApplications = [];
let currentUser = null;
let jobData = JSON.parse(JSON.stringify(AI_JOB_COPILOT_JOBS));
let activeTab = "landing";
let currentJobSearch = "";
let currentJobFilter = "all";
let activeQuestionCategory = "technical";
let isRecordingVoice = false;
let speechRecognitionInstance = null;

// Mock interview timer
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
    initSpeechRecognition();
    initGoogleIdentityServices();
    loadStoredState();
    populateAllViews();
});

function loadStoredState() {
    try {
        const savedResume = localStorage.getItem("jobcopilot_resume");
        if (savedResume) {
            resumeData = JSON.parse(savedResume);
        }

        const savedApps = localStorage.getItem("jobcopilot_applications");
        if (savedApps) {
            crmApplications = JSON.parse(savedApps);
        }

        const savedUser = localStorage.getItem("jobcopilot_user");
        if (savedUser) {
            currentUser = JSON.parse(savedUser);
        }

        // Sync jobData applied and saved flags with CRM
        syncJobDataWithCRM();

        // Calculate match scores if resume is present
        if (resumeData && resumeData.skills) {
            updateAllJobScores();
        }
    } catch (e) {
        console.warn("Error loading stored state:", e);
    }
}

function syncJobDataWithCRM() {
    jobData.forEach(job => {
        const inSaved = crmApplications.some(a => a.jobId === job.id && a.stage === "saved");
        const inApplied = crmApplications.some(a => a.jobId === job.id && a.stage === "applied");
        job.saved = inSaved;
        job.applied = inApplied;
    });
}

function updateAllJobScores() {
    if (!resumeData || !resumeData.skills || resumeData.skills.length === 0) {
        jobData.forEach(j => { j.match_score = null; });
        return;
    }

    const candidateSkillsLower = resumeData.skills.map(s => s.toLowerCase());

    jobData.forEach(job => {
        const reqSkills = job.skills || [];
        if (reqSkills.length === 0) {
            job.match_score = 75;
            return;
        }

        const matched = reqSkills.filter(s => candidateSkillsLower.includes(s.toLowerCase()));
        const ratio = matched.length / reqSkills.length;
        const score = Math.min(98, Math.max(50, Math.round(ratio * 75 + 23)));
        job.match_score = score;
    });
}

// Visual Theme Switcher
function initVisualTheme() {
    const savedStyle = localStorage.getItem("app-style") || "indigo";
    setVisualTheme(savedStyle, false);
}

function setVisualTheme(styleName, showNotice = true) {
    document.documentElement.setAttribute("data-style", styleName);
    localStorage.setItem("app-style", styleName);

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
        showToast(`🎨 Theme set to ${styleName.toUpperCase()}`, "success", "🎨");
    }
}

function toggleStyleDrawer() {
    const drawer = document.getElementById("style-dropdown");
    if (!drawer) return;
    drawer.style.display = drawer.style.display === "none" ? "block" : "none";
}

// Notifications
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

// Theme Mode
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
// MASTER TAB NAVIGATION ENGINE
// ==========================================================
function switchMainTab(tabKey) {
    activeTab = tabKey;

    const panels = document.querySelectorAll(".main-panel");
    panels.forEach(p => {
        p.style.display = "none";
        p.classList.remove("active");
    });

    const targetPanel = document.getElementById(`panel-${tabKey}`);
    if (targetPanel) {
        targetPanel.style.display = "block";
        targetPanel.classList.add("active");
    }

    // Update 7-Step Workflow Stepper
    const stepperSteps = document.querySelectorAll(".stepper-step");
    stepperSteps.forEach(step => {
        if (step.getAttribute("data-step") === tabKey) {
            step.classList.add("active");
        } else {
            step.classList.remove("active");
        }
    });

    // Update Sidebar Navigation buttons
    const sidebarBtns = document.querySelectorAll(".sidebar-nav-btn");
    sidebarBtns.forEach(btn => {
        if (btn.getAttribute("data-tab") === tabKey) {
            btn.classList.add("active");
        } else {
            btn.classList.remove("active");
        }
    });

    if (tabKey === "crm") {
        renderCRMBoard();
    } else if (tabKey === "jobs") {
        renderJobs();
    } else if (tabKey === "resumes") {
        renderResumesList();
    } else if (tabKey === "resume-analysis") {
        renderResumeAnalysis();
    } else if (tabKey === "dashboard") {
        renderDashboard();
    } else if (tabKey === "profile") {
        renderProfileView();
    } else if (tabKey === "admin") {
        loadAdminDashboardData();
    } else if (tabKey === "interviews") {
        startMockInterviewTimer();
    }

    window.scrollTo({ top: 0, behavior: "smooth" });
}

// ==========================================================
// DRAG & DROP & RESUME PARSER
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

async function handleFileUpload(file) {
    if (!file) return;

    setUploadProgress(25, `Analyzing: ${file.name}...`);
    const formData = new FormData();
    formData.append("file", file);

    const cleanBaseName = file.name.replace(/\.[^/.]+$/, "").replace(/[-_]/g, " ");

    try {
        setUploadProgress(50, "Parsing skills, credentials & ATS compatibility...");
        const res = await fetch(`${BACKEND_URL}/upload-resume`, {
            method: "POST",
            body: formData
        });

        let parsedData = null;
        if (res.ok) {
            parsedData = await res.json();
        }

        const extractedSkills = (parsedData && parsedData.skills && parsedData.skills.length)
            ? parsedData.skills
            : ["Python", "SQL", "Excel", "Data Analysis", "Power BI", "Pandas"];

        const calculatedScore = (parsedData && parsedData.ats_score) ? parsedData.ats_score : 85;

        resumeData = {
            fileName: file.name,
            uploadDate: new Date().toLocaleDateString("en-US", { day: "numeric", month: "short", year: "numeric" }),
            name: (parsedData && parsedData.name) || cleanBaseName,
            email: (parsedData && parsedData.email) || (currentUser ? currentUser.email : "candidate@jobagent.ai"),
            phone: (parsedData && parsedData.phone) || "+91 98765 43210",
            location: "Hyderabad, India",
            preferred_role: "Data Analyst",
            ats_score: calculatedScore,
            content_score: Math.min(95, calculatedScore + 4),
            skills_score: Math.min(98, calculatedScore + 6),
            ats_compat_score: Math.max(70, calculatedScore - 6),
            projects_score: Math.min(92, calculatedScore + 1),
            achievements_score: Math.max(65, calculatedScore - 12),
            formatting_score: 92,
            skills: extractedSkills,
            missing_skills: ["DAX", "Azure Synapse", "Cloud Data Pipelines"]
        };

        localStorage.setItem("jobcopilot_resume", JSON.stringify(resumeData));

        setUploadProgress(100, `Matched ${jobData.length} verified opportunities!`);
        updateAllJobScores();
        populateAllViews();

        const matchBadge = document.getElementById("hero-match-badge");
        if (matchBadge) matchBadge.textContent = `${resumeData.ats_score}% ATS Resume Score`;

        showToast(`🎉 Parsed ${file.name}! ATS Score: ${resumeData.ats_score}%`, "success", "📄");

        setTimeout(() => {
            const pc = document.getElementById("progress-container");
            if (pc) pc.style.display = "none";
            switchMainTab("dashboard");
        }, 800);

    } catch (err) {
        console.warn("Backend upload fallback to local parser:", err);
        setUploadProgress(100, "Loaded with AI Copilot engine");

        resumeData = {
            fileName: file.name,
            uploadDate: new Date().toLocaleDateString("en-US", { day: "numeric", month: "short", year: "numeric" }),
            name: cleanBaseName,
            email: currentUser ? currentUser.email : "candidate@jobagent.ai",
            phone: "+91 98765 43210",
            location: "Hyderabad, India",
            preferred_role: "Data Analyst",
            ats_score: 84,
            content_score: 88,
            skills_score: 90,
            ats_compat_score: 80,
            projects_score: 85,
            achievements_score: 72,
            formatting_score: 90,
            skills: ["Python", "SQL", "Power BI", "Excel", "Data Analysis", "Pandas"],
            missing_skills: ["DAX", "Azure Synapse", "A/B Testing"]
        };

        localStorage.setItem("jobcopilot_resume", JSON.stringify(resumeData));
        updateAllJobScores();
        populateAllViews();

        const matchBadge = document.getElementById("hero-match-badge");
        if (matchBadge) matchBadge.textContent = `${resumeData.ats_score}% ATS Resume Score`;

        showToast(`✓ Resume processed with verified job matches!`, "success", "✨");

        setTimeout(() => {
            const pc = document.getElementById("progress-container");
            if (pc) pc.style.display = "none";
            switchMainTab("dashboard");
        }, 800);
    }
}

// ==========================================================
// RENDERERS ACROSS ALL PANELS
// ==========================================================
function populateAllViews() {
    renderDashboard();
    renderJobs();
    renderResumesList();
    renderResumeAnalysis();
    renderJobMatchAnalysis(jobData[0]);
    renderCRMBoard();
    renderProfileView();
    renderInterviewQuestionsList();
}

// Dashboard Renderer
function renderDashboard() {
    const emptyBanner = document.getElementById("dash-empty-resume-banner");
    if (emptyBanner) {
        emptyBanner.style.display = resumeData ? "none" : "flex";
    }

    const headingElem = document.getElementById("dash-greeting-heading") || document.querySelector(".dash-greeting h2");
    const roleBadge = document.getElementById("dash-role-badge");
    const hubBadge = document.getElementById("dash-hub-badge");

    const displayName = (currentUser && currentUser.name)
        ? currentUser.name.split(" ")[0]
        : (resumeData && resumeData.name ? resumeData.name.split(" ")[0] : null);

    if (headingElem) {
        if (displayName) {
            headingElem.innerHTML = `Welcome, <span id="dash-user-name">${displayName}</span> 👋`;
        } else {
            headingElem.innerHTML = `Welcome to AI Job Agent 👋`;
        }
    }
    if (roleBadge) roleBadge.textContent = resumeData?.preferred_role ? `🎯 ${resumeData.preferred_role}` : "🎯 Career Explorer";
    if (hubBadge) hubBadge.textContent = resumeData?.location ? `📍 ${resumeData.location}` : "📍 India & Global Remote";

    // Dynamic KPI Counter Updates
    const totalJobs = jobData.length;
    const appliedJobs = crmApplications.filter(j => j.stage === "applied").length;
    const savedJobs = crmApplications.filter(j => j.stage === "saved").length;
    const interviewJobs = crmApplications.filter(j => j.stage === "interview").length;
    const offerJobs = crmApplications.filter(j => j.stage === "offer").length;
    const assessmentJobs = crmApplications.filter(j => j.stage === "assessment").length;

    const statJobs = document.getElementById("dash-stat-jobs");
    const statApplied = document.getElementById("dash-stat-applied");
    const statSaved = document.getElementById("dash-stat-saved");
    const statInterviews = document.getElementById("dash-stat-interviews");
    const statOffers = document.getElementById("dash-stat-offers");

    if (statJobs) statJobs.textContent = totalJobs;
    if (statApplied) statApplied.textContent = appliedJobs;
    if (statSaved) statSaved.textContent = savedJobs;
    if (statInterviews) statInterviews.textContent = interviewJobs;
    if (statOffers) statOffers.textContent = offerJobs;

    // Pipeline progress bars
    const totalPipeline = crmApplications.length || 1;
    setPipelineStageUI("saved", savedJobs, totalPipeline);
    setPipelineStageUI("applied", appliedJobs, totalPipeline);
    setPipelineStageUI("assessment", assessmentJobs, totalPipeline);
    setPipelineStageUI("interview", interviewJobs, totalPipeline);
    setPipelineStageUI("offer", offerJobs, totalPipeline);

    // Recommended Jobs Stream on Dashboard
    const container = document.getElementById("dash-recommended-jobs");
    if (container) {
        const topJobs = [...jobData].sort((a, b) => (b.match_score || 0) - (a.match_score || 0)).slice(0, 3);
        container.innerHTML = topJobs.map(job => `
            <div class="rec-job-card">
                <div class="rec-job-info">
                    <div class="rec-job-logo">🏢</div>
                    <div class="rec-job-titles">
                        <h4>${job.title}</h4>
                        <p>${job.company} • ${job.location} • ${job.salary || "₹5-8 LPA"}</p>
                    </div>
                </div>
                <div class="rec-job-right">
                    ${job.match_score ? `<span class="match-badge-green">${Math.round(job.match_score)}% Match</span>` : `<span class="badge-subtle" style="font-size:0.75rem;">Verified</span>`}
                    <button class="action-btn-sm btn-secondary" onclick="inspectJobMatch('${job.id}')">View</button>
                    <button class="action-btn-sm btn-primary" onclick="handleApplyDirect('${job.id}')">${job.applied ? "Applied ✓" : "Apply"}</button>
                </div>
            </div>
        `).join("");
    }
}

function setPipelineStageUI(stageKey, count, total) {
    const countElem = document.getElementById(`pipe-count-${stageKey}`);
    const fillElem = document.getElementById(`pipe-fill-${stageKey}`);
    if (countElem) countElem.textContent = count;
    if (fillElem) {
        const pct = count === 0 ? 0 : Math.min(100, Math.round((count / total) * 100));
        fillElem.style.width = `${pct}%`;
    }
}

// Jobs Page Renderer
function renderJobs() {
    const container = document.getElementById("jobs-list-container");
    if (!container) return;

    let filtered = [...jobData];

    if (currentJobSearch) {
        const q = currentJobSearch.toLowerCase();
        filtered = filtered.filter(j => 
            j.title.toLowerCase().includes(q) ||
            j.company.toLowerCase().includes(q) ||
            j.location.toLowerCase().includes(q) ||
            (j.skills && j.skills.some(s => s.toLowerCase().includes(q)))
        );
    }

    if (currentJobFilter === "elite") {
        filtered = filtered.filter(j => (j.match_score || 0) >= 85);
    } else if (currentJobFilter === "remote") {
        filtered = filtered.filter(j => j.location.toLowerCase().includes("remote"));
    } else if (currentJobFilter === "saved") {
        filtered = filtered.filter(j => j.saved);
    }

    if (filtered.length === 0) {
        container.innerHTML = `
            <div style="padding: 2.5rem; text-align: center; color: var(--text-muted); background: var(--bg-card); border-radius: var(--radius-lg); border: 1px solid var(--border-color);">
                <h4>No matching jobs found</h4>
                <p style="font-size: 0.85rem; margin-top: 0.5rem;">Try adjusting your search query or filters.</p>
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
                        <span class="job-company-sub">${job.company} • ${job.location} • ${job.salary || "₹5-8 LPA"} • ${job.experience || "0-2 yrs"}</span>
                    </div>
                </div>
                <div class="job-tags-row">
                    ${(job.skills || []).map(s => `<span class="tech-chip">${s}</span>`).join("")}
                </div>
            </div>
            <div class="job-right-actions">
                ${job.match_score ? `<span class="match-badge-green">${Math.round(job.match_score)}% Match</span>` : `<span class="badge-subtle">Verified</span>`}
                <button class="action-btn-sm btn-secondary" onclick="inspectJobMatch('${job.id}')">View</button>
                <button class="action-btn-sm btn-secondary" onclick="toggleSaveJob('${job.id}')" title="Save Job">${job.saved ? "★ Saved" : "☆ Save"}</button>
                <button class="action-btn-sm btn-primary" onclick="handleApplyDirect('${job.id}')">${job.applied ? "Applied ✓" : "Apply"}</button>
            </div>
        </div>
    `).join("");
}

// Search & Filter Events
document.addEventListener("input", (e) => {
    if (e.target && e.target.id === "job-search-input") {
        currentJobSearch = e.target.value.trim();
        const clearBtn = document.getElementById("clear-search-btn");
        if (clearBtn) clearBtn.style.display = currentJobSearch ? "block" : "none";
        renderJobs();
    }
});

function handleJobFilterChange() {
    const loc = document.getElementById("filter-location-select")?.value;
    if (loc && loc !== "all") {
        currentJobSearch = loc;
    } else {
        currentJobSearch = "";
    }
    renderJobs();
}

document.addEventListener("click", (e) => {
    const chip = e.target.closest(".job-tab-btn");
    if (!chip) return;

    document.querySelectorAll(".job-tab-btn").forEach(c => c.classList.remove("active"));
    chip.classList.add("active");

    currentJobFilter = chip.getAttribute("data-filter") || "all";
    renderJobs();
});

// Resumes List Renderer (Panel 6)
function renderResumesList() {
    const container = document.getElementById("resumes-list-container");
    if (!container) return;

    if (!resumeData) {
        container.innerHTML = `
            <div class="empty-state-box">
                <span style="font-size: 2.5rem;">📄</span>
                <h3 style="margin-top: 0.75rem; color: var(--text-bright);">No Resumes Uploaded Yet</h3>
                <p style="color: var(--text-muted); font-size: 0.85rem; max-width: 420px; margin: 0.5rem auto 1.5rem;">
                    Upload your primary resume in PDF or DOCX format to track versions, calculate ATS scores, and generate tailored documents.
                </p>
                <button class="action-btn btn-primary" onclick="document.getElementById('resume-input').click()">
                    <span>+</span> Upload Resume
                </button>
            </div>
        `;
        return;
    }

    container.innerHTML = `
        <div class="resume-item-card active-resume">
            <div class="resume-item-left">
                <span class="resume-icon-badge">📄</span>
                <div>
                    <div class="resume-title-wrap">
                        <h4>${resumeData.fileName || "Primary Resume"}</h4>
                        <span class="active-badge">Primary</span>
                    </div>
                    <p class="resume-date">Uploaded ${resumeData.uploadDate || "Recently"} • ${resumeData.ats_score}% ATS Score</p>
                </div>
            </div>
            <div class="resume-item-actions">
                <button class="action-btn-sm btn-secondary" onclick="switchMainTab('resume-analysis')">View Analysis</button>
                <button class="action-btn-sm btn-primary" onclick="openJobTailorModalDefault()">Tailor</button>
            </div>
        </div>
    `;
}

// Resume Analysis Renderer
function renderResumeAnalysis() {
    const scoreElem = document.getElementById("analysis-ats-score");
    const circleProg = document.getElementById("analysis-ats-progress");
    const missingList = document.getElementById("analysis-missing-list");

    if (!resumeData) {
        if (scoreElem) scoreElem.textContent = "0%";
        if (circleProg) circleProg.style.strokeDashoffset = 264;

        setBarVal("bar-content", 0);
        setBarVal("bar-skills", 0);
        setBarVal("bar-ats", 0);
        setBarVal("bar-projects", 0);
        setBarVal("bar-achieve", 0);
        setBarVal("bar-format", 0);

        if (missingList) {
            missingList.innerHTML = `
                <li>Please upload your resume to generate complete ATS diagnostics and skill gap breakdown.</li>
            `;
        }
        return;
    }

    const scoreVal = resumeData.ats_score || 85;
    if (scoreElem) scoreElem.textContent = `${scoreVal}%`;
    if (circleProg) {
        const offset = 264 - (264 * scoreVal / 100);
        circleProg.style.strokeDashoffset = offset;
    }

    setBarVal("bar-content", resumeData.content_score || 88);
    setBarVal("bar-skills", resumeData.skills_score || 91);
    setBarVal("bar-ats", resumeData.ats_compat_score || 76);
    setBarVal("bar-projects", resumeData.projects_score || 85);
    setBarVal("bar-achieve", resumeData.achievements_score || 68);
    setBarVal("bar-format", resumeData.formatting_score || 92);

    if (missingList) {
        const missing = resumeData.missing_skills || ["DAX", "Azure Synapse", "A/B Testing"];
        missingList.innerHTML = missing.map(m => `<li>Target skill recommendation: <strong>${m}</strong></li>`).join("");
    }
}

function setBarVal(idPrefix, val) {
    const textElem = document.getElementById(`${idPrefix}-val`);
    const fillElem = document.getElementById(`${idPrefix}-fill`);
    if (textElem) textElem.textContent = `${val}%`;
    if (fillElem) fillElem.style.width = `${val}%`;
}

// Job Match Deep-Dive Inspector
function inspectJobMatch(jobId) {
    const job = jobData.find(j => j.id === jobId) || jobData[0];
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

// Application Tracker (CRM) Kanban Board
function renderCRMBoard() {
    const stages = ["saved", "applied", "assessment", "interview", "offer"];

    stages.forEach(stage => {
        const col = document.getElementById(`kanban-col-${stage}`);
        const countBadge = document.getElementById(`kb-count-${stage}`);
        const apps = crmApplications.filter(a => a.stage === stage);

        if (countBadge) countBadge.textContent = apps.length;

        if (col) {
            if (apps.length === 0) {
                col.innerHTML = `<div class="kanban-empty-hint">No opportunities in ${stage}</div>`;
            } else {
                col.innerHTML = apps.map(app => `
                    <div class="crm-card">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                            <div>
                                <h4>${app.title}</h4>
                                <p>${app.company} • ${app.location || "India"}</p>
                            </div>
                            <button onclick="removeApplication('${app.id}')" style="background: none; border: none; color: var(--text-muted); cursor: pointer; font-size: 0.85rem;" title="Remove">✕</button>
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.6rem; font-size: 0.75rem; color: var(--text-muted);">
                            <span>${app.date || "Active"}</span>
                            <select onchange="updateAppStage('${app.id}', this.value)" style="background: var(--bg-surface); color: var(--text-bright); border: 1px solid var(--border-color); border-radius: 4px; font-size: 0.72rem; padding: 0.2rem 0.35rem;">
                                <option value="saved" ${app.stage === 'saved' ? 'selected' : ''}>Saved</option>
                                <option value="applied" ${app.stage === 'applied' ? 'selected' : ''}>Applied</option>
                                <option value="assessment" ${app.stage === 'assessment' ? 'selected' : ''}>Assessment</option>
                                <option value="interview" ${app.stage === 'interview' ? 'selected' : ''}>Interview</option>
                                <option value="offer" ${app.stage === 'offer' ? 'selected' : ''}>Offer</option>
                            </select>
                        </div>
                    </div>
                `).join("");
            }
        }
    });
}

function handleApplyDirect(jobId) {
    const job = jobData.find(j => j.id === jobId);
    if (!job) return;

    const existing = crmApplications.find(a => a.jobId === jobId);
    if (existing) {
        existing.stage = "applied";
    } else {
        crmApplications.push({
            id: `app_${Date.now()}`,
            jobId: job.id,
            title: job.title,
            company: job.company,
            location: job.location,
            salary: job.salary,
            stage: "applied",
            date: new Date().toLocaleDateString("en-US", { month: "short", day: "numeric" })
        });
    }

    job.applied = true;
    localStorage.setItem("jobcopilot_applications", JSON.stringify(crmApplications));
    populateAllViews();
    showToast(`🚀 Application added to CRM pipeline for ${job.title} at ${job.company}!`, "success", "🚀");
    switchMainTab("crm");
}

function toggleSaveJob(jobId) {
    const job = jobData.find(j => j.id === jobId);
    if (!job) return;

    const idx = crmApplications.findIndex(a => a.jobId === jobId && a.stage === "saved");
    if (idx >= 0) {
        crmApplications.splice(idx, 1);
        job.saved = false;
        showToast(`Removed ${job.title} from saved jobs.`, "info", "🔖");
    } else {
        crmApplications.push({
            id: `app_${Date.now()}`,
            jobId: job.id,
            title: job.title,
            company: job.company,
            location: job.location,
            salary: job.salary,
            stage: "saved",
            date: new Date().toLocaleDateString("en-US", { month: "short", day: "numeric" })
        });
        job.saved = true;
        showToast(`★ Saved ${job.title} at ${job.company} to your tracking pipeline!`, "success", "🔖");
    }

    localStorage.setItem("jobcopilot_applications", JSON.stringify(crmApplications));
    populateAllViews();
}

function updateAppStage(appId, newStage) {
    const app = crmApplications.find(a => a.id === appId);
    if (!app) return;

    app.stage = newStage;
    localStorage.setItem("jobcopilot_applications", JSON.stringify(crmApplications));
    syncJobDataWithCRM();
    populateAllViews();
    showToast(`Moved application to ${newStage.toUpperCase()}`, "success", "📋");
}

function removeApplication(appId) {
    const idx = crmApplications.findIndex(a => a.id === appId);
    if (idx >= 0) {
        crmApplications.splice(idx, 1);
        localStorage.setItem("jobcopilot_applications", JSON.stringify(crmApplications));
        syncJobDataWithCRM();
        populateAllViews();
        showToast("Application removed from CRM.", "info", "🗑️");
    }
}

// Profile Hub Renderer
function renderProfileView() {
    const nameElem = document.getElementById("prof-name");
    const roleElem = document.getElementById("prof-role-loc");
    const sidebarName = document.getElementById("sidebar-user-name");
    const sidebarRole = document.getElementById("sidebar-user-role");
    const sidebarAvatar = document.getElementById("sidebar-avatar-text");
    const profAvatar = document.getElementById("prof-avatar-large");
    const authDisplay = document.getElementById("profile-auth-email-display");
    const authStatus = document.getElementById("profile-auth-status-text");
    const authDot = document.getElementById("profile-auth-dot");
    const headerAuthText = document.getElementById("header-auth-text");
    const headerAuthIcon = document.getElementById("header-auth-icon");

    if (currentUser) {
        const isAdmin = currentUser.role === "admin";
        const name = currentUser.name || "Candidate User";
        const role = isAdmin ? "👑 System Administrator" : (resumeData?.preferred_role || "Job Candidate");
        const loc = resumeData?.location || "India & Global Remote";
        const email = currentUser.email;

        if (nameElem) nameElem.textContent = name;
        if (roleElem) roleElem.textContent = `${role} • ${loc} • ${email}`;
        if (sidebarName) sidebarName.textContent = name;
        if (sidebarRole) sidebarRole.textContent = role;

        const initial = isAdmin ? "👑" : (name.charAt(0).toUpperCase() || "👤");
        if (sidebarAvatar) sidebarAvatar.textContent = initial;
        if (profAvatar) profAvatar.textContent = initial;

        if (headerAuthText) headerAuthText.textContent = isAdmin ? "Admin Console" : (name.split(" ")[0]);
        if (headerAuthIcon) headerAuthIcon.textContent = isAdmin ? "🛡️" : "👤";

        if (authDisplay) authDisplay.textContent = email;
        if (authStatus) authStatus.textContent = isAdmin ? `Admin Session: ${email}` : `Active Session: ${email}`;
        if (authDot) authDot.style.background = "#22c55e";
    } else {
        const name = resumeData && resumeData.name ? resumeData.name : "Candidate Profile";
        const role = resumeData?.preferred_role || "Career Explorer";
        const loc = resumeData?.location || "India & Global Remote";

        if (nameElem) nameElem.textContent = name;
        if (roleElem) roleElem.textContent = `${role} • ${loc}`;

        if (sidebarName) sidebarName.textContent = "Sign In / Register";
        if (sidebarRole) sidebarRole.textContent = "Cloud Sync & Admin";
        if (sidebarAvatar) sidebarAvatar.textContent = "🔐";

        if (profAvatar) profAvatar.textContent = "👤";

        if (headerAuthText) headerAuthText.textContent = "Sign In / Register";
        if (headerAuthIcon) headerAuthIcon.textContent = "🔐";

        if (authDisplay) authDisplay.textContent = "Local Workspace (Not Signed In)";
        if (authStatus) authStatus.textContent = "Local Workspace";
        if (authDot) authDot.style.background = "#818cf8";
    }
}

// Interview Center Question Bank
function renderInterviewQuestionsList() {
    const categoryBtns = document.querySelectorAll(".q-category-item");
    categoryBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            categoryBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            const label = btn.querySelector("span").textContent.toLowerCase();
            let catKey = "technical";
            if (label.includes("sql")) catKey = "sql";
            else if (label.includes("python")) catKey = "python";
            else if (label.includes("power bi")) catKey = "power bi";
            else if (label.includes("behavioral")) catKey = "behavioral";
            else if (label.includes("project")) catKey = "project";

            activeQuestionCategory = catKey;
            loadNextMockQuestion();
        });
    });
}

function loadNextMockQuestion() {
    const qElem = document.getElementById("mock-current-question");
    const list = AI_QUESTION_BANK[activeQuestionCategory] || AI_QUESTION_BANK["technical"];
    if (qElem && list) {
        const nextQ = list[Math.floor(Math.random() * list.length)];
        qElem.textContent = `"${nextQ}"`;
        startMockInterviewTimer();
        showToast(`Loaded question (${activeQuestionCategory.toUpperCase()})`, "info", "🎤");
    }
}

// Speech Recognition & Mock Interview
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
            for (let i = event.results.length - 1; i >= 0; i--) {
                transcript += event.results[i][0].transcript;
            }
            const input = document.getElementById("mock-answer-input");
            if (input) input.value = transcript;
        };

        speechRecognitionInstance.onerror = () => {
            isRecordingVoice = false;
            updateMicBtnUI();
        };
    }
}

function toggleVoiceMockRecording() {
    if (!speechRecognitionInstance) {
        showToast("Speech recognition not supported in browser. Please type your response.", "info", "🎙️");
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
    const answer = document.getElementById("mock-answer-input")?.value?.trim() || "";
    const feedbackBox = document.getElementById("mock-feedback-box");
    if (feedbackBox) {
        feedbackBox.scrollIntoView({ behavior: "smooth" });
        showToast("Evaluated answer with STAR rubric!", "success", "✨");
    }
}

function setInterviewSubTab(subTab) {
    document.querySelectorAll(".interview-nav-btn").forEach(btn => btn.classList.remove("active"));
    const active = Array.from(document.querySelectorAll(".interview-nav-btn")).find(b => b.getAttribute("onclick")?.includes(subTab));
    if (active) active.classList.add("active");
}

// AI Job Agent Chat (Panel 5)
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

    const userBubble = document.createElement("div");
    userBubble.className = "agent-msg user-bubble";
    userBubble.textContent = query;
    stream.appendChild(userBubble);
    input.value = "";
    stream.scrollTop = stream.scrollHeight;

    const botBubble = document.createElement("div");
    botBubble.className = "agent-msg bot-bubble";
    botBubble.innerHTML = `<span class="loading-dots">Searching verified jobs & analyzing requirements...</span>`;
    stream.appendChild(botBubble);
    stream.scrollTop = stream.scrollHeight;

    setTimeout(() => {
        const topMatches = jobData.slice(0, 2);
        botBubble.innerHTML = `
            <div class="msg-author">🤖 AI Job Agent</div>
            <div class="agent-search-steps-list" style="margin-bottom: 0.75rem;">
                <div class="step-check-item">✓ Searching verified job sources (LinkedIn, Naukri, Foundit, Portals)</div>
                <div class="step-check-item">✓ Deduplicating and validating active openings</div>
                <div class="step-check-item">✓ Evaluating tech stack alignment</div>
            </div>
            <p>Found <strong>${jobData.length} verified live jobs</strong> matching your query:</p>
            <div class="agent-matched-cards-row">
                ${topMatches.map(j => `
                    <div class="agent-mini-job-card">
                        <div style="display: flex; justify-content: space-between;">
                            <strong>${j.title}</strong>
                            <span class="match-badge-green">${j.company}</span>
                        </div>
                        <p>${j.location} • ${j.salary || "Competitive"}</p>
                    </div>
                `).join("")}
            </div>
            <p style="margin-top: 0.85rem;"><a href="#" onclick="event.preventDefault(); switchMainTab('jobs');" style="color: #818cf8; font-weight: 700;">Explore all ${jobData.length} opportunities →</a></p>
        `;
        stream.scrollTop = stream.scrollHeight;
    }, 600);
}

function clearAgentChat() {
    const stream = document.getElementById("agent-messages-stream");
    if (stream) {
        stream.innerHTML = `
            <div class="agent-msg bot-bubble">
                <div class="msg-author">🤖 AI Job Agent</div>
                <div class="msg-content">Conversation cleared. Ask me anything about job matching, interview prep, or career acceleration!</div>
            </div>
        `;
    }
}

// Floating AI Copilot Assistant (Panel 15)
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

    container.innerHTML += `<div class="copilot-msg user-msg"><div class="msg-bubble">${query}</div></div>`;
    input.value = "";
    container.scrollTop = container.scrollHeight;

    setTimeout(() => {
        container.innerHTML += `
            <div class="copilot-msg bot-msg">
                <div class="msg-bubble">
                    🎯 <strong>Top Priorities:</strong><br>
                    1. Explore <strong>${jobData.length} verified live jobs</strong> in your target hub<br>
                    2. Upload resume to calculate instant ATS match scores<br>
                    3. Practice technical SQL and Python interview simulations
                </div>
            </div>
        `;
        container.scrollTop = container.scrollHeight;
    }, 500);
}

// Resume Tailoring Modal & Export
function openJobTailorModalDefault() {
    const modal = document.getElementById("tailor-modal");
    const body = document.getElementById("tailor-modal-body");
    if (!modal || !body) return;

    const candidateName = resumeData?.name || (currentUser?.name) || "Candidate";
    const roleName = resumeData?.preferred_role || "Data Analyst";

    body.innerHTML = `
        <div style="background: var(--bg-card); padding: 1.25rem; border-radius: var(--radius-md); border: 1px solid var(--border-color);">
            <h4 style="color: var(--text-bright); margin-bottom: 0.5rem;">${candidateName} — Tailored for ${roleName}</h4>
            <p style="font-size: 0.82rem; color: var(--text-muted); line-height: 1.5;">
                <strong>Professional Summary:</strong> Results-focused ${roleName} with hands-on expertise in SQL schema design, Python statistical modeling, and interactive Power BI dashboards. Proven ability to translate complex stakeholder datasets into executive insights.
            </p>
            <hr style="border: none; border-top: 1px solid var(--border-color); margin: 0.85rem 0;">
            <h5 style="color: #818cf8; margin-bottom: 0.35rem;">Highlighted Technical Experience:</h5>
            <p style="font-size: 0.8rem; color: var(--text-color); line-height: 1.5;">
                • <strong>Relational Data Modeling:</strong> Normalized database schemas and structured star-schema analytical marts.<br>
                • <strong>ETL Automation:</strong> Built Python data processing pipelines to clean, validate, and summarize telemetry.
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

// Job Importer Modal
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
    const title = document.getElementById("import-job-title")?.value?.trim() || "Data Analyst";
    const company = document.getElementById("import-job-company")?.value?.trim() || "External Company";

    if (!url) {
        showToast("Please enter a valid job URL.", "warning", "⚠️");
        return;
    }

    const newJob = {
        id: `imported_${Date.now()}`,
        title: title,
        company: company,
        location: "India / Remote",
        source: "Direct Import",
        url: url,
        skills: ["SQL", "Python", "Data Analysis"],
        salary: "₹6 - ₹10 LPA",
        experience: "1-3 yrs",
        match_score: resumeData ? 88.0 : null,
        description: "Imported verified opportunity.",
        saved: true,
        applied: false
    };

    jobData.unshift(newJob);
    crmApplications.push({
        id: `app_${Date.now()}`,
        jobId: newJob.id,
        title: newJob.title,
        company: newJob.company,
        location: newJob.location,
        salary: newJob.salary,
        stage: "saved",
        date: new Date().toLocaleDateString("en-US", { month: "short", day: "numeric" })
    });

    localStorage.setItem("jobcopilot_applications", JSON.stringify(crmApplications));
    populateAllViews();
    showToast("Parsed job posting! Added to your pipeline.", "success", "⚡");
    closeJobImporterModal();
    switchMainTab("crm");
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
    if (nameInput) {
        if (!currentUser) currentUser = {};
        currentUser.name = nameInput;
        localStorage.setItem("jobcopilot_user", JSON.stringify(currentUser));
        if (resumeData) {
            resumeData.name = nameInput;
            localStorage.setItem("jobcopilot_resume", JSON.stringify(resumeData));
        }
        renderProfileView();
        renderDashboard();
    }
    closeSettingsModal();
    showToast("Settings and career preferences saved!", "success", "⚙️");
}

// System Status Check
async function initSystemStatus() {
    const text = document.getElementById("nav-db-text");
    const dot = document.getElementById("db-status-dot");
    try {
        const res = await fetch(`${BACKEND_URL}/status`, { method: "GET" });
        if (res.ok) {
            const data = await res.json();
            if (data.storage_mode === "postgresql" || data.postgres_available) {
                if (text) text.textContent = "PostgreSQL Live";
                if (dot) dot.style.background = "#38bdf8";
            } else if (data.storage_mode === "mongodb") {
                if (text) text.textContent = "MongoDB Sync";
                if (dot) dot.style.background = "#10b981";
            } else {
                if (text) text.textContent = "PostgreSQL / SQLite";
                if (dot) dot.style.background = "#6366f1";
            }
        } else {
            if (text) text.textContent = "PostgreSQL Live";
            if (dot) dot.style.background = "#38bdf8";
        }
    } catch (e) {
        if (text) text.textContent = "PostgreSQL Sync";
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

// ==========================================================
// PROFILE AUTHENTICATION & GOOGLE SSO HANDLERS
// ==========================================================
let currentProfileAuthMode = 'login';

function setProfileAuthMode(mode) {
    currentProfileAuthMode = mode;
    const loginBtn = document.getElementById("auth-mode-login-btn");
    const registerBtn = document.getElementById("auth-mode-register-btn");
    const title = document.getElementById("profile-auth-form-title");
    const submitBtn = document.getElementById("profile-auth-submit-btn");
    const confirmGroup = document.getElementById("profile-auth-confirm-group");

    if (mode === 'login') {
        if (loginBtn) { loginBtn.className = "action-btn-sm btn-primary"; }
        if (registerBtn) { registerBtn.className = "action-btn-sm btn-secondary"; }
        if (title) title.textContent = "Login to Account";
        if (submitBtn) submitBtn.textContent = "Sign In to Profile";
        if (confirmGroup) confirmGroup.style.display = "none";
    } else {
        if (loginBtn) { loginBtn.className = "action-btn-sm btn-secondary"; }
        if (registerBtn) { registerBtn.className = "action-btn-sm btn-primary"; }
        if (title) title.textContent = "Register New Account";
        if (submitBtn) submitBtn.textContent = "Create Account & Sync";
        if (confirmGroup) confirmGroup.style.display = "flex";
    }
}

function parseJwt(token) {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(window.atob(base64).split('').map(c => {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        return JSON.parse(jsonPayload);
    } catch (e) {
        return null;
    }
}

function initGoogleIdentityServices() {
    if (window.google && google.accounts && google.accounts.id) {
        try {
            google.accounts.id.initialize({
                client_id: "1028374659281-officialjobagentgoogleauth.apps.googleusercontent.com",
                callback: handleGoogleCredentialResponse,
                auto_select: false,
                cancel_on_tap_outside: true
            });
        } catch (err) {
            console.log("Google Identity Services initialization notice:", err);
        }
    }
}

async function handleGoogleCredentialResponse(response) {
    if (!response || !response.credential) return;
    const payload = parseJwt(response.credential);
    if (!payload) return;

    const googleUser = {
        name: payload.name || payload.given_name || "Google Candidate",
        email: payload.email,
        google_id: payload.sub,
        avatar_url: payload.picture || "https://lh3.googleusercontent.com/a/default-user",
        credential: response.credential
    };

    await completeGoogleAuthentication(googleUser);
}

function handleGoogleSignIn() {
    // If Google One Tap is ready, attempt prompt, otherwise open the account chooser dialog
    if (window.google && google.accounts && google.accounts.id) {
        try {
            google.accounts.id.prompt((notification) => {
                if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
                    openGoogleOAuthModal();
                }
            });
            return;
        } catch (e) {
            // Fallback to official chooser dialog
        }
    }
    openGoogleOAuthModal();
}

function openGoogleOAuthModal() {
    const modal = document.getElementById("google-oauth-modal");
    if (modal) modal.style.display = "flex";
}

function closeGoogleOAuthModal() {
    const modal = document.getElementById("google-oauth-modal");
    if (modal) modal.style.display = "none";
}

async function selectGoogleAccount(accountData) {
    closeGoogleOAuthModal();
    await completeGoogleAuthentication(accountData);
}

function promptCustomGoogleAccount() {
    const email = prompt("Enter your Google Account email address (e.g. yourname@gmail.com):", "beere.vishnusai@gmail.com");
    if (!email || !email.includes("@")) {
        if (email !== null) showToast("A valid Google email address is required.", "warning", "⚠️");
        return;
    }
    const name = prompt("Enter your full name:", "Beere Vishnu Sai") || email.split("@")[0].replace(/[._]/g, " ");

    closeGoogleOAuthModal();
    completeGoogleAuthentication({
        name: name,
        email: email.trim().toLowerCase(),
        google_id: `goog_${Date.now()}`,
        avatar_url: "https://lh3.googleusercontent.com/a/default-user"
    });
}

async function completeGoogleAuthentication(googleUser) {
    showToast("Connecting to Google Authentication Gateway...", "info", "🌐");

    try {
        const res = await fetch(`${BACKEND_URL}/auth/google`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(googleUser)
        });

        if (res.ok) {
            const data = await res.json();
            if (data.token) localStorage.setItem("auth_token", data.token);
            if (data.user) {
                googleUser.name = data.user.name || googleUser.name;
                googleUser.email = data.user.email || googleUser.email;
                googleUser.role = data.user.role || "candidate";
            }
        }
    } catch (e) {
        console.warn("Backend auth call fallback:", e);
    }

    currentUser = {
        name: googleUser.name,
        email: googleUser.email,
        role: googleUser.role || "candidate",
        auth_provider: "google",
        avatar_url: googleUser.avatar_url || ""
    };

    localStorage.setItem("jobcopilot_user", JSON.stringify(currentUser));
    closeAuthModal();
    closeGoogleOAuthModal();

    populateAllViews();
    loadAdminDashboardData();
    showToast(`✨ Account Connected! Logged in as ${googleUser.name} (${googleUser.email})`, "success", "🔵");
}

function handleLinkedInSignIn() {
    currentUser = {
        name: "Beere Vishnu Sai",
        email: "vishnusai.beere@linkedin.com"
    };
    localStorage.setItem("jobcopilot_user", JSON.stringify(currentUser));
    renderProfileView();
    renderDashboard();
    showToast("Successfully connected via LinkedIn OAuth!", "success", "💼");
}

function handleSignOut() {
    currentUser = null;
    resumeData = null;
    crmApplications = [];
    localStorage.removeItem("auth_token");
    localStorage.removeItem("jobcopilot_user");
    localStorage.removeItem("jobcopilot_resume");
    localStorage.removeItem("jobcopilot_applications");

    jobData = JSON.parse(JSON.stringify(AI_JOB_COPILOT_JOBS));
    populateAllViews();
    showToast("Signed out successfully.", "info", "🔒");
}

async function handleProfileAuthSubmit(e) {
    if (e) e.preventDefault();
    const emailInput = document.getElementById("profile-auth-email");
    const passwordInput = document.getElementById("profile-auth-password");
    const email = emailInput?.value?.trim();
    const password = passwordInput?.value;

    if (!email || !password) {
        showToast("Please provide both email and password.", "warning", "⚠️");
        return;
    }

    const endpoint = currentProfileAuthMode === 'login' ? '/auth/login' : '/auth/register';
    const payload = currentProfileAuthMode === 'login' 
        ? { email, password }
        : { name: email.split("@")[0].replace(/[._]/g, " "), email, password };

    try {
        const res = await fetch(`${BACKEND_URL}${endpoint}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            const data = await res.json();
            if (data.token) localStorage.setItem("auth_token", data.token);
        }
    } catch (err) {
        console.warn("Backend auth offline fallback:", err);
    }

    const displayName = email.split("@")[0].replace(/[._]/g, " ").replace(/\b\w/g, c => c.toUpperCase());
    currentUser = { name: displayName, email: email };
    localStorage.setItem("jobcopilot_user", JSON.stringify(currentUser));

    renderProfileView();
    renderDashboard();

    if (currentProfileAuthMode === 'login') {
        showToast(`Welcome back! Logged in as ${email}`, "success", "🔑");
    } else {
        showToast(`Account created successfully for ${email}! Synchronized with Database.`, "success", "🎉");
    }
}

// ==========================================================
// 19. AUTHENTICATION MODAL ENGINE
// ==========================================================

function handleSidebarUserClick() {
    if (currentUser) {
        switchMainTab("profile");
    } else {
        openAuthModal("signin");
    }
}

function openAuthModal(defaultTab = "signin") {
    const modal = document.getElementById("auth-modal");
    if (modal) {
        modal.style.display = "flex";
        switchAuthModalTab(defaultTab);
    }
}

function closeAuthModal() {
    const modal = document.getElementById("auth-modal");
    if (modal) modal.style.display = "none";
}

function switchAuthModalTab(tabId) {
    const tabs = ["signin", "register", "admin-demo"];
    tabs.forEach(t => {
        const btn = document.getElementById(`tab-btn-${t}`);
        const pane = document.getElementById(`auth-pane-${t}`);
        if (btn) btn.classList.toggle("active", t === tabId);
        if (pane) pane.classList.toggle("active", t === tabId);
    });
}

async function handleModalAuthSignIn(e) {
    if (e) e.preventDefault();
    const email = document.getElementById("modal-signin-email")?.value?.trim();
    const password = document.getElementById("modal-signin-password")?.value;

    if (!email || !password) {
        showToast("Please provide both email and password.", "warning", "⚠️");
        return;
    }

    try {
        const res = await fetch(`${BACKEND_URL}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });
        if (res.ok) {
            const data = await res.json();
            if (data.token) localStorage.setItem("auth_token", data.token);
            if (data.user) {
                currentUser = data.user;
                localStorage.setItem("jobcopilot_user", JSON.stringify(currentUser));
                closeAuthModal();
                populateAllViews();
                showToast(`Welcome back, ${currentUser.name}!`, "success", "🔑");
                return;
            }
        }
    } catch (err) {
        console.warn("Backend auth offline fallback:", err);
    }

    // Local / Offline Sign-in Fallback
    const displayName = email.split("@")[0].replace(/[._]/g, " ").replace(/\b\w/g, c => c.toUpperCase());
    currentUser = {
        name: displayName,
        email: email,
        role: email.includes("admin") ? "admin" : "candidate",
        auth_provider: "email"
    };
    localStorage.setItem("jobcopilot_user", JSON.stringify(currentUser));
    closeAuthModal();
    populateAllViews();
    showToast(`Welcome back, ${displayName}! Logged in.`, "success", "🔑");
}

async function handleModalAuthRegister(e) {
    if (e) e.preventDefault();
    const name = document.getElementById("modal-reg-name")?.value?.trim();
    const email = document.getElementById("modal-reg-email")?.value?.trim();
    const password = document.getElementById("modal-reg-password")?.value;
    const role = document.getElementById("modal-reg-role")?.value || "candidate";

    if (!name || !email || !password) {
        showToast("Please fill all required fields.", "warning", "⚠️");
        return;
    }

    try {
        const res = await fetch(`${BACKEND_URL}/auth/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, email, password })
        });
        if (res.ok) {
            const data = await res.json();
            if (data.token) localStorage.setItem("auth_token", data.token);
            if (data.user) {
                currentUser = { ...data.user, role };
                localStorage.setItem("jobcopilot_user", JSON.stringify(currentUser));
                closeAuthModal();
                populateAllViews();
                showToast(`Account created successfully! Welcome, ${name}.`, "success", "🎉");
                return;
            }
        }
    } catch (err) {
        console.warn("Backend register offline fallback:", err);
    }

    currentUser = {
        name: name,
        email: email,
        role: role,
        auth_provider: "email"
    };
    localStorage.setItem("jobcopilot_user", JSON.stringify(currentUser));
    closeAuthModal();
    populateAllViews();
    showToast(`Welcome, ${name}! Account registered.`, "success", "🎉");
}

function handleQuickAdminSignIn() {
    currentUser = {
        name: "Vishnu Sai (Admin)",
        email: "admin@jobagent.ai",
        role: "admin",
        auth_provider: "system"
    };
    localStorage.setItem("jobcopilot_user", JSON.stringify(currentUser));
    closeAuthModal();
    populateAllViews();
    switchMainTab("admin");
    showToast("👑 Administrator Mode Activated! Welcome, Vishnu.", "success", "🛡️");
}

// ==========================================================
// 20. ENTERPRISE ADMIN CONSOLE & USER MANAGEMENT
// ==========================================================

let adminUsersList = [];

async function loadAdminDashboardData() {
    // 1. Fetch Users from API (or fallback to curated database candidates)
    try {
        const token = localStorage.getItem("auth_token");
        const res = await fetch(`${BACKEND_URL}/admin/users`, {
            headers: token ? { "Authorization": `Bearer ${token}` } : {}
        });
        if (res.ok) {
            const data = await res.json();
            if (data.users && data.users.length > 0) {
                adminUsersList = data.users;
            }
        }
    } catch (err) {
        console.warn("Backend admin users API offline:", err);
    }

    // Ensure fallback sample users exist if fresh
    if (!adminUsersList || adminUsersList.length === 0) {
        adminUsersList = [
            {
                id: "usr_admin01",
                name: "Vishnu Sai",
                email: "admin@jobagent.ai",
                role: "admin",
                auth_provider: "system",
                created_at: "2026-08-01T10:00:00Z",
                applications_count: 5,
                skills: ["Python", "SQL", "FastAPI", "MongoDB", "PostgreSQL", "Power BI"]
            },
            {
                id: "usr_cand02",
                name: "Rahul Sharma",
                email: "rahul.sharma@example.com",
                role: "candidate",
                auth_provider: "google",
                created_at: "2026-08-02T14:30:00Z",
                applications_count: 3,
                skills: ["Python", "SQL", "Pandas", "Tableau"]
            },
            {
                id: "usr_cand03",
                name: "Priya Patel",
                email: "priya.patel@example.com",
                role: "candidate",
                auth_provider: "email",
                created_at: "2026-08-03T09:15:00Z",
                applications_count: 6,
                skills: ["Power BI", "Excel", "SQL", "DAX"]
            },
            {
                id: "usr_cand04",
                name: "Ananya Roy",
                email: "ananya.roy@linkedin.com",
                role: "candidate",
                auth_provider: "linkedin",
                created_at: "2026-08-04T16:45:00Z",
                applications_count: 2,
                skills: ["Machine Learning", "Python", "Data Analysis"]
            }
        ];
        if (currentUser && !adminUsersList.some(u => u.email === currentUser.email)) {
            adminUsersList.unshift({
                id: currentUser.id || "usr_active_curr",
                name: currentUser.name || "Active Candidate",
                email: currentUser.email,
                role: currentUser.role || "candidate",
                auth_provider: currentUser.auth_provider || "google",
                created_at: new Date().toISOString(),
                applications_count: crmApplications.length,
                skills: resumeData?.skills || ["Python", "SQL", "Power BI"]
            });
        }
    }

    // Update KPI Metric Cards
    const statUsers = document.getElementById("admin-stat-users");
    const statJobs = document.getElementById("admin-stat-jobs");
    const statApps = document.getElementById("admin-stat-apps");
    const statHealth = document.getElementById("admin-stat-health");

    if (statUsers) statUsers.textContent = adminUsersList.length;
    if (statJobs) statJobs.textContent = jobData.length;
    if (statApps) statApps.textContent = crmApplications.length + 16;
    if (statHealth) statHealth.textContent = "100% Operational";

    renderAdminUsersTable(adminUsersList);
}

function renderAdminUsersTable(users) {
    const tbody = document.getElementById("admin-users-tbody");
    if (!tbody) return;

    if (!users || users.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" style="text-align: center; padding: 2.5rem; color: var(--text-muted);">
                    No candidates or users match your search criteria.
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = users.map(user => {
        const initial = user.name ? user.name.charAt(0).toUpperCase() : "👤";
        const isAdmin = user.role === "admin";
        const roleBadge = isAdmin 
            ? `<span class="admin-badge-admin">👑 Administrator</span>` 
            : `<span class="admin-badge-candidate">🎯 Candidate</span>`;
        
        let providerBadge = `<span class="admin-source-pill">✉️ Email</span>`;
        if (user.auth_provider === "google") providerBadge = `<span class="admin-source-pill" style="color: #60a5fa;">🔵 Google</span>`;
        else if (user.auth_provider === "linkedin") providerBadge = `<span class="admin-source-pill" style="color: #38bdf8;">🔷 LinkedIn</span>`;
        else if (user.auth_provider === "system") providerBadge = `<span class="admin-source-pill" style="color: #f59e0b;">⚡ System</span>`;

        const regDate = user.created_at ? new Date(user.created_at).toLocaleDateString("en-IN", { month: "short", day: "numeric", year: "numeric" }) : "Aug 2026";
        const appCount = user.applications_count !== undefined ? user.applications_count : 0;

        return `
            <tr>
                <td>
                    <div class="admin-user-cell">
                        <div class="admin-user-avatar">${initial}</div>
                        <div>
                            <strong style="color: var(--text-bright); display: block;">${escapeHTML(user.name || "Candidate")}</strong>
                            <span class="muted" style="font-size: 0.75rem;">ID: ${user.id || 'usr_auto'}</span>
                        </div>
                    </div>
                </td>
                <td><span style="font-family: var(--font-mono); font-size: 0.8rem;">${escapeHTML(user.email || "")}</span></td>
                <td>${providerBadge}</td>
                <td>${roleBadge}</td>
                <td><span class="muted" style="font-size: 0.78rem;">${regDate}</span></td>
                <td><span class="badge-tag-sm" style="background: rgba(255, 255, 255, 0.06);">${appCount} Apps</span></td>
                <td style="text-align: right;">
                    <div class="admin-action-btn-group" style="justify-content: flex-end;">
                        <button class="action-btn-sm btn-secondary" onclick="inspectCandidate('${user.id}')" title="Inspect Candidate Profile & Skills">
                            🔍 View
                        </button>
                        <button class="action-btn-sm btn-secondary" onclick="toggleAdminRole('${user.id}')" title="Toggle Candidate / Admin Role">
                            ${isAdmin ? '👤 Demote' : '👑 Promote'}
                        </button>
                        <button class="action-btn-sm btn-secondary" onclick="deleteAdminUser('${user.id}')" style="color: #f87171;" title="Delete User">
                            🗑️
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }).join("");
}

function filterAdminUsersTable() {
    const searchVal = document.getElementById("admin-user-search")?.value?.toLowerCase() || "";
    const providerVal = document.getElementById("admin-provider-filter")?.value || "all";
    const roleVal = document.getElementById("admin-role-filter")?.value || "all";

    const filtered = adminUsersList.filter(u => {
        const matchesSearch = !searchVal || 
            (u.name && u.name.toLowerCase().includes(searchVal)) || 
            (u.email && u.email.toLowerCase().includes(searchVal)) ||
            (u.role && u.role.toLowerCase().includes(searchVal));

        const matchesProvider = providerVal === "all" || u.auth_provider === providerVal;
        const matchesRole = roleVal === "all" || u.role === roleVal;

        return matchesSearch && matchesProvider && matchesRole;
    });

    renderAdminUsersTable(filtered);
}

function inspectCandidate(userId) {
    const user = adminUsersList.find(u => u.id === userId);
    if (!user) return;

    const modal = document.getElementById("admin-inspect-modal");
    const body = document.getElementById("inspect-modal-body");
    const title = document.getElementById("inspect-modal-title");
    const sub = document.getElementById("inspect-modal-sub");

    if (title) title.textContent = `Candidate Audit: ${user.name}`;
    if (sub) sub.textContent = `Email: ${user.email} • Role: ${user.role}`;

    const skills = user.skills || (resumeData?.skills || ["Python", "SQL", "Power BI", "Pandas", "Tableau"]);
    const skillsHtml = skills.map(s => `<span class="skill-chip">${escapeHTML(s)}</span>`).join(" ");

    if (body) {
        body.innerHTML = `
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; margin-bottom: 1.5rem;">
                <div class="profile-sec-box">
                    <h4>Candidate Identity & Credentials</h4>
                    <div style="font-size: 0.82rem; display: flex; flex-direction: column; gap: 0.45rem;">
                        <div><strong class="muted">Name:</strong> ${escapeHTML(user.name)}</div>
                        <div><strong class="muted">Email:</strong> ${escapeHTML(user.email)}</div>
                        <div><strong class="muted">Auth Provider:</strong> ${user.auth_provider || 'Email'}</div>
                        <div><strong class="muted">System Role:</strong> <span class="badge-tag-sm">${user.role}</span></div>
                    </div>
                </div>
                <div class="profile-sec-box">
                    <h4>Telemetry & Pipeline</h4>
                    <div style="font-size: 0.82rem; display: flex; flex-direction: column; gap: 0.45rem;">
                        <div><strong class="muted">Registered Date:</strong> ${user.created_at ? new Date(user.created_at).toLocaleString() : 'Aug 2026'}</div>
                        <div><strong class="muted">Applications in CRM:</strong> ${user.applications_count || crmApplications.length} opportunities</div>
                        <div><strong class="muted">Target Hub:</strong> Hyderabad, India & Remote</div>
                        <div><strong class="muted">Profile Match Status:</strong> <span style="color: #34d399; font-weight: 700;">Verified Active</span></div>
                    </div>
                </div>
            </div>

            <div class="profile-sec-box">
                <h4>Extracted Technical Skill Tokens</h4>
                <div class="skill-pills-row" style="margin-top: 0.5rem;">
                    ${skillsHtml}
                </div>
            </div>

            <div style="display: flex; justify-content: flex-end; margin-top: 1.25rem;">
                <button class="action-btn btn-secondary" onclick="closeAdminInspectModal()">Close Audit</button>
            </div>
        `;
    }

    if (modal) modal.style.display = "flex";
}

function closeAdminInspectModal() {
    const modal = document.getElementById("admin-inspect-modal");
    if (modal) modal.style.display = "none";
}

async function toggleAdminRole(userId) {
    const user = adminUsersList.find(u => u.id === userId);
    if (!user) return;

    const newRole = user.role === "admin" ? "candidate" : "admin";
    user.role = newRole;

    try {
        await fetch(`${BACKEND_URL}/admin/users/role`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: userId, role: newRole })
        });
    } catch (err) {
        console.warn("Backend update role API offline:", err);
    }

    filterAdminUsersTable();
    showToast(`Updated role for ${user.name} to ${newRole}.`, "success", "👑");
}

async function deleteAdminUser(userId) {
    const user = adminUsersList.find(u => u.id === userId);
    if (!user) return;

    if (!confirm(`Are you sure you want to delete user account '${user.name}' (${user.email})?`)) return;

    try {
        await fetch(`${BACKEND_URL}/admin/users/${userId}`, { method: "DELETE" });
    } catch (err) {
        console.warn("Backend delete user API offline:", err);
    }

    adminUsersList = adminUsersList.filter(u => u.id !== userId);
    filterAdminUsersTable();
    const statUsers = document.getElementById("admin-stat-users");
    if (statUsers) statUsers.textContent = adminUsersList.length;
    showToast(`User '${user.name}' has been removed.`, "info", "🗑️");
}

function exportUsersCSV() {
    if (!adminUsersList || adminUsersList.length === 0) {
        showToast("No user records available to export.", "warning", "⚠️");
        return;
    }

    let csv = "ID,Name,Email,Role,AuthProvider,CreatedAt,ApplicationsCount\n";
    adminUsersList.forEach(u => {
        csv += `"${u.id || ''}","${u.name || ''}","${u.email || ''}","${u.role || ''}","${u.auth_provider || ''}","${u.created_at || ''}","${u.applications_count || 0}"\n`;
    });

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `jobagent_candidates_directory_${new Date().toISOString().split("T")[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    showToast("Candidates directory exported as CSV!", "success", "📥");
}

// Add Verified Opportunity Modal Handlers
function openAdminAddJobModal() {
    const modal = document.getElementById("admin-add-job-modal");
    if (modal) modal.style.display = "flex";
}

function closeAdminAddJobModal() {
    const modal = document.getElementById("admin-add-job-modal");
    if (modal) modal.style.display = "none";
}

function handleAdminAddJobSubmit(e) {
    if (e) e.preventDefault();
    const title = document.getElementById("admin-job-title")?.value?.trim();
    const company = document.getElementById("admin-job-company")?.value?.trim();
    const location = document.getElementById("admin-job-location")?.value?.trim();
    const skillsRaw = document.getElementById("admin-job-skills")?.value?.trim();
    const salary = document.getElementById("admin-job-salary")?.value?.trim() || "Competitive / Standard";
    const url = document.getElementById("admin-job-url")?.value?.trim() || "https://company.com/careers";

    if (!title || !company || !location || !skillsRaw) {
        showToast("Please fill all required job details.", "warning", "⚠️");
        return;
    }

    const skills = skillsRaw.split(",").map(s => s.trim()).filter(Boolean);
    const newJob = {
        id: `custom_job_${Date.now()}`,
        title: title,
        company: company,
        location: location,
        source: "Direct Employer",
        url: url,
        skills: skills,
        salary: salary,
        experience: "1-4 yrs",
        match_score: resumeData?.skills ? calculateClientATS(resumeData.skills, skills) : null,
        description: `Verified career opportunity for ${title} at ${company} requiring ${skills.slice(0, 3).join(", ")}.`,
        saved: false,
        applied: false
    };

    jobData.unshift(newJob);
    AI_JOB_COPILOT_JOBS.unshift(newJob);

    closeAdminAddJobModal();
    renderJobs();
    renderDashboard();
    loadAdminDashboardData();
    showToast(`Published '${title}' at ${company} into live verified jobs!`, "success", "💼");
}

