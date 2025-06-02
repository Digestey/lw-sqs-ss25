# 9. Frontend-Backend Seperation

Date: 20.05.2025

## Status

Accepted

## Context

We want to maintain clean architecture between UI and API logic. ('Trennung von Struktur und Inhalt') This is performed in order to
increase the maintainability of the application and make the structure more clear.

## Decision

The frontend uses JavaScript or HTML forms to make requests to a clean API layer in FastAPI.

## Alternatives Considered

- Just keep everything as was in the poc-Phase. Not performed since its not a good look.

## Consequences

Better modularity and testability, at the cost of a slightly steeper learning curve.