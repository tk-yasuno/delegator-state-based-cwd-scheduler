# 🧠 Delegator v5.2.1 — State-Based Agentic CWD Scheduler

## 🏞 Background: Public Park Safety and Maintenance in Japan

Since 2018, annual inspections of playground equipment in public parks have been mandated across Japan. Park administrators (Coordinators) are responsible for monitoring the physical condition of over 1,000 playground units in more than 200 parks. Within limited budgets and increasing constraints on resources—such as rising material costs and labor shortages—they must plan and execute cost-efficient repair and replacement schedules to uphold safety.

Each year, Coordinators face bottlenecks in both budget allocation and field execution. Securing skilled maintenance crews (Workers) and managing construction priorities under fiscal and workforce limitations adds further complexity. As such, park management presents a classic **CWD (Coordinator, Worker, Delegator)** problem, requiring state-responsive planning that balances safety, feasibility, and public value.

To address this challenge, Delegators—AI agents tasked with long-term maintenance scheduling—must construct responsive plans based on inspection-informed degradation states. They aim to ensure sustainable safety levels while adapting to complex, large-scale, and uncertain infrastructure conditions.

In this context, we developed **Delegator v5.2.1**, a Minimum Viable Product built upon the **Agentic CWD framework**, leveraging real inspection data and parallelized state-based optimization. This system enables park administrators to generate cost-effective, safety-conscious schedules at scale.

---

## 🔍 Motivation
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
