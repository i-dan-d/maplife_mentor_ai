<div align="center">
  <h1>🌱 MAPLIFE - AI Personal Career Mentor</h1>
  <p><b>An intelligent, data-driven platform that helps young people build personalized career development roadmaps.</b></p>
  <p><i>Developed by Team 3 - Data for Impact 2026</i></p>
</div>

---

## 📋 Project Overview

In a world of information overload, over 75% of young professionals face career crises and lack clear direction. **MAPLIFE** is a web-based AI mentoring platform designed to solve this by acting as your **Personal AI Career Coach**. 

Instead of generic advice, MAPLIFE uses advanced Retrieval-Augmented Generation (RAG) and Vector Databases to combine your personal identity (CV, Personality) with real-world industry data (Reddit AMAs, Professional Books, Online Courses) to generate highly actionable career paths.

---

## 🗺️ User Workflow: How to use MAPLIFE

Getting started with MAPLIFE is a seamless, 4-step journey:

### 1️⃣ Step 1: Identity Initialization (Self-Discovery)
* **Upload CV:** Navigate to the `Hồ sơ CV` tab. The AI will extract your skills, strengths, and areas for improvement.
* **Personality Test:** Go to the `Tính cách` tab. Take the integrated Holland Code / Big Five assessment so the AI understands your work style.

### 2️⃣ Step 2: Multi-Source Career Mapping (Planning)
* **Set a Goal:** Head over to the `Lộ trình` (Roadmap) tab and enter your dream role (e.g., "Data Analyst in 1 Year").
* **AI Generation:** The system fetches real-world data (Courses, Books) via Vector Search and builds a phase-by-phase timeline tailored specifically to the skills you currently lack.

### 3️⃣ Step 3: Execution & Tracking (Action)
* **Track Progress:** Use the `Tiến độ` (Progress) tab to check off completed milestones.
* **Mental Health Tracking:** Along with tracking task completion, the system monitors your emotional state and stress levels to provide timely motivational support and help prevent burnout. 
* **Gamification:** Watch your progress bar fill up and earn motivational feedback from the system to stay on track.

### 4️⃣ Step 4: Continuous Mentoring & Networking (Support)
* **AI Mentor Chat:** Stuck on a task? Go to `AI Chat`. The AI already knows your CV, your roadmap, and your current progress. Ask it for interview tips or learning strategies.
* **Community Feed:** Jump into the `Cộng đồng` tab to share your achievements, ask for human advice, and upvote inspiring stories from peers.
* **Dynamic Social Matching:** The platform automatically groups you with users sharing similar personality traits (Holland/Big Five) and career goals, making it easy to find study buddies or professional connections.

---

## ✨ Key Features

- **💬 AI Mentor Chat**: Intelligent conversation based on your personal data and history
- **🧪 Personality Assessment**: Big Five, Holland Code, and custom tests
- **📄 CV Analyzer**: Upload CV and get job matching insights
- **🛤️ Dynamic Career Roadmap**: Build, visualize, and adjust your career path
- **📊 Progress & Gamification**: Track achievements, earn points, create Vision Board, and generate Year Wrap-up
- **🤝 Social Matching (Dynamic Clustering)**: Automatically group and connect users with similar personality traits (Holland/Big Five) and career goals using K-Means clustering.
- **💚 Sentiment Analysis**: Analyze users' emotional states in real-time during chat conversations to track mental well-being trends and provide proactive psychological support.
- **🔗 Networking**: Connect with mentors and peers

---

## 🛠 Technology Stack

* **Frontend:** [Streamlit](https://streamlit.io/) (Python)
* **Backend Logic:** Python 3.10+
* **Core AI Engine:** `gemini-2.5-flash-lite` (Logic) + `text-embedding-3-small` (Vectorization)
* **Database & Auth:** [Supabase](https://supabase.com/) (PostgreSQL)
* **Vector Search:** Supabase `pgvector` & Custom RPC Functions
* **Data Processing:** FAISS (Local Vector Search)

---

## 🚀 Getting Started (Installation Guide)

Follow these steps to run MAPLIFE on your local machine.

### 1. Prerequisites
* Python 3.10 or higher
* Git
* A Supabase Account (with your database and RLS policies configured)
* API Keys for OpenAI / Anthropic

### 2. Clone the Repository
```bash
git clone https://github.com/i-dan-d/maplife_mentor_ai
cd maplife_mentor_ai
pip install -r requirements.txt
streamlit run main.py or python -m streamlit run main.py
