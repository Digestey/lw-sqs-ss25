# ADR 012 - Use SQL parameterization

Date: 21.05.2025

## Status

Accepted

## Context

Databases are a vital part of this application. But since security is very important, we need to shield our database
from threats such as SQL Injection attacks. For this we should add some kind of mechanism.

## Decision

We decided to use **SQL-Parameterization** in order to implement such protection. everything variable to be added to a
SQL query shall be added as one string.

## Alternatives Considered

- **SQLAlchemy**: A full-featured ORM that includes parameterization and model abstraction.  
  Rejected due to added complexity and learning overhead for this small-scale application.

- **Manual query sanitization**: Too error-prone and easy to overlook; does not provide reliable protection.

## Consequences

- **Pros**:
  - Strong protection against SQL injection vulnerabilities.
  - Simple and readable SQL code using native `mysql.connector` parameterization.
  - Keeps implementation lightweight without an additional ORM layer.

- **Cons**:
  - Manual query construction still carries some risk if parameterization is not applied consistently.
  - Lacks advanced abstraction and migration tools that come with ORMs like SQLAlchemy.

