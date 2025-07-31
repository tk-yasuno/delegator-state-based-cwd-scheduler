# 🧠 Delegator v5.2.1 — State-Based Agentic CWD Scheduler

## Overview
**Delegator v5.2.1** is a state-based AI scheduler designed for infrastructure maintenance. It targets Japan’s public park CWD (Crack, Wear, Deformation) problem and generates repair and renewal plans based on inspection scores. It accounts for budget constraints and delay penalties while producing practical, prioritized maintenance schedules in seconds.

---

## 🔍 Background & Motivation
Since 2018, annual inspections have been mandatory for public parks in Japan. Municipalities must make complex maintenance decisions under limited budgets and human resources. This project implements an **Agentic Scheduling framework**, transforming inspection scores into actionable state-based decisions.

- Scope: 1,300+ playground units with CWD scores
- Challenges: Budget limits, repair delays, prioritization
- Solution: State-based scheduling + Streamlit UI

---

## ⚙️ Key Features

| Feature                         | Description                                                                 |
|--------------------------------|-----------------------------------------------------------------------------|
| State-Based Scheduling         | Extracts deterioration state from inspection scores to build repair schedules |
| Parallel Execution             | Supports up to 16-core processing via joblib                                 |
| Delay Penalty Evaluation       | Dynamically calculates penalties for late repairs                            |
| Streamlit UI                   | Visualizes schedules by cost, priority, and time                            |
| Utility Functions              | Budget handling, random split, priority scoring                             |

---

## 📊 Performance

- Dataset: 1,331 playground units
- Execution Time: 1.9 seconds (16-thread Core i9)
- Output: Budget-aware plans, priority-ranked list, lateness evaluation
- No GPU required (Pyomo + joblib-based)

---

## 🚀 How to Run

```bash
# Setup
pip install -r requirements.txt

# Launch UI
streamlit run streamlit_app.py
```

Input required: `inspectionList_sample.csv` (CWD-scored inspection data)

---

## 📁 Repository Structure

```
delegator-state-based-cwd-scheduler/
├── README.md
├── requirements.txt
├── data/
│   └── inspectionList_sample.csv
├── src/
│   ├── scheduler.py
│   ├── degradation_model.py
│   ├── utils.py
│   └── streamlit_app.py
├── docs/
│   └── model_diagram.png
├── LICENSE
└── .gitignore
```

---

## 📚 License & Citations

This project is released under the MIT License. Use cases related to municipalities or public infrastructure applications are warmly welcomed.

---

## 🌐 Contributor & Contact

This repository was designed and implemented by **Takato Yasuno**, an AI/ML engineer focused on scalable, socially responsive agentic systems for public safety. Ongoing development includes multimodal disaster monitoring and explainable infrastructure scheduling.

---
