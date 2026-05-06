# Phase Plan: Linting & Static Analysis

This phase focuses on ensuring the highest code quality standards by implementing comprehensive linting across all file types in the project.

## 1. Tools & Scope
We will implement the following industry-standard linters:
- **Python Source:** `ruff` (replaces flake8, isort, black) - handles formatting and linting.
- **Dockerfiles:** `hadolint` - ensures best practices for container security and efficiency.
- **YAML Files:** `yamllint` - validates GitHub Actions and other configuration files.
- **Markdown:** `pymarkdownlnt` - ensures documentation consistency.
- **Shell Scripts:** `shellcheck` - validates any bash/sh scripts.

## 2. Implementation Steps

### Step 1: Infrastructure Setup
- Create a `requirements-dev.txt` for development/linting tools.
- Configure `.ruff.toml` with project-specific rules (e.g., target version 3.11).
- Configure `.yamllint` configuration.

### Step 2: Source Code Refactoring
- Run `ruff format .` to standardize Python styling.
- Run `ruff check --fix .` to auto-resolve common linting errors.
- Manually resolve any remaining complex issues in Python, Docker, and YAML.

### Step 3: CI Integration
- Update `.github/workflows/test.yml` to include a `lint` job.
- This job must pass entirely before any code is considered "Ready".

## 3. Success Criteria
- [ ] `ruff check .` returns zero errors.
- [ ] `yamllint .` returns zero errors.
- [ ] `hadolint Dockerfile` returns zero errors.
- [ ] GitHub Actions "Lint" job is Green.

## 4. Timeline
This phase will be executed immediately following approval of this plan.
