# ADR 007 - Use Json Web Tokens (JWT)

Date: 20-05-2025

## Status

Accepted

## Context

For DexQuiz, we require a stateless and scalable authentication mechanism that integrates well with our FastAPI backend and RESTful architecture. Traditional session-based approaches would introduce server-side state and complicate horizontal scaling.

## Decision

**JSON Web Tokens (JWTs)** for authenticating and authorizing users. A token is issued upon successful login and must be included in the `Authorization` header of subsequent requests using the `Bearer` scheme.

## Alternatives Considered

- **Session-based authentication:** Would require managing server-side session state, making scaling and stateless design harder.
- **OAuth2 providers (e.g., Google, GitHub):** Overkill for the simplicity of this application.


## Consequences

- **Pros:**
  - Enables stateless and scalable API authentication.
  - Simple to implement and supported natively in FastAPI.
  - Well-documented and widely used standard.

- **Cons:**
  - JWTs must be securely signed and verified.
  - Token storage on the client must be secure (e.g., not accessible via JS to avoid XSS).