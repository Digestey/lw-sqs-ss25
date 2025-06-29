.. _test-strategy:

Test Strategy
=============

DexQuiz implements a test strategy based on the test pyramid.

Overview
--------

+---------------------+-----------------------------+---------------------------------------------------------------+
| **Test Level**      | **Tools/Frameworks**        | **Scope/Focus**                                               |
+=====================+=============================+===============================================================+
| Unit Tests          | pytest, unittest.mock       | Core service functions (e.g., user auth, quiz logic)          |
+---------------------+-----------------------------+---------------------------------------------------------------+
| Integration Tests   | pytest, testcontainers      | Database access, JWT handling, service interactions           |
+---------------------+-----------------------------+---------------------------------------------------------------+
| End-to-End Tests    | Playwright                  | Full user flows: login, quiz interaction, score submission    |
+---------------------+-----------------------------+---------------------------------------------------------------+
| Security Tests      | Manual + scripted tests     | SQL injection attempts on login/highscore endpoints           |
+---------------------+-----------------------------+---------------------------------------------------------------+
| Static Analysis     | Codacy, pytest-cov          | Linting, duplication, code smells, coverage enforcement       |
+---------------------+-----------------------------+---------------------------------------------------------------+

Goals
-----

- Ensure correctness across isolated and integrated components.
- Validate security of exposed endpoints (e.g., SQLi).
- Achieve **>80% code coverage**, enforced via CI.
- Maintain test execution through **GitHub Actions CI**.
- Detect regressions early through fast unit + integration feedback.

Test Automation
---------------

All test stages are integrated into a GitHub Actions pipeline:

- Run on every commit (to the main and dev branches) and every pull request
- Generates coverage reports and Codacy annotations
- Flags failed tests, low coverage, or critical code issues
- overview generated on the codacy web UI

Limitations
-----------

- Load testing is currently omitted as per updated requirements.
- Security tests are limited to known vector checks (e.g., SQLi), without fuzzing or automated DAST tooling.
