# AI incident investigation platform

<!-- project-guide:start -->
## Project guide

[Project architecture](PROJECT_ARCHITECTURE.md) · [Interview questions and answers](INTERVIEW_QA.md)

Use the architecture document for the component diagram, implementation boundaries, and verification entry points. The interview guide includes source-backed answers and project walkthroughs.

### Implementation map

| Component | Responsibility |
| --- | --- |
| [`src/incident/main.py`](src/incident/main.py) | HTTP handlers: `POST /investigations` |
| [`src/incident/investigate.py`](src/incident/investigate.py) | Functions: `investigate` |
| [`requirements.txt`](requirements.txt) | Implementation or supporting configuration |
| [`tests/test_incident.py`](tests/test_incident.py) | Executable checks and regression examples |
| [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | GitHub Actions job definitions |
| [`README.md`](README.md) | Project explanations or operating notes |

### Local setup and verification

From the repository root (the commands follow the checked-in manifests):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

To serve the FastAPI application locally, install the server separately if it is not already available:

```bash
python -m pip install uvicorn
PYTHONPATH=src python -m uvicorn incident.main:app --reload
```

<!-- project-guide:end -->

Level: Advanced

Skills: Logs, Kubernetes signals, a hypothesis, FastAPI

Send a snapshot: OOMKilled, memory percent, restart count. If the container was OOMKilled and memory was at or above 90 percent, the response names that hypothesis and lists the evidence.

`confirmed_root_cause` stays false. A person confirms a cause. This service does not query a live cluster; you pass the snapshot.

```bash
pip install -r requirements.txt
pytest -q
```

## Ops plane

Workspaces, tenant isolation, job approval, and audit live under `/v1`. Production apply is refused. See `docs/ARCHITECTURE.md`.
