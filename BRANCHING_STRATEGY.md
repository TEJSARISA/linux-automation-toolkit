# Git Branching Strategy & Version Control

## Overview

This project follows Git Flow branching strategy with protected branches and required status checks to ensure code quality and stable releases.

## Branch Types

### 1. Main Branch (`main`)
- **Purpose**: Production-ready code
- **Protection**: Yes
- **Requirements**:
  - All CI/CD checks must pass
  - Code review required
  - Pull request required
  - Linear history (no merge commits)
- **Deployment**: Automatic production deployment
- **Versioning**: Semantic version tags (v1.0.0)

### 2. Develop Branch (`develop`)
- **Purpose**: Integration branch for features
- **Protection**: Yes
- **Requirements**:
  - All CI/CD checks must pass
  - Code review required
  - Pull request required
- **Deployment**: Automatic staging deployment
- **Lifetime**: Long-lived

### 3. Feature Branches (`feature/*`)
- **Naming**: `feature/feature-name`
- **Created from**: `develop`
- **Merged back to**: `develop`
- **Lifetime**: Temporary (deleted after merge)
- **Examples**:
  - `feature/add-logging`
  - `feature/improve-performance`
  - `feature/fix-security-issue`

### 4. Release Branches (`release/*`)
- **Naming**: `release/v1.2.0`
- **Created from**: `develop`
- **Merged back to**: `main` and `develop`
- **Purpose**: Prepare production release
- **Duration**: Final testing and bug fixes
- **CI/CD**: Full pipeline execution

### 5. Hotfix Branches (`hotfix/*`)
- **Naming**: `hotfix/critical-bug-fix`
- **Created from**: `main`
- **Merged back to**: `main` and `develop`
- **Purpose**: Critical production fixes
- **Deployment**: Immediate to production

## Workflow Examples

### Starting a Feature

```bash
# Update develop branch
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/my-feature

# Make changes and commit
git add .
git commit -m "feat: add new functionality"

# Push to remote
git push origin feature/my-feature

# Create Pull Request on GitHub
```

### Feature to Main (via Pull Request)

1. Push feature branch
2. Create Pull Request from `feature/*` → `develop`
3. Wait for:
   - ✓ All CI/CD checks pass
   - ✓ Code review approval
   - ✓ Conversation resolution
4. Merge PR (GitHub will run post-merge checks)
5. Delete feature branch (automatic on merge)
6. CI/CD deploys to staging

### Release Process

```bash
# Create release branch
git checkout develop
git pull origin develop
git checkout -b release/v1.2.0

# Update version numbers if needed
# Make release-specific fixes

# Create PR: release/v1.2.0 → main
# After merge:
git checkout main
git pull origin main
git tag v1.2.0
git push origin v1.2.0

# Merge back to develop
git checkout develop
git pull origin develop
git merge --no-ff release/v1.2.0
git push origin develop
```

### Emergency Hotfix

```bash
# Create hotfix branch from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-fix

# Make critical fix
git commit -m "hotfix: resolve critical issue"

# Create PR: hotfix/* → main
# After merge to main:
# - Automatic deployment to production
# - GitHub Release created
# - Must also merge to develop
```

## Commit Message Guidelines

### Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation
- **style**: Code style changes
- **refactor**: Code refactoring
- **perf**: Performance improvements
- **test**: Tests
- **ci**: CI/CD changes
- **chore**: Build, dependencies

### Examples
```
feat(auth): add two-factor authentication

Implement TOTP-based 2FA for enhanced security.
Users can enable 2FA from account settings.

Fixes #123
```

```
fix(cli): resolve parsing error in args

The argument parser was throwing when encountering
empty strings. Now properly handles empty values.

Closes #456
```

## Pull Request Process

### Before Creating PR
1. Ensure branch is up-to-date: `git rebase origin/develop`
2. Run local tests: `pytest`
3. Check linting: `pylint **/*.py`
4. Verify no debug code or secrets

### PR Description Template
```markdown
## Description
Clear description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation

## Testing Done
Steps to test the changes

## Checklist
- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] No breaking changes
- [ ] Documentation updated
```

### After Creating PR
1. Wait for CI/CD checks
2. Respond to review comments
3. Push fixes (don't force-push in open PRs)
4. Request re-review after changes
5. Merge when approved

## Branch Protection Rules

### Main Branch
- ✓ Require pull request reviews (1)
- ✓ Require status checks to pass
- ✓ Dismiss stale PR approvals
- ✓ Require branches up to date
- ✓ Restrict pushes (only admins)

### Develop Branch
- ✓ Require pull request reviews (1)
- ✓ Require status checks to pass
- ✓ Dismiss stale PR approvals
- ✓ Require branches up to date

## Versioning (Semantic Versioning)

### Format: MAJOR.MINOR.PATCH

- **MAJOR**: Incompatible API changes
- **MINOR**: Backward-compatible features
- **PATCH**: Bug fixes

### Examples
- v1.0.0 - Initial release
- v1.1.0 - New features (backward compatible)
- v1.1.1 - Bug fix
- v2.0.0 - Breaking changes

## Status Checks (CI/CD)

All of these must pass before merge:
1. ✓ Build & Test (Python 3.9, 3.10, 3.11)
2. ✓ Security Scan (Trivy)
3. ✓ Code Coverage (Codecov)
4. ✓ Code Quality (Pylint, Black)

## FAQ

**Q: Can I push directly to main?**
A: No, main is protected. All changes require PR with approvals.

**Q: What if my PR conflicts with develop?**
A: Rebase locally: `git rebase origin/develop` and resolve conflicts.

**Q: How long should feature branches live?**
A: Days to weeks. Long-lived branches increase merge conflict risk.

**Q: Can I merge without all checks passing?**
A: No, branch protection requires all status checks to pass.

## Tools & Resources

- **GitHub CLI**: `gh pr create`, `gh pr status`
- **Git**: `git flow` (optional extension)
- **Documentation**: https://git-scm.com/book/en/v2
- **Conventional Commits**: https://www.conventionalcommits.org/
