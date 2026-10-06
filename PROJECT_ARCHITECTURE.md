# ai-incident-investigation — project architecture

[README](README.md) · [Interview questions and answers](INTERVIEW_QA.md)

## Purpose and scope

Send a snapshot: OOMKilled, memory percent, restart count. If the container was OOMKilled and memory was at or above 90 percent, the response names that hypothesis and lists the evidence.

This document describes files and symbols in this checkout. Deployment templates and statements in the original overview are distinguished from a verified running environment.

## Component diagram

```mermaid
flowchart LR
    M0["src/incident/investigate.py"]
    M1["src/incident/main.py"]
    M2["src/incident/ops.py"]
    M1 -->|imports| M0
    M1 -->|imports| M2
```

For Python repositories, arrows show resolved local imports, not network calls or deployment order. Otherwise the diagram is a repository component map; containment arrows do not assert runtime integration.

## Components and responsibilities

| Component | Responsibility |
| --- | --- |
| [`src/incident/main.py`](src/incident/main.py) | HTTP handlers: `POST /investigations` |
| [`src/incident/ops.py`](src/incident/ops.py) | HTTP handlers: `GET /readyz`, `POST /workspaces`, `GET /workspaces`, `POST /workspaces/{workspace_id}/jobs`, `GET /jobs/{job_id}` |
| [`src/incident/investigate.py`](src/incident/investigate.py) | Functions: `investigate` |
| [`requirements.txt`](requirements.txt) | Implementation or supporting configuration |
| [`Dockerfile`](Dockerfile) | Container build/service configuration |
| [`Makefile`](Makefile) | Implementation or supporting configuration |
| [`docker-compose.yml`](docker-compose.yml) | Container build/service configuration |
| [`tests/test_incident.py`](tests/test_incident.py) | Executable checks and regression examples |
| [`tests/test_ops.py`](tests/test_ops.py) | Executable checks and regression examples |
| [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | GitHub Actions job definitions |
| [`README.md`](README.md) | Project explanations or operating notes |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Project explanations or operating notes |

## Existing design and operating guides

These checked-in guides provide the project’s detailed design, operational context, or deployment view:

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Request interface

| Method and path | Handler | Source |
| --- | --- | --- |
| `POST /investigations` | `create` | [`src/incident/main.py`](src/incident/main.py#L19) |
| `GET /readyz` | `readyz` | [`src/incident/ops.py`](src/incident/ops.py#L74) |
| `POST /workspaces` | `create_workspace` | [`src/incident/ops.py`](src/incident/ops.py#L80) |
| `GET /workspaces` | `list_workspaces` | [`src/incident/ops.py`](src/incident/ops.py#L98) |
| `POST /workspaces/{workspace_id}/jobs` | `create_job` | [`src/incident/ops.py`](src/incident/ops.py#L106) |
| `GET /jobs/{job_id}` | `get_job` | [`src/incident/ops.py`](src/incident/ops.py#L130) |
| `POST /jobs/{job_id}/approve` | `approve_job` | [`src/incident/ops.py`](src/incident/ops.py#L140) |
| `GET /audit` | `audit` | [`src/incident/ops.py`](src/incident/ops.py#L160) |
| `GET /metrics` | `metrics` | [`src/incident/ops.py`](src/incident/ops.py#L176) |

The table lists literal route decorators found in the inspected Python modules. Router prefixes and middleware can add behavior; check the linked handler and application setup before calling an endpoint.

## Implementation walkthrough

### `investigate(snapshot)`

Source: [`src/incident/investigate.py`](src/incident/investigate.py#L1).

Calls visible in this function: `evidence.append`, `hypotheses.append`, `snapshot.get`.

```python
def investigate(snapshot):
    evidence = []
    if snapshot.get("oom_killed"):
        evidence.append("container OOMKilled")
    if snapshot.get("memory_percent", 0) >= 90:
        evidence.append("memory at or above 90 percent")
    if snapshot.get("restart_count", 0) >= 3:
        evidence.append("three or more restarts")
    hypotheses = []
    if "container OOMKilled" in evidence and "memory at or above 90 percent" in evidence:
        hypotheses.append({
            "id": "memory-limit",
            "statement": "The container was OOMKilled while memory was already high.",
            "evidence": evidence,
        })
    return {"confirmed_root_cause": False, "hypotheses": hypotheses, "evidence": evidence}
```

## Validation and failure paths

| Explicit exception | Source |
| --- | --- |
| `HTTPException(status_code=404, detail='workspace not found')` | [`src/incident/ops.py`](src/incident/ops.py#L77) |
| `HTTPException(status_code=404, detail='job not found')` | [`src/incident/ops.py`](src/incident/ops.py#L100) |
| `HTTPException(status_code=404, detail='job not found')` | [`src/incident/ops.py`](src/incident/ops.py#L109) |
| `HTTPException(status_code=403, detail='production apply is disabled in this lab')` | [`src/incident/ops.py`](src/incident/ops.py#L113) |

These are explicit exceptions in the inspected source, rather than a claim that every failure is handled. Follow the calling handler to see whether the exception becomes an HTTP response or propagates.

## Data and state

- [`src/incident/ops.py`](src/incident/ops.py) defines module-level containers: `_WORKSPACES`, `_JOBS`, `_AUDIT`, `_METRICS`.

Module-level dictionaries/lists live in a Python process. They can be fixtures or mutable state; inspect writes before treating them as persistent storage. A production extension would need to define persistence and concurrency behavior explicitly.

## Data flow and design decisions

### What is the input-to-output contract of `investigate`

In [`src/incident/investigate.py`](src/incident/investigate.py#L1), `investigate(snapshot)` receives the inputs. The function computes these intermediate values:

- `evidence = []`
- `hypotheses = []`

Its result is defined by:

- `{'confirmed_root_cause': False, 'hypotheses': hypotheses, 'evidence': evidence}`

### Which decision rules or boundary conditions should an interviewer challenge

The implementation in [`src/incident/investigate.py`](src/incident/investigate.py#L1) branches on:

- `snapshot.get('oom_killed')`
- `snapshot.get('memory_percent', 0) >= 90`
- `snapshot.get('restart_count', 0) >= 3`
- `'container OOMKilled' in evidence and 'memory at or above 90 percent' in evidence`

A useful extension is a table-driven test that covers each condition just below, at, and above its boundary where applicable. These expressions are the current rules; changing them changes behavior and should be justified by the project’s acceptance criteria.

### What does the operations plane add, and where is its limit

[`src/incident/ops.py`](src/incident/ops.py) declares `GET /readyz`, `POST /workspaces`, `GET /workspaces`, `POST /workspaces/{workspace_id}/jobs`, `GET /jobs/{job_id}`, `POST /jobs/{job_id}/approve`, `GET /audit`, `GET /metrics`. Inspect the application’s `include_router` call for its URL prefix.

Its state containers are `_WORKSPACES`, `_JOBS`, `_AUDIT`, `_METRICS`. The job-approval handler defines whether a target is accepted or refused; check that branch and the associated tests instead of treating a recorded job as a successful infrastructure apply.

## Setup and verification

The following commands are derived from the checked-in dependency/test contracts. Execute them from the repository root; the block prepares a local environment, not a cloud deployment.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

Python dependencies: [`requirements.txt`](requirements.txt).

Test entry points: [`tests/test_incident.py`](tests/test_incident.py), [`tests/test_ops.py`](tests/test_ops.py).

Automation definitions: [`.github/workflows/ci.yml`](.github/workflows/ci.yml). Read their triggers and job steps to determine what CI actually runs.

## Operating boundaries and design review

Before turning this checkout into a customer deployment, establish the input contract, data ownership, access controls, failure response, evaluation criteria, and rollback owner. Repository fixtures and unit tests demonstrate local behavior; they do not establish throughput, uptime, compliance, or business impact.

A useful architecture review starts with the linked implementation: identify where input enters, where a decision is made, which state can change, and which external dependency can fail. Add a deployment view only for infrastructure that is actually configured and exercised.
