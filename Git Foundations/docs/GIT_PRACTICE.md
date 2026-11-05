# Git practice with Insurance Manager

Each exercise uses a real change to this project. Run tests with `pytest`
before every commit.

## 0. Start the repository
```bash
git init -b main
git add .
git status                      # check .gitignore kept .venv and instance/ out
git commit -m "Initial commit: Insurance Manager portal"
git log --oneline
```

## 1. Branch, change, merge
Add a new plan ("Family") in `app/db.py` (note: seeding only runs on an empty
database, so delete `instance/insurance_manager.db` to see it).
```bash
git switch -c feature/family-plan
# edit app/db.py
git diff
git add app/db.py
git commit -m "Add Family plan to seed data"
git switch main
git merge feature/family-plan
git branch -d feature/family-plan
```

## 2. Fix a bug on its own branch
Bug idea: the smoker loading in `app/services.py` should be 40%, not 30%.
Update the code **and** the matching test in `tests/test_services.py`.
```bash
git switch -c fix/smoker-loading
git commit -am "Raise smoker loading to 40%"
```

## 3. Undo things safely
```bash
git restore app/routes.py            # discard unstaged edits
git restore --staged app/routes.py   # unstage
git commit --amend                   # fix the last commit message
git revert <commit>                  # undo a pushed commit with a new commit
git stash / git stash pop            # park work in progress
```

## 4. Create and resolve a merge conflict
1. On `main`, change the Essential plan description in `app/db.py`.
2. On a branch `feature/copy-edit`, change the same line differently.
3. `git merge feature/copy-edit` → resolve the markers → `git add` → `git commit`.

## 5. Work with a remote
```bash
git remote add origin <your-repo-url>
git push -u origin main
git switch -c feature/claim-notes && git push -u origin feature/claim-notes
git fetch && git pull --rebase
```
Then open a pull request on GitHub or GitLab.

## 6. Inspect history
```bash
git log --oneline --graph --all
git blame app/services.py
git show <commit>
git diff main..feature/family-plan
git tag v1.0.0
```

## Feature ideas for more branches
- Search/filter on the Claims table
- A `denied reason` field on rejected claims
- Pagination for members
- Export claims to CSV
Use commit messages like `Add ...`, `Fix ...`, `Update ...` (imperative, under 72 chars).
