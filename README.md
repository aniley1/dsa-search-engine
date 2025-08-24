  🔍 DSA Search Engine

A   search engine for Data Structures & Algorithms problems  , built during the Hackathon 🚀.  
This project helps students, developers, and competitive programmers quickly find   relevant DSA problems   using intelligent search and similarity matching.

---

   ✨ Features
- ⚡   Fast Search  : Search problems by keywords (e.g., "dp", "graph", "greedy").
- 🏷️   Tag-based Filtering  : Results include problem tags for easy categorization.
- 📊   Similarity Ranking  : Results are ranked by semantic similarity score.
- 🎨   Attractive Frontend  : Clean, responsive UI built with React.
- 🐍   Backend with Python  : Efficient text processing and problem matching.

---

   🛠️ Tech Stack
-   Frontend:   React + Axios
-   Backend:   Python (FastAPI/Flask)
-   Data Processing:   TF-IDF, Cosine Similarity
-   Containerization:   Docker & Docker Compose (optional)

---

   🚀 Getting Started
1️⃣ Clone the repository
```bash
git clone https://github.com/aniley1/dsa-search-engine.git
cd dsa-search-engine
2️⃣ Backend Setup
# Create virtual environment
python -m venv venv
source venv/bin/activate   # (Linux/Mac)
venv\Scripts\activate      # (Windows)

# Install dependencies
pip install -r requirements.txt

# Start backend server
python app.py

By default, backend runs on http://127.0.0.1:8000

3️⃣ Frontend Setup
cd frontend
npm install
npm start

Frontend runs on http://localhost:3000

<img width="653" height="903" alt="image" src="https://github.com/user-attachments/assets/011019d7-0a28-4aed-92de-055543adb9b1" />
<img width="1126" height="278" alt="image" src="https://github.com/user-attachments/assets/24061e93-4f2e-4da7-9ceb-b3ed2c79a2d2" />


dsa-search-engine/
│── app.py              # Backend API
│── process.py          # Data preprocessing
│── problems.json       # Dataset of DSA problems
│── requirements.txt    # Backend dependencies
│── frontend/           # React frontend
│── docker-compose.yml  # Docker orchestration

🙌 Team & Contribution

Built by aniley1
 for Hackathon 2025 🎉.
Contributions and suggestions are welcome! Fork the repo and submit a PR.

⭐ Acknowledgement

Inspired by the need for better DSA problem discovery.
Thanks to open-source libraries: React, Axios, FastAPI, scikit-learn.
