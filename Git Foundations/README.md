# Insurance Manager

A small Flask + vanilla JavaScript web app for managing health insurance
plans, members and claims. It exists as a clean, realistic codebase for
practising everyday Git workflows.

## Features
- Browse plans (Essential, Balanced, Complete) and calculate a monthly quote
- Add and remove members
- File claims; claims above the plan's coverage limit are rejected
- Approve or reject pending claims; the overview updates live

## Project structure
```
insurance-manager/
├── app/
│   ├── __init__.py      # app factory
│   ├── db.py            # SQLite schema + seed plans
│   ├── routes.py        # JSON API + page route
│   ├── services.py      # premium and validation logic (no Flask)
│   ├── templates/index.html
│   └── static/{css,js}/
├── tests/               # pytest suite
├── docs/GIT_PRACTICE.md # guided Git exercises
├── run.py               # dev server entry point
└── requirements.txt
```

## Run it
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run.py                    # http://127.0.0.1:5000
pytest                           # run tests
```

## API
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/plans` | List plans |
| POST | `/api/quote` | `{age, plan_id, smoker}` → premium |
| GET/POST | `/api/members` | List / create members |
| DELETE | `/api/members/<id>` | Remove a member and their claims |
| GET/POST | `/api/claims` | List / file claims |
| PATCH | `/api/claims/<id>` | `{status: approved\|rejected\|pending}` |
| GET | `/api/stats` | Dashboard numbers |

The SQLite database is created in `instance/` on first run and is git-ignored.

## Git practice
See [docs/GIT_PRACTICE.md](docs/GIT_PRACTICE.md).
