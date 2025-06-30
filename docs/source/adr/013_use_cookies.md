# 013 - Use Cookies for authentication

Date: 23.05.2025

## Status

Accepted

## Context

The application uses JWT-based authentication as of now, tokens were stored in the browsers localStorage.
But to protect from possible XSS-Securtiy flaws and make the authentication be valid across sessions,
we need a better way to store the access tokens

## Decision

The decision was made to **switch to using cookies** (**HTTP-only** and **Secure** cookies) to store JWT tokens
for session management. These cookies wil automatically be sent for every request to the backend and marked as
HttpOnly to prevent JS access, mitigating XSS risks.

## Alternatives Considered

1. **Continue using local storage**: Simple to implement, but very overhead-y and vulerable
2. **Session-based authentication**: Probably the most secure way, but may be overkill for my application due to its complexity
3. **Cookies with JWT**: Stateless, Simple and secure

## Consequences

- The backend must support setting and readinc cookies.
- The application may be vulnerable to CSRF attacks. (Attempted mitigation thru "Samesite=Strict")
- Logging out will involve clearing cookies.
