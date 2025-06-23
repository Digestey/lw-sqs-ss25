# ADR 010 - Database for testing

Date: 06.06.2025

## Status

Accepted

## Context

Testing the database portion of the DexQuiz application requires a database for testing purposes.
For simple unit tests, these are mocked but for any further testing a proper database should be provided.

## Decision

The decision was made to use the testcontainers framework which provides on the fly containers running desired apps.

## Alternatives Considered

- test docker container: using a seperate  docker compose for testing the project. Rejected because it would be 
    a lot more difficult to execute during pipelines and requires way more configuration for the same work that 
    the testcontainers framework provides

## Consequences

The tests are run using a MySQL testcontainer.