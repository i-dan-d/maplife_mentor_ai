# MAPLIFE - AI Personal Career Mentor

**An intelligent platform that helps young people build personalized career development roadmaps**

---

## 📋 Project Overview

**MAPLIFE** is a web-based AI mentoring platform designed to support young people (especially students and fresh graduates) in navigating their personal and career development journey.

Acting as a **personal AI mentor**, MAPLIFE uses advanced AI and data-driven approaches to:

- Analyze user's personality, goals, and behaviors
- Generate clear, personalized career roadmaps
- Recommend suitable actions, courses, and resources
- Track progress with gamification and work-life balance features
- Connect users with mentors and like-minded community

---

## ✨ Key Features

- **💬 AI Mentor Chat**: Intelligent conversation based on your personal data and history
- **🧪 Personality Assessment**: Big Five, Holland Code, and custom tests
- **📄 CV Analyzer**: Upload CV and get job matching insights
- **🛤️ Dynamic Career Roadmap**: Build, visualize, and adjust your career path
- **📊 Progress & Gamification**: Track achievements, earn points, create Vision Board, and generate Year Wrap-up
- **🔗 Networking**: Connect with mentors and peers

---

## 🛠 Technology Stack

- **Frontend**: Streamlit
- **Backend**: Python (Vanilla)
- **LLM & Embedding**: OpenAI (`gpt-4o-mini` + `text-embedding-3-small`)
- **Vector Database**: Supabase (pgvector)
- **Local Vector Search**: FAISS
- **Structured Database**: Supabase PostgreSQL

---

## 🚀 How to Run the Project

### 1. Clone the repository
```bash
git clone https://github.com/i-dan-d/maplife_mentor_ai
cd maplife_mentor_ai
streamlit run main.py
