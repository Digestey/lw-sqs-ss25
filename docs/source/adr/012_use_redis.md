# ADR 012 - Redis as game storage

Date: 26.05.2025

## Status

Accepted

## Context

We need a place to store things like the question and score temporarily. Until now the localStorage was used, but that
means that it can easily be tampered with. And I hate cheaters in multiplayer games.

## Decision

The decision was made to handle the score **server-side** using **Redis**. this way, the score cannot be tampered with
easily. Of course, in order to display the score, the actual value is still kept in the localStorage, but that cannot be
posted to the leaderboard anymore

## Alternatives Considered

- **keep the localStorage**: Would be easier and definetly work, but as stated in the context, I would really like to make
  tampering with the score non-trivial

- **use the exisiting MySQL database**: This would have been the go-to for me, just store it in a database. But in this case,
  the performance would suffer. 

## Consequences

- **Pros**:
  - Harder to tamper with scores
  - less client-side logic

- **Cons**:
  - Adds another dependency and therefore increased complexity
