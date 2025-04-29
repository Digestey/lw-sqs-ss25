# 1. Application environment/deployment

Date: 08-04-25

## Status

Accepted

## Context

In order to ensure the correct building and deployment of the application, it is considered whether to deploy the application "as-is" starting everything using python on
the host machine, or setting up an environment.

## Decision

Dockerize the application. Comes in handy since the MySQL-Database is also dockerized.

## Alternatives Considered

- Docker: industry standard, well documented
- Standalone: More control, easier to debug.

## Consequences

- The environment is now independent from the host system
- Adds docker configurations to ensure build
