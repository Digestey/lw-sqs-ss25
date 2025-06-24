# ADR 008 - Form-based Authentication handling

Date: 20.05.2025

## Status

Considered

## Context

Using JS fetch to post login credentials created extra complexity in error handling and debugging.

## Decision

We considered moving logic to the backend (e.g., FastAPI forms), but chose to keep JS-based login for now.

## Alternatives Considered

Status Quo (JS-Based login handling)

## Consequences

Stays more flexible and API-like, but harder to debug than traditional form posts.