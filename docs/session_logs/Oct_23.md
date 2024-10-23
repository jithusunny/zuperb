Worked on creating a plan that I can follow in the next few sessions. 
Decided to go with FastAPI + React + Postgres + DigitalOcean

## Context & Requirements
Build a Finance Tracker first as part of a broader "Zuperb" life assistant project.

 - Focus is on simplicity, keeping the development fast, minimal, and clean without unnecessary complexity.
 - Project should be accessible on multiple devices (laptop, tablet, phone, etc.) and potentially support feature phones and smartwatches in the future.
 - Aim to avoid vendor lock-in and favor cloud-agnostic setups that can scale easily, support multi-region availability, backups, and replication.
 - Prefer building step-by-step to ensure a deep understanding of the entire codebase.
 - Use the FastAPI Full-Stack Template for guidance but only add code I’ve written or understood, avoiding auto-generated parts.

## Considerations & Workflow
 - Start small, focusing on core features and gradually adding complexity.
 - Prioritize a fast-loading, minimal UI.
 - Plan for scaling and deployment flexibility in the future.
 - Use principles from the Pomodoro method for focused, time-bound development sessions.
 - Aim to complete the core finance tracker in a few sessions (2-5), making it basic but usable.

## Development Approach
 - Build from Scratch using FastAPI, React, and SQLModel, with PostgreSQL as the database.
 - Manual Code Understanding: Every piece of code in your repository will be something you've directly written or understood, leveraging the template as a guide.
 - Component-Based Frontend using React for simplicity and scalability.

## Project Workflow
- Step-by-Step Increments: Start with minimal backend functionality and then integrate with the frontend. Only add features after mastering the previous step.
- Use Docker for a simple, isolated development environment with PostgreSQL.
- Deploy incrementally to a cloud setup that supports easy future expansion without immediate complexity.

## Plan

1. Local Setup
  - Create FastAPI "Hello World".
  - Test locally.
  - Deploy Hello World

2. Containerize with Docker.
  - Deploy to cloud.
  - Google Authentication

3. Integrate "Continue with Google" auth using OAuth2.
  - Test locally.
  - Redeploy with Google Auth.
  - UI Setup

4. Build React login UI with "Continue with Google".
  - Connect to backend.
  - Deploy UI.
  - Transaction Model & CRUD

5. Define the Transaction model in SQLModel.
  - Implement CRUD APIs for transactions:
  - Create a new transaction.
  - Fetch transactions.
  - Update existing transactions.
  - Delete transactions.

6. Build Transaction UI
  - Create a UI for adding, viewing, updating, and deleting transactions.
  - Deploy updates.
  - Enhance & Automate

7. Integrate Docker Compose & GitHub Actions.
  - Automate CI/CD with tests and deployments.
