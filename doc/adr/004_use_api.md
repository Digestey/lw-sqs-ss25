# 1. API to be used in order to get information about Pokémon

Date: 05-04-2025

## Status

Accepted

## Context

We need to get the information about the Pokémon the user has to guess. For that, we need to use an available Pokemon Lexicon.

## Decision

Use the [PokeAPI](https://pokeapi.co/) with the [pokebase](https://github.com/PokeAPI/pokebase) Python Wrapper

## Alternatives Considered

- Use the PokeAPI directly without wrapper
- Use a local Database with hand-made entries

## Consequences

- No need to implement a wrapper for the PokeAPI and the hassle that comes with it
- Dependence on the pokebase developers, less flexibility
- dependent on API
