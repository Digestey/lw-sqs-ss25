# ADR 000 – Use Python as the Primary Programming Language

## Status

Accepted

## Context

We need to choose a programming language for the backend of our quiz application. The language should allow for rapid development, have strong community support, and be suitable for a web-based application that includes features such as user authentication, database interaction, and data processing.

## Decision

We have decided to use **Python** as the primary programming language for the backend because:

- Python has a simple and readable syntax, which makes it ideal for educational projects and team collaboration.
- It offers a wide range of libraries and frameworks (e.g., FastAPI, SQLAlchemy, bcrypt) that support rapid development of modern web applications.
- FastAPI, a Python framework, allows for automatic generation of OpenAPI documentation and supports async features out of the box.
- Python is well-supported in Dockerized environments, making it easy to containerize and deploy.

## Alternatives consideres

- Typescript: Easy to set up, but I dont have much experience in testing typescript and getting it to run correctly on my hardware turned out to be frustrating
- Java: Probably to 'heavy' for my light application.
- C#: Lack of experience. Just no.

## Consequences

- All backend code will be written in Python.
- Team members need to have basic familiarity with Python or be willing to learn.
- Integration with external services or libraries will prioritize Python-based solutions where possible.
