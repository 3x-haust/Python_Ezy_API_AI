This is the English version of the README.  
[여기를 클릭하여 한국어 버전을 확인하세요.](./README-ko.md)

![Contributors](https://img.shields.io/github/contributors/3x-haust/Python_Ezy_API_AI?style=flat)
![Forks](https://img.shields.io/github/forks/3x-haust/Python_Ezy_API_AI?style=social?style=flat)
[![Stars](https://img.shields.io/github/stars/3x-haust/Python_Ezy_API_AI?style=flat&logo=GitHub&color=yellow)](https://github.com/3x-haust/Python_Ezy_API/stargazers)
![License](https://img.shields.io/github/license/3x-haust/Python_Ezy_API_AI?style=flat)

</br>

# Table of Contents

- [Table of Contents](#table-of-contents)
- [Contribution Guide](#contribution-guide)
  - [Create a Branch](#create-a-branch)
    - [Branch Naming Convention](#branch-naming-convention)
  - [Work and Commit](#work-and-commit)
    - [Commit Message Convention](#commit-message-convention)
    - [Commit Examples](#commit-examples)
  - [Push to Remote](#push-to-remote)
  - [Create a Pull Request (PR)](#create-a-pull-request-pr)
  - [Merge](#merge)
  
</br>
</br>
</br>

# Contribution Guide

Ezy API is open to contributions from everyone!  
Feel free to follow the steps below to participate.

## Create a Branch

When starting new work, please create a **branch**. Branches are usually named in the format `feature/{feature-name}`.

```bash
# Switch to the main branch and sync with the latest version
$ git checkout main
$ git pull origin main

# Create and switch to a new branch
$ git checkout -b feature/feature-name
```

### Branch Naming Convention

Name your branch according to the nature of your work.

| Type | Description | Example |
|:---:|:---|:---|
| `feature/` | New feature development | `feature/login-api`, `feature/add-user-api` |
| `fix/` | Bug fixes | `fix/login-bug`, `fix/routing-error` |
| `docs/` | Documentation (README, comments, etc.) | `docs/update-readme`, `docs/api-docs` |
| `refactor/` | Code refactoring | `refactor/login-service`, `refactor/db-helper` |
| `test/` | Adding or updating tests | `test/user-service-test` |
| `chore/` | Build settings, package management, miscellaneous tasks | `chore/update-deps`, `chore/ci-config` |

> **Tip**
> 
> Branch names should clearly indicate the purpose of the work.

## Work and Commit

After completing your work, write a commit message following the **commit convention** below.

### Commit Message Convention

| Tag | Description |
|:---:|:---|
| `feat` | Add a new feature |
| `fix` | Fix a bug |
| `docs` | Update documentation (README, comments, etc.) |
| `style` | Code formatting, typos, non-functional changes |
| `refactor` | Code refactoring (internal improvements without behavior change) |
| `test` | Add or update tests |
| `chore` | Build tasks, package manager configuration, maintenance work |

### Commit Examples
```bash
$ git commit -m "feat: add user API"
$ git commit -m "fix: fix incorrect router path"
$ git commit -m "docs: add installation guide to README"
```

## Push to Remote

Push your branch to the remote repository.

```bash
$ git push origin feature/feature-name
```

## Create a Pull Request (PR)

- Create a **Pull Request** on GitHub.
- Briefly describe what you worked on in the PR description.
- Then proceed with a code review with your team.

## Merge

- Once the review is complete and approved, **merge into the main branch**.
- After merging, always make sure to sync your local `main` branch before starting new work.

```bash
$ git checkout main
$ git pull origin main
```