# DayFlow HRM — Git Workflow

## Branch Strategy

```
main (protected)
 ├── feature/frontend-ui
 ├── feature/backend-hrms
 ├── feature/ai-intelligence
 └── feature/analytics-devops
```

### Branch Rules

| Rule | Details |
|------|---------|
| `main` is protected | No direct pushes; merge via PR only |
| One feature branch per developer | Work exclusively on your assigned branch |
| Never force push | Especially to `main` or another developer's branch |
| Keep branches updated | Regularly merge/rebase from `main` |
| Small, focused commits | One logical change per commit |

---

## Developer Assignments

### Dev 1 — `feature/frontend-ui`

**Directories:** `frontend/`

**Responsibilities:**
- React components, pages, layouts
- Employee & HR dashboard UI
- API client integration (Axios)
- Routing, auth guards, loading/error states
- Charts (Recharts), tables, modals

**Do NOT modify:** `backend/`, `ai-engine/`, `analytics/`, `database/`

---

### Dev 2 — `feature/backend-hrms`

**Directories:** `backend/`

**Responsibilities:**
- FastAPI routes and middleware
- SQLAlchemy models and migrations
- JWT auth, RBAC, password hashing
- CRUD for employees, attendance, leave, payroll, notifications
- Pydantic schemas matching API contract

**Do NOT modify:** `frontend/`, `ai-engine/` internals (may import)

---

### Dev 3 — `feature/ai-intelligence`

**Directories:** `ai-engine/`

**Responsibilities:**
- Isolation Forest anomaly detection
- Workplace risk signal scoring
- Smart leave recommendation logic
- HR Copilot (Gemini integration)
- Employee AI Assistant (Gemini integration)
- AI-related backend routes in coordination with Dev 2

**Do NOT modify:** `frontend/`, unrelated backend modules

---

### Dev 4 — `feature/analytics-devops`

**Directories:** `analytics/`, `database/`, `deployment/`, `tests/`

**Responsibilities:**
- KPI calculations and trend aggregations
- HR Priority Queue generation
- Team availability analysis
- Database schema and seed data
- Docker/deployment configuration
- Integration and unit tests

**Do NOT modify:** `frontend/`, unrelated backend modules

---

## Shared Files Protocol

These files affect all developers. Changes require team agreement:

| File | Change Protocol |
|------|-----------------|
| `docs/api-contract.md` | Propose change in team chat; all devs review |
| `docs/architecture.md` | Architect approval |
| `.env.example` | Any dev may add vars; document in PR |
| `docker-compose.yml` | Dev 4 owns; others propose via PR |
| Root `README.md` | Any dev; keep accurate |

---

## Daily Workflow

```bash
# 1. Start of day — sync with main
git checkout main
git pull origin main
git checkout feature/your-branch
git merge main

# 2. Work on your module
# ... make changes ...

# 3. Commit
git add frontend/   # only your module
git commit -m "feat: add employee dashboard KPI cards"

# 4. Push your branch
git push origin feature/your-branch

# 5. Create PR when feature is ready
gh pr create --base main --head feature/your-branch
```

---

## Pull Request Guidelines

### PR Title Format

```
[frontend] Add employee attendance weekly view
[backend] Implement leave approval endpoint
[ai] Add isolation forest anomaly detection
[analytics] Create demo seed data script
```

### PR Checklist

- [ ] Changes limited to owned module (+ shared docs if needed)
- [ ] API contract updated if endpoints changed
- [ ] No secrets committed
- [ ] `.env.example` updated if new env vars added
- [ ] Test plan included in PR description
- [ ] No unrelated file changes

### Review Requirements

- At least 1 approval from another developer
- API contract changes need all affected devs to acknowledge
- Cross-module changes need reviewers from both modules

---

## Merge Strategy

Use **squash merge** for feature branches into `main`:

```bash
# Via GitHub UI: "Squash and merge"
# Or via CLI:
gh pr merge --squash
```

This keeps `main` history clean with one commit per feature.

---

## Conflict Resolution

1. **Within your module:** Resolve locally
2. **Shared files (`docs/`):** Discuss with team; architect decides
3. **Cross-module conflicts:** Pair with the other developer

```bash
git checkout feature/your-branch
git merge main
# resolve conflicts
git add .
git commit -m "merge: resolve conflicts with main"
git push origin feature/your-branch
```

---

## Commit Message Convention

```
<type>: <description>

Types:
  feat     — new feature
  fix      — bug fix
  docs     — documentation only
  refactor — code change that neither fixes nor adds
  test     — adding tests
  chore    — build, config, tooling
  style    — formatting, no code change
```

Examples:
```
feat: add POST /attendance/check-in endpoint
fix: prevent duplicate check-in on same day
docs: document leave recommendation API
test: add anomaly detection unit tests
chore: update docker-compose postgres version
```

---

## What NOT To Do

- ❌ Force push to any branch (`git push --force`)
- ❌ Push to another developer's branch
- ❌ Commit `.env` files
- ❌ Modify unrelated modules in your PR
- ❌ Merge to `main` without PR review
- ❌ Change API contract without team notification
- ❌ Expose Gemini API key in frontend code

---

## Initial Branch Setup

Run once after cloning (each developer runs their own):

```bash
git clone <repo-url>
cd dayflow-hrm
git checkout -b feature/frontend-ui      # Dev 1
git checkout -b feature/backend-hrms     # Dev 2
git checkout -b feature/ai-intelligence  # Dev 3
git checkout -b feature/analytics-devops   # Dev 4
git push -u origin feature/your-branch
```

---

## Release Tagging (Post-Hackathon)

```bash
git checkout main
git tag -a v0.1.0 -m "DayFlow HRM hackathon MVP"
git push origin v0.1.0
```
