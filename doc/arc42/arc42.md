# 

**About arc42**

arc42, the template for documentation of software and system
architecture.

Template Version 8.2 EN. (based upon AsciiDoc version), January 2023

Created, maintained and © by Dr. Peter Hruschka, Dr. Gernot Starke and
contributors. See <https://arc42.org>.

# Introduction and Goals

DexQuiz is an application that lets the user participate in a quiz about the different species of pokemon. Registered users will also have the opportunity to post and view the highest scores ever achieved.

## Requirements Overview

| Requirement | Description |
|-------------|-------------|
| 1           | The user can access the quiz even if he is not logged in |
| 2 | The user can register a new account with secure credentials |
| 3 | The user can log in using credentials entered during registration |
| 4 | The user can log out at any time using a button |
| 5 | The user can not access the highscores if he is not logged in |
| 6 | The user can view the highscore table if he is logged in |
| 7 | The user can participate in the quiz even if he is not logged in |
| 8 | The user can start the quiz when pressing a button |
| 9 | The user can make a guess using a text input |
| 10 | The user will receive feedback whether his guess was correct or not |
| 11 | If the guess was correct, a new question will be generated |
| 12 | If the guess was not correct, the user has the opportunity to give another answer |
| 13 | The highscore and user data will be stored using a database |

## Quality Goals

The quality of this project is assured using codacy.

The quality goals are set as follows:

- Minimum test coverage: **80%**, achieved by implementing the following types of tests:
    - Unit tests
    - Integration tests
    - API tests
    - e2e tests
    - load tests
- Maximum code duplication: **10%** (measures in SLoC, only code blocks are considered)
- Low code complexity
- Maximum **5 issues** (code smells) per 1000 SLoC

## Stakeholder

Theres only me who wants to pass this course and my professor who sets the requirements for this course.

# Architecture Constraints

DexQuiz shall be:

- platform-independent and be able to run on Windows, Linux and MacOS
- completely dockerized (including the database)
- executable by running a maximum of 2 terminal commands (excluding git clone operations)
- accessable using a chromium-based browser or Firefox (frontend only, backend is excluded from this)
- developed under a liberal license

# Context and Scope

## Business Context

**\<Diagram or Table>**

**\<optionally: Explanation of external domain interfaces>**

## Technical Context

**\<Diagram or Table>**

**\<optionally: Explanation of technical interfaces>**

**\<Mapping Input/Output to Channels>**

# Solution Strategy

# Building Block View

## Whitebox Overall System

***\<Overview Diagram>***

Motivation  
*\<text explanation>*

Contained Building Blocks  
*\<Description of contained building block (black boxes)>*

Important Interfaces  
*\<Description of important interfaces>*

### \<Name black box 1>

*\<Purpose/Responsibility>*

*\<Interface(s)>*

*\<(Optional) Quality/Performance Characteristics>*

*\<(Optional) Directory/File Location>*

*\<(Optional) Fulfilled Requirements>*

*\<(optional) Open Issues/Problems/Risks>*

### \<Name black box 2>

*\<black box template>*

### \<Name black box n>

*\<black box template>*

### \<Name interface 1>

…

### \<Name interface m>

## Level 2

### White Box *\<building block 1>*

*\<white box template>*

### White Box *\<building block 2>*

*\<white box template>*

…

### White Box *\<building block m>*

*\<white box template>*

## Level 3

### White Box \<\_building block x.1\_\>

*\<white box template>*

### White Box \<\_building block x.2\_\>

*\<white box template>*

### White Box \<\_building block y.1\_\>

*\<white box template>*

# Runtime View

## \<Runtime Scenario 1>

-   *\<insert runtime diagram or textual description of the scenario>*

-   *\<insert description of the notable aspects of the interactions
    between the building block instances depicted in this diagram.>*

## \<Runtime Scenario 2>

## …

## \<Runtime Scenario n>

# Deployment View

## Infrastructure Level 1

***\<Overview Diagram>***

Motivation  
*\<explanation in text form>*

Quality and/or Performance Features  
*\<explanation in text form>*

Mapping of Building Blocks to Infrastructure  
*\<description of the mapping>*

## Infrastructure Level 2

### *\<Infrastructure Element 1>*

*\<diagram + explanation>*

### *\<Infrastructure Element 2>*

*\<diagram + explanation>*

…

### *\<Infrastructure Element n>*

*\<diagram + explanation>*

# Cross-cutting Concepts

## *\<Concept 1>*

*\<explanation>*

## *\<Concept 2>*

*\<explanation>*

…

## *\<Concept n>*

*\<explanation>*

# Architecture Decisions

# Quality Requirements

## Quality Tree

## Quality Scenarios

# Risks and Technical Debts

# Glossary

| Term        | Definition        |
|-------------|-------------------|
| *\<Term-1>* | *\<definition-1>* |
| *\<Term-2>* | *\<definition-2>* |
