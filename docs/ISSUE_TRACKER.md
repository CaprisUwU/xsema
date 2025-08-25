# Issue Tracker

This document tracks all issues encountered during development, their resolutions, and any workarounds implemented.

## Issue Log

| ID | Date       | Status  | Component | Description | Resolution |
|----|------------|---------|-----------|-------------|------------|
| 1  | 2025-08-01 | Resolved | Environment | Missing 'backoff' dependency | Added to requirements.txt and installed in virtual environment |
| 2  | 2025-08-01 | Resolved | Web3 | ImportError: cannot import name 'geth_poa_middleware' | Updated to use 'ExtraDataToPOAMiddleware' for web3.py 5.31.1 compatibility |
| 3  | 2025-08-01 | Resolved | Services | Circular import issues | Restructured imports in services layer to use package-level imports |
| 4  | 2025-08-01 | Resolved | Testing | Port conflicts (8000 in use) | Standardized on port 8000 for all environments |
| 5  | 2025-08-01 | Resolved | API | Duplicate parameter bug in routers | Removed redundant path parameters from endpoint decorators |
| 6  | 2025-08-01 | Resolved | Environment | Unicode encoding issues in Windows | Implemented safe_print function and removed emoji/Unicode characters from console output |
| 7  | 2025-08-01 | Open    | Testing | Inconsistent test discovery | Investigating pytest configuration and sys.path issues |
| 8  | 2025-08-11 | Open    | Testing | pytest-asyncio configuration warning | Need to set asyncio_default_fixture_loop_scope in pytest.ini |
| 9  | 2025-08-11 | Open    | Testing | Test failures in wallet clustering tests | Multiple test failures due to missing job_store attribute and incorrect function signatures |
| 10 | 2025-08-11 | Open    | Dependencies | Pydantic V2 deprecation warnings | Need to migrate from @validator to @field_validator and update deprecated config patterns |
| 11 | 2025-08-11 | Open    | Dependencies | FastAPI on_event deprecation warnings | Need to migrate from @app.on_event to lifespan event handlers |
| 12 | 2025-08-11 | Open    | Dependencies | datetime.utcnow() deprecation warnings | Need to replace with datetime.now(datetime.UTC) |

## Active Issues

### 7. Inconsistent Test Discovery
- **Status**: Investigating
- **Component**: Testing
- **Description**: Some integration tests are not being discovered or run by pytest
- **Impact**: Incomplete test coverage
- **Next Steps**:
  - [ ] Review pytest.ini configuration
  - [ ] Check PYTHONPATH and sys.path in test environment
  - [ ] Verify test file naming conventions

### 8. pytest-asyncio Configuration Warning
- **Status**: Open
- **Component**: Testing
- **Description**: Warning about asyncio_default_fixture_loop_scope being unset
- **Impact**: Future pytest-asyncio versions may have unexpected behavior
- **Next Steps**:
  - [ ] Add asyncio_default_fixture_loop_scope to pytest.ini
  - [ ] Set appropriate scope (function, class, module, package, or session)

### 9. Wallet Clustering Test Failures
- **Status**: Open
- **Component**: Testing
- **Description**: Multiple test failures in wallet clustering unit tests
- **Impact**: Test suite not passing, potential code quality issues
- **Next Steps**:
  - [ ] Investigate missing job_store attribute in wallets.py
  - [ ] Fix function signature mismatches in rate_limit_check
  - [ ] Review test mocking strategy

### 10. Pydantic V2 Deprecation Warnings
- **Status**: Open
- **Component**: Dependencies
- **Description**: Multiple Pydantic V1 style validators and config patterns deprecated
- **Impact**: Future compatibility issues, warnings in logs
- **Next Steps**:
  - [ ] Migrate @validator to @field_validator
  - [ ] Update deprecated config patterns
  - [ ] Replace json_encoders with custom serializers

### 11. FastAPI on_event Deprecation Warnings
- **Status**: Open
- **Component**: Dependencies
- **Description**: @app.on_event decorators are deprecated in favor of lifespan event handlers
- **Impact**: Future FastAPI versions may remove on_event support
- **Next Steps**:
  - [ ] Migrate startup and shutdown events to lifespan handlers
  - [ ] Update portfolio/main.py and other affected files

### 12. datetime.utcnow() Deprecation Warnings
- **Status**: Open
- **Component**: Dependencies
- **Description**: datetime.utcnow() is deprecated in favor of timezone-aware alternatives
- **Impact**: Future Python versions may remove utcnow() support
- **Next Steps**:
  - [ ] Replace datetime.utcnow() with datetime.now(datetime.UTC)
  - [ ] Update portfolio/models/user.py and other affected files

## Resolution Guidelines

When resolving issues, please follow these steps:

1. Document the issue with clear reproduction steps
2. Assign a unique ID and date
3. Update status as work progresses
4. Document the resolution and any relevant code changes
5. Reference any related pull requests or commits
6. Add any new test cases to prevent regression

## Issue Template

```markdown
### [ID]. [Brief Description]
- **Status**: [Open/In Progress/Resolved]
- **Component**: [e.g., API, Database, Frontend]
- **Description**: 
  [Detailed description of the issue]
- **Impact**:
  [How does this affect the system/users?]
- **Reproduction Steps**:
  1. [Step 1]
  2. [Step 2]
  3. [Step 3]
- **Expected Behavior**:
  [What should happen]
- **Actual Behavior**:
  [What actually happens]
- **Resolution**:
  [How was the issue resolved]
- **Related PRs/Commits**:
  - [PR/Commit reference]
```

## Automated Issue Tracking

To help automate issue tracking, you can use the following git hook to generate issue templates when creating new branches:

```bash
#!/bin/bash
# .git/hooks/prepare-commit-msg

# Get the current branch name
BRANCH_NAME=$(git symbolic-ref --short HEAD)

# Check if branch name starts with 'issue-'
if [[ $BRANCH_NAME == issue-* ]]; then
    # Extract issue number from branch name
    ISSUE_NUMBER=${BRANCH_NAME#issue-}
    
    # Create a template commit message
    echo "Fix #$ISSUE_NUMBER: [Brief description of changes]" > "$1"
    echo "" >> "$1"
    echo "- Resolves issue #$ISSUE_NUMBER" >> "$1"
    echo "- [ ] Tests added/updated" >> "$1"
    echo "- [ ] Documentation updated" >> "$1"
    echo "- [ ] All tests pass" >> "$1"
fi
```

## Monitoring

For automated issue tracking and monitoring, consider integrating with:
- GitHub Issues
- JIRA
- Sentry (for runtime errors)
- Prometheus/Grafana (for system metrics)

## Roadmap Alignment

This issue tracker should be cross-referenced with the [ROADMAP.md](./ROADMAP.md) to ensure all planned features and fixes are properly tracked and prioritized.
