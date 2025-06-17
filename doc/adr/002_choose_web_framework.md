# 1. Use FastAPI for Web Backend

Date: 2025-03-28

## Status

Accepted

## Context

In search of a modern and capable python web framework that has well-enough developer support and provides automatic documentation. Another point is the
simplicity to create a REST-API for the DexQuiz application.

## Decision

[FastAPI](https://fastapi.tiangolo.com/) will be used instead of Flask or Django.

## Alternatives Considered

- Flask: Familiar but sync by default, lacks type hints.
- Django: Heavy for our simple project.

## Consequences

- FastAPI allows async endpoints, auto-generates docs, and improves performance.
- Slightly newer, so some ecosystem parts may be less mature, potential lack of support
