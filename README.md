
---

# 🧠 Chat Summary Model

A project focused on building an AI-powered summarization model for chat dialogues. The goal is to generate concise, meaningful summaries from multi-turn conversations—useful for customer support logs, internal communication analysis, or chatbot reviews.

👉 **GitHub Repo**: [markolie20/Datalab-lectoraat](https://github.com/markolie20/Datalab-lectoraat/tree/develop)

---

## 📁 Project Structure

```
.
├── EDA/                     
│   ├── Dashboard.py             # Dashboard for visualizing chat patterns
│   └── EDA_Chatboxen.ipynb      # Notebook for exploratory data analysis
│
├── Data_generation/
│   ├── agent.py                 # Agent persona logic
│   ├── bio_generation.py        # User biography/context generation
│   ├── custom_expectations.py   # Domain-specific constraints/rules
│   └── group_generation.py      # Group conversation simulation
├── Testing/
│   ├── main.ipynb               # Main notebook where the training happends
└── README.md
```

---

## 🔍 Description

This project is focused on creating a summarization model specifically for **chatbox dialogues**. Because annotated datasets are limited, we use **Gemini** to generate high-quality synthetic chats, enriched with personas and context, to train and test our model on different pre-trained models.

---

## 🧪 Folder Overview

### `EDA/`
Exploratory Data Analysis tools:

- **`Dashboard.py`** — Interactive dashboard to visualize chat trends, message flows, and speaker stats.
- **`EDA_Chatboxen.ipynb`** — Jupyter notebook with data inspection, distributions, and summary previews.

### `Data_generation/`
Artificial data generation logic:

- **`agent.py`** — Defines behavior patterns for different conversational agents.
- **`bio_generation.py`** — Creates user bios to add realism and variety.
- **`custom_expectations.py`** — Adds custom constraints and logic for generating meaningful dialogue.
- **`group_generation.py`** — Combines all components to simulate multi-party chat scenarios.

### `Testing/`
Training the models on our data:
- **`main.ipynb`** — Prepering the data, training the models and evaluating them.
---


## 🚀 How to Use

1. **Clone the repo**:
   ```bash
   git clone https://github.com/markolie20/Datalab-lectoraat.git
   cd Datalab-lectoraat
   ```

2. **(Optional)** Create a virtual environment and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run data generation**:
   ```bash
   python Data_generation/group_generation.py
   ```

4. **Explore data** using:
   - `EDA/EDA_Chatboxen.ipynb` (Jupyter)
   - `EDA/Dashboard.py` (dashboard app)

5. **Training**: 
   - `Testing/main.ipynb` (Jupyter)
   - For all the trained models head to: https://dehaagsehogeschool-my.sharepoint.com/:u:/g/personal/22076719_student_hhs_nl/ETC6Isj35KFAsx11hD6xXRsBFJCQvxsWWmTuC-GhhGjjJg?e=IZbd0d Where you can download them. They are in total 16 gigabyte
---

## 🎯 Project Goals

- 💬 Build a summarizer for messy, multi-speaker dialogues
- 🧠 Train on synthetic, diverse, and realistic data
- ✨ Output clean, informative summaries with minimal hallucination

---

## 📄 License

This project is licensed under the **MIT License**.

---

 