# DexQuiz

Challenge your knowledge in the realm of Pokémon!  
Can you recognize Pokémon by their stats and Pokédex entries?  
**DexQuiz** is a web-based application that puts your knowledge to the test.

---

## 🧩 Description

DexQuiz is a full-stack quiz app built with FastAPI and MySQL. It presents users with hints about a Pokémon (such as base stats and Pokédex descriptions), and challenges them to guess the correct name. It includes a highscore table, viewable
and postable only when you are logged in.

---

## 🚀 Getting Started

### ✅ Dependencies

- Python 3.12+
- Docker (for local MySQL or test containers)
- `pip` (Python package manager)

### Configuration

The application expects a .env file in the folder. A sample .env-example file is provided.

### 🏃 Running DexQuiz

If you have at least docker installed, you should be good to go!

```bash
cp project/app/.env-example project/app/.env
docker compose -f project/app/docker-compose.yaml up --build
```

Then open [http://localhost:8000](http://localhost:8000) in your browser.

---

To stop the application, do

```bash
docker compose down -v
```

## 🧪 Testing

### Normal tests (basically everything except UI-Tests)

Run tests using `pytest`:

```bash
project/tests/pytest
```

This projects tests use [testcontainers](https://pypi.org/project/testcontainers/), ensure Docker is running beforehand.


### Playwright UI-Tests

The playwright tests are contained within the project/playwright folder. To run them follow these steps:

Start the application using the docker-compose file **for testing** or set the **USE_TEST_POKEMON** flag to 1 in the environment variables. Otherwise the quiz questions will be pulled directly from the PokeAPI and mess up the tests

```bash
docker compose -f project/app/docker-compose.test.yaml up --build
docker build -t playwright-tests .\project\playwright\
docker run --rm --network host playwright-tests  
```

## 📚 Documentation

Check out the full documentation for this project in [ReadTheDocs](https://lw-sqs-ss25.readthedocs.io/en/latest/)

### 🏗️ Architecture Decisions

See [`docs/source/adr`](docs/source/adr/) for ADRs (Architecture Decision Records).

### 🧱 System Design (arc42)

See [`docs/source/arc42`](docs/source/arc42) for arc42-based architectural documentation.

---

## ⚖️ License

This project is licensed under the GNU General License, for further information, see the included LICENSE file.
