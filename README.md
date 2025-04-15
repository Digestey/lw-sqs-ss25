# DexQuiz

Challenge your knowledge in the realm of Pokémon!  
Can you recognize Pokémon by their stats and Pokédex entries?  
**DexQuiz** is a web-based application that puts your knowledge to the test.

---

## 🧩 Description

DexQuiz is a full-stack quiz app built with FastAPI and MySQL. It presents users with hints about a Pokémon (such as base stats and Pokédex descriptions), and challenges them to guess the correct name.

---

## 🚀 Getting Started

### ✅ Dependencies

- Python 3.10+
- Docker (for local MySQL or test containers)
- `pip` (Python package manager)

### 📦 Installation

```bash
git clone https://github.com/your-username/dexquiz.git
cd dexquiz
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 🏃 Running DexQuiz

```bash
uvicorn project.main:app --reload
```

Then open [http://localhost:8000](http://localhost:8000) in your browser.

---

## 🧪 Testing

Run tests using `pytest`:

```bash
pytest
```

If you’re using [testcontainers](https://pypi.org/project/testcontainers/), ensure Docker is running beforehand.


## 📚 Documentation

### 🏗️ Architecture Decisions

See [`doc/adr`](doc/adr) for ADRs (Architecture Decision Records).

### 🧱 System Design (arc42)

See [`doc/arc42`](doc/arc42) for arc42-based architectural documentation.

---

## ⚖️ License

This project uses the MIT License (see [`LICENSE`](LICENSE)).

Make sure to review licenses of dependencies used in this project (e.g., by using `pip-licenses`).
