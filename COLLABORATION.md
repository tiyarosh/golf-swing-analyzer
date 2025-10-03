# Team Collaboration Guide

This guide outlines our team workflow, best practices, and repository setup for the Golf Swing Analyzer project.

## 📋 Table of Contents

- [Repository Setup](#repository-setup)
- [Access Control](#access-control)
- [Branch Strategy](#branch-strategy)
- [Development Workflow](#development-workflow)
- [Code Review Process](#code-review-process)
- [Communication](#communication)
- [Task Management](#task-management)
- [Meeting Schedule](#meeting-schedule)

---

## Repository Setup

## Branch Strategy

We use **Git Flow** (simplified for student project):

```
main (production)
  ↓
develop (integration)
  ↓
feature/* (individual work)
```

### Branch Types

1. **`main`** - Production-ready code

   - Only merge from `develop` via PR
   - Tagged releases (v0.1.0, v0.2.0, etc.)
   - Used for final project submission

2. **`develop`** - Integration branch

   - Default branch for PRs
   - Where features are integrated
   - Should always be stable enough to demo

3. **`feature/*`** - Feature development

   - Created from `develop`
   - Naming: `feature/descriptive-name`
   - Examples:
     - `feature/early-extension-analyzer`
     - `feature/streamlit-ui`
     - `feature/video-processing`

4. **`fix/*`** - Bug fixes

   - Created from `develop` (or `main` if hotfix)
   - Naming: `fix/issue-description`
   - Example: `fix/pose-detection-crash`

5. **`docs/*`** - Documentation only
   - Example: `docs/api-reference`

### Branch Naming Rules

- Use lowercase
- Use hyphens, not underscores
- Be descriptive but concise
- Include issue number if applicable: `feature/23-add-swing-segmenter`

---

## Development Workflow

### Starting New Work

```bash
# 1. Update local develop branch
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/your-feature-name

# 3. Make changes and commit regularly
git add .
git commit -m "feat(analyzer): implement early extension detection"

# 4. Push to remote (creates remote branch)
git push -u origin feature/your-feature-name
```

### Keeping Your Branch Updated

```bash
# Option 1: Rebase (preferred - cleaner history)
git fetch origin
git rebase origin/develop

# If conflicts occur:
# 1. Resolve conflicts in files
# 2. git add <resolved-files>
# 3. git rebase --continue

# Option 2: Merge (easier but messier history)
git fetch origin
git merge origin/develop
```

### Committing Changes

**Commit Message Format:**

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**

```bash
git commit -m "feat(segmenter): add swing phase detection algorithm"

git commit -m "fix(pose): handle missing landmarks gracefully"

git commit -m "docs(readme): add installation instructions"

git commit -m "test(analyzer): add unit tests for early extension"
```

### Creating Pull Requests

1. **Push your feature branch**

   ```bash
   git push origin feature/your-feature-name
   ```

2. **Open PR on GitHub**

   - Base: `develop` ← Compare: `feature/your-feature-name`
   - Title: Clear, descriptive (same as commit message)
   - Description: Use the template (see below)
   - Assign reviewers: At least one team member
   - Link issues: "Closes #123" or "Relates to #456"

3. **PR Description Template:**

   ```markdown
   ## Description

   Brief description of changes

   ## Type of Change

   - [ ] Bug fix
   - [ ] New feature
   - [ ] Documentation update
   - [ ] Refactoring

   ## Testing

   - [ ] Unit tests added/updated
   - [ ] Manual testing completed
   - [ ] All tests passing

   ## Screenshots/Demo (if applicable)

   ## Checklist

   - [ ] Code follows style guidelines
   - [ ] Documentation updated
   - [ ] No new warnings
   - [ ] Tested on sample videos
   ```

---

## Code Review Process

### For Authors

1. **Before requesting review:**

   - All tests pass locally
   - Code is properly formatted (`black`)
   - No linting errors (`flake8`)
   - Documentation updated
   - Self-review completed

2. **Request review:**

   - Assign at least 1 reviewer
   - Add relevant labels
   - Link to related issues

3. **Address feedback:**
   - Respond to all comments
   - Push updates to same branch
   - Re-request review when ready

### For Reviewers

**Review within 24 hours** (or communicate delays)

**What to check:**

- Code works as described
- Tests are adequate
- No obvious bugs or edge cases missed
- Code is readable and maintainable
- Follows project conventions
- Documentation is clear

**How to review:**

- Use GitHub's review features
- Be constructive and specific
- Suggest improvements, don't just criticize
- Approve when satisfied, or request changes

**Review comments:**

- Use "Comment" for questions/suggestions
- Use "Request changes" for required fixes
- Use "Approve" when ready to merge

### Merging

**Who can merge:**

- Any team member once PR is approved
- Use "Squash and merge" for clean history

**Before merging:**

1. All reviewers have approved
2. All CI checks pass (when implemented)
3. Branch is up-to-date with develop
4. No unresolved conversations

---

## Communication

### Daily Standups (Async)

Post daily in team chat by 12 PM:

1. What I completed yesterday
2. What I'm working on today
3. Any blockers or questions

### Communication Channels

**Slack - For:**

- Daily updates
- Quick questions
- Coordination
- Informal discussion

**Email - For:**

- Professor communications
- Formal coordination
- Scheduling

### Response Time Expectations

- **Urgent** (blocking work): < 2 hours
- **High priority**: Same day
- **Normal**: Within 24 hours
- **Low priority**: Within 48 hours

---

## Task Management

## Meeting Schedule

### Weekly Team Meetings

**Monday (25 min) - Sprint Planning**

- Review progress
- Plan upcoming week
- Assign tasks
- Discuss blockers

**Wednesday (25 min) - Mid-Sprint Check-in**

- Progress updates
- Resolve blockers
- Adjust timeline if needed

**Friday (50 min) - Code Review Session**

- Review open PRs together
- Discuss technical decisions
- Plan integration testing

### Ad-hoc Meetings

Schedule as needed for:

- Pair programming
- Debugging sessions
- Design discussions
- Demo preparation

---

## Academic Considerations

### Course Requirements

Track alignment with objectives:

- [ ] Literature review completed
- [ ] Real-world problem articulated
- [ ] Algorithm evaluation documented
- [ ] Working prototype developed
- [ ] Testing and validation done
- [ ] Documentation comprehensive
- [ ] Presentation prepared

### Documentation Requirements

Maintain throughout project:

- Weekly progress reports
- Design decisions log
- Testing results
- Lessons learned
- Individual contributions

### Fair Contribution

**Track contributions:**

- GitHub commit history
- PR reviews completed
- Issues resolved
- Documentation written
- Meeting participation

**Be transparent:**

- Communicate availability
- Flag if falling behind
- Ask for help when needed
- Credit teammates appropriately

---

## Conflict Resolution

### Technical Disagreements

1. Discuss pros/cons openly
2. Research and present evidence
3. Vote if necessary (majority wins)
4. Document decision rationale
5. Move forward as team

### Workflow Issues

1. Raise in team meeting
2. Discuss as group
3. Update this document
4. Apply consistently

### Serious Issues

Contact course instructor/TA if:

- Team member consistently unresponsive
- Major disagreements can't be resolved
- Someone not contributing fairly
- Project timeline at risk

---

## Team Agreements

All team members agree to:

- [ ] Check team chat daily
- [ ] Respond to assigned code reviews within 24 hours
- [ ] Attend weekly meetings (or notify in advance)
- [ ] Follow branch and commit conventions
- [ ] Write tests for new features
- [ ] Document code and decisions
- [ ] Ask for help when stuck
- [ ] Help teammates when asked
- [ ] Be respectful and constructive
- [ ] Give credit where due

**Signed:**

- [ ] [Team Member 1]
- [ ] [Team Member 2]
- [ ] [Team Member 3]

---

**Last Updated:** 10/3/2025
**Next Review:** [Date]
