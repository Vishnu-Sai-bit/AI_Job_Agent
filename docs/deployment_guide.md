# 🚀 AI JobAgent Deployment Guide

This guide details how to deploy your AI JobAgent project as a live, public website on the internet for free.

---

## 📋 Architecture Overview
*   **Frontend**: Streamlit Community Cloud (Static Serverless Python Web Hosting)
*   **Backend**: Render (Python Web Service Host)
*   **LLM Database**: Google Gemini API (Serverless Cloud LLM Fallback)

---

## 🛠️ Step 1: Push Code to GitHub

1.  Open PowerShell in `C:\JobAgent` and run:
    ```powershell
    git init
    ```
2.  Create a `.gitignore` file in `C:\JobAgent` containing:
    ```text
    .env
    __pycache__/
    *.pyc
    uploads/
    temp/
    logs/
    reports/
    matched_jobs.md
    ```
3.  Commit your local files:
    ```powershell
    git add .
    git commit -m "Deploy-ready release of AI JobAgent"
    ```
4.  Go to [GitHub](https://github.com/) and create a new repository named `AI-JobAgent`.
5.  Link your local repository and push:
    ```powershell
    git remote add origin https://github.com/<your-username>/AI-JobAgent.git
    git branch -M main
    git push -u origin main
    ```

---

## ⚙️ Step 2: Deploy the FastAPI Backend to Render

1.  Create a free account at [Render.com](https://render.com/).
2.  Click **New +** at the top right and select **Web Service**.
3.  Connect your GitHub account and select your `AI-JobAgent` repository.
4.  Configure the Web Service:
    *   **Name**: `jobagent-backend`
    *   **Language**: `Python`
    *   **Branch**: `main`
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
    *   **Instance Type**: `Free`
5.  Open **Advanced** settings and add these **Environment Variables**:
    *   `GEMINI_API_KEY`: *(Your Google AI Studio API Key)*
    *   `SERPAPI_KEY`: *(Your SerpApi API Key)*
6.  Click **Deploy Web Service**.
7.  Once deployed, copy your live Render API URL from the dashboard (e.g., `https://jobagent-backend.onrender.com`).

---

## 🖥️ Step 3: Deploy the Streamlit Frontend

1.  Go to [Streamlit Community Cloud](https://share.streamlit.io/) and log in with GitHub.
2.  Click **New App** (or **Create App**).
3.  Configure your deployment settings:
    *   **Repository**: `<your-username>/AI-JobAgent`
    *   **Branch**: `main`
    *   **Main file path**: `frontend.py`
4.  Before clicking deploy, click the **Advanced settings** gear icon on the Streamlit screen.
5.  In the **Secrets** box, paste your backend URL configuration:
    ```toml
    BACKEND_URL = "https://jobagent-backend.onrender.com"
    ```
    *(Replace with your actual live Render URL)*
6.  Click **Save**, then click **Deploy**.

---

## 🎉 Step 4: Verification

Your site is now live! 
1.  Open the Streamlit app URL provided by Streamlit Cloud (e.g., `https://jobagent.streamlit.app`).
2.  Upload a resume.
3.  The frontend will send the file to your Render backend, run the analysis using the Gemini API, search live job boards, and load the dynamic reports instantly!
