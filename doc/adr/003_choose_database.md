# 1. Use MySQL as Database

Date: 2025-04-04

## Status

Accepted

## Context

An easy to use, commonly used SQL-based relational Database management system was needed in order to manage saving the highscores and for
user management. Ideally open-source.

## Decision

[MySQL](www.mysql.com) will be used.

## Alternatives Considered

- PostGresSQL: Similar Database.
- SQLite: Lightweight SQL Database.
- MongoDB: Document-based alternative to commonly used SQL Database.

## Consequences

- Less lightweight application than SQLite (SQLite does not need a seperate docker container)
- Risk of SQL-Injection attacks by using a SQL-Database
