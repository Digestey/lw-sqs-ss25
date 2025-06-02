# 7. Use Json Web Tokens

Date: 20-05-2025

## Status

Accepted

## Context

We need stateless authentication suitable for API-based interaction.

## Decision

We use JWTs to authorize users. Tokens are generated on login and passed with subsequent requests.

## Alternatives Considered

None

## Consequences

Easier to scale and stateless, but care must be taken to securely store and validate tokens.